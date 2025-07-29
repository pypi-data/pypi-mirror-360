"""
File-based JSON storage backend for rate limiter state.

This module provides a file-based storage implementation using JSON format
with OS-level file locking for cross-process synchronization.
"""

import json
import logging
import os
import threading
import time
from typing import Any, Dict, Optional

import portalocker

from ..types import StorageBackend

logger = logging.getLogger(__name__)


class FileJSONBackend(StorageBackend):
    """
    File-based JSON storage backend with OS-level locking.

    Uses portalocker for cross-platform file locking to ensure
    atomic operations across processes.
    """

    def __init__(self, state_path: str) -> None:
        """
        Initialize the file-based storage backend.

        Args:
            state_path: Path to the JSON state file
        """
        self.state_file = state_path
        self.lock_file = f"{state_path}.lock"

        # Thread-local storage for lock handles
        self._local = threading.local()

        # Default values for rate limit state
        self.default_remaining = -1  # -1 means unknown
        self.default_reset_ts = 0.0

        # Ensure lock file exists
        if not os.path.exists(self.lock_file):
            with open(self.lock_file, "w") as f:
                f.write("")

    def __enter__(self) -> "FileJSONBackend":
        """Acquire lock on entry to context manager."""
        self._acquire_lock()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Release lock on exit from context manager."""
        self._release_lock()

    def _get_lock_handle(self) -> Optional[Any]:
        """Get the thread-local lock handle."""
        return getattr(self._local, "lock_handle", None)

    def _set_lock_handle(self, handle: Optional[Any]) -> None:
        """Set the thread-local lock handle."""
        self._local.lock_handle = handle

    def _acquire_lock(self) -> None:
        """Acquire an exclusive lock on the lock file."""
        if self._get_lock_handle() is not None:
            logger.warning("Attempting to acquire lock when already held by this thread")
            return

        max_attempts = 600  # 60 seconds total timeout
        attempt = 0

        while attempt < max_attempts:
            try:
                # Open lock file and acquire exclusive lock
                handle = open(self.lock_file, "r+")
                portalocker.lock(handle, portalocker.LOCK_EX | portalocker.LOCK_NB)
                self._set_lock_handle(handle)
                logger.debug(f"Thread {threading.current_thread().name} acquired lock on {self.lock_file}")
                return
            except portalocker.LockException:
                # Lock is held by another process/thread
                try:
                    handle.close()
                except Exception:
                    pass
                if attempt == 0:
                    logger.debug(f"Lock busy, waiting... (thread: {threading.current_thread().name})")
                attempt += 1
                time.sleep(0.1)  # Wait 100ms before retry
            except Exception as e:
                logger.error(f"Failed to acquire lock: {e}")
                if "handle" in locals():
                    try:
                        handle.close()
                    except Exception:
                        pass
                raise

        raise TimeoutError(f"Could not acquire lock after {max_attempts * 0.1} seconds")

    def _release_lock(self) -> None:
        """Release the lock on the lock file."""
        handle = self._get_lock_handle()
        if handle is None:
            logger.warning("Attempting to release lock when not held by this thread")
            return

        try:
            portalocker.unlock(handle)
            handle.close()
            self._set_lock_handle(None)
            logger.debug(f"Thread {threading.current_thread().name} released lock on {self.lock_file}")
        except Exception as e:
            logger.error(f"Failed to release lock: {e}")
            # Still clear the handle
            self._set_lock_handle(None)

    def read(self) -> Dict[str, Any]:
        """
        Read the current state from the state file.

        Must be called within the context manager.

        Returns:
            Current state dictionary
        """
        if self._get_lock_handle() is None:
            raise RuntimeError("read() called without acquiring lock")

        if not os.path.exists(self.state_file):
            # Return default state
            return {"remaining": self.default_remaining, "reset_ts": self.default_reset_ts, "last_update_ts": time.monotonic()}

        try:
            with open(self.state_file, "r") as f:
                content = f.read()
                if not content.strip():
                    # Empty file, return defaults
                    return {"remaining": self.default_remaining, "reset_ts": self.default_reset_ts, "last_update_ts": time.monotonic()}
                data: Dict[str, Any] = json.loads(content)
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read state file, using defaults: {e}")
            return {"remaining": self.default_remaining, "reset_ts": self.default_reset_ts, "last_update_ts": time.monotonic()}

    def write(self, state: Dict[str, Any]) -> None:
        """
        Write state to the state file.

        Must be called within the context manager.
        Uses atomic write with os.replace().

        Args:
            state: State dictionary to write
        """
        if self._get_lock_handle() is None:
            raise RuntimeError("write() called without acquiring lock")

        # Add timestamp
        state["last_update_ts"] = time.monotonic()

        # Write to temporary file first
        temp_file = f"{self.state_file}.tmp"
        try:
            with open(temp_file, "w") as f:
                json.dump(state, f, indent=2)

            # Atomic replace
            os.replace(temp_file, self.state_file)
            logger.debug(f"Updated rate limit state: remaining={state.get('remaining')}, reset_ts={state.get('reset_ts')}")
        except Exception as e:
            logger.error(f"Failed to write state: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            raise
