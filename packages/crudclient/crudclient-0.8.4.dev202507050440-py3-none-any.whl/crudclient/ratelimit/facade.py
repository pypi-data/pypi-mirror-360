"""
Rate limiter facade for synchronous operations.

This module provides the main RateLimiter class that coordinates rate limiting
across multiple processes using file-based storage.
"""

import hashlib
import logging
import os
import time
from typing import List, Mapping, Optional

from .parsing.tripletex import TripletexParser
from .storage.file_json import FileJSONBackend

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Synchronous rate limiter with cross-process coordination.

    .. warning::
        **EXPERIMENTAL**: This rate limiter is experimental and subject to change.
        It currently only supports Tripletex API rate limit headers.

    This class provides the main interface for rate limiting, checking if
    requests can proceed and updating state based on API responses.

    Known limitations:
    - Only parses Tripletex rate limit headers (X-Rate-Limit-Remaining, X-Rate-Limit-Reset)
    - File-based locking may have edge cases under extreme concurrency
    - State file format may change between versions without migration
    """

    def __init__(
        self,
        api_host: str,
        state_path: Optional[str] = None,
        buffer: int = 10,
        track_delays: bool = False,
        buffer_time: float = 1.0,
    ) -> None:
        """
        Initialize the rate limiter.

        Args:
            api_host: The API hostname/URL to rate limit
            state_path: Directory for state files. If None, uses system cache.
            buffer: Buffer size for threshold calculation
            track_delays: Whether to track rate limiting delays for testing
            buffer_time: Time buffer in seconds to add when waiting (default: 1.0)
        """
        self.api_host = api_host
        self.buffer = buffer
        self.track_delays = track_delays
        self.buffer_time = buffer_time
        self._delay_history: List[float] = []

        # Create state file path
        if state_path is None:
            import appdirs

            cache_dir = appdirs.user_cache_dir("crudclient", "crudclient")
            os.makedirs(cache_dir, exist_ok=True)
            # Generate unique filename for this API
            host_hash = hashlib.md5(api_host.encode()).hexdigest()[:8]
            state_file = os.path.join(cache_dir, f"rl_{host_hash}.json")
        elif os.path.splitext(state_path)[1] == ".json":
            # If a specific JSON file path is provided, use it directly
            state_file = state_path
            # Ensure parent directory exists
            parent_dir = os.path.dirname(state_file)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
        else:
            # If a directory path is provided, generate filename within it
            os.makedirs(state_path, exist_ok=True)
            host_hash = hashlib.md5(api_host.encode()).hexdigest()[:8]
            state_file = os.path.join(state_path, f"rl_{host_hash}.json")

        # Initialize backend and parser
        self.backend = FileJSONBackend(state_file)
        self.parser = TripletexParser()

        logger.warning(
            f"EXPERIMENTAL: RateLimiter initialized for {api_host} with "
            f"state={state_file}, buffer={buffer}. This feature is experimental "
            f"and may change in future releases."
        )

    def check_and_wait(self, calls: int = 1) -> None:
        """
        Check rate limit and wait if necessary.

        This method will block if the rate limit would be exceeded,
        sleeping until the rate limit window resets.

        Args:
            calls: Number of calls that will be made (default: 1)

        Raises:
            Exception: If there's an error accessing the rate limiter state
        """
        # Calculate dynamic threshold
        threshold = self._get_dynamic_threshold()
        logger.debug(f"check_and_wait called with calls={calls}, threshold={threshold}")

        while True:
            with self.backend:
                state = self.backend.read()
                remaining = state["remaining"]
                reset_ts = state["reset_ts"]

                now = time.time()

                logger.debug(
                    f"Current state: remaining={remaining}, reset_ts={reset_ts:.1f}, " f"now={now:.1f}, seconds_until_reset={(reset_ts - now):.1f}"
                )

                # Check if we should reset (window expired)
                if reset_ts > 0 and now >= reset_ts and remaining != -1:
                    logger.info("Rate limit window expired, resetting to unknown state")
                    self.backend.write({"remaining": -1, "reset_ts": 0})
                    continue

                # Check if we need to wait
                if remaining != -1 and remaining <= threshold:
                    wait_time = reset_ts - now
                    if wait_time <= 0:
                        # Window expired during check
                        logger.info("Rate limit window expired during check, resetting")
                        self.backend.write({"remaining": -1, "reset_ts": 0})
                        continue

                    # Add time buffer
                    wait_time += self.buffer_time
                    logger.warning(
                        f"Rate limit threshold reached: remaining={remaining} <= threshold={threshold}. "
                        f"Waiting {wait_time:.1f}s until reset (includes {self.buffer_time}s buffer) to prevent 429 errors."
                    )

                    # Track delay if enabled
                    if self.track_delays:
                        self._delay_history.append(wait_time)
                        logger.debug(f"Tracked delay of {wait_time:.1f}s (total delays: {len(self._delay_history)})")

                    # Sleep without holding lock
                    time.sleep(wait_time)
                    logger.info(f"Finished waiting {wait_time:.1f}s, retrying request")
                    continue

                # We can proceed
                if remaining != -1:
                    # Decrement counter
                    new_remaining = remaining - calls
                    self.backend.write({"remaining": new_remaining, "reset_ts": reset_ts})
                    logger.debug(f"Request allowed. Remaining: {remaining} -> {new_remaining} " f"(consumed {calls}, threshold={threshold})")
                else:
                    logger.debug("Rate limit state unknown (remaining=-1), proceeding without decrement")

                # Exit the loop
                break

    def update_from_headers(self, headers: Mapping[str, str]) -> None:
        """
        Update rate limit state from API response headers.

        Args:
            headers: Response headers that may contain rate limit info
        """
        try:
            result = self.parser.parse(headers)
            if result is None:
                logger.debug("No rate limit headers found in response")
                return

            remaining, seconds_until_reset = result
            reset_ts = time.time() + seconds_until_reset

            logger.debug(f"Parsed rate limit headers: remaining={remaining}, " f"reset_in={seconds_until_reset}s")

            with self.backend:
                # Read current state to check if we should update
                state = self.backend.read()
                current_remaining = state["remaining"]
                current_reset_ts = state["reset_ts"]

                # Update if:
                # 1. New reset time is different (window changed)
                # 2. Same window but lower remaining count
                # 3. Current state is unknown
                should_update = (
                    current_remaining == -1
                    or abs(reset_ts - current_reset_ts) > 1  # Allow 1s tolerance
                    or (abs(reset_ts - current_reset_ts) <= 1 and remaining < current_remaining)
                )

                if should_update:
                    self.backend.write({"remaining": remaining, "reset_ts": reset_ts})
                    logger.info(f"Updated rate limit state: remaining {current_remaining} -> {remaining}, " f"reset_in={seconds_until_reset:.1f}s")
                else:
                    logger.debug(
                        f"Skipping rate limit update (no improvement): "
                        f"current_remaining={current_remaining}, new_remaining={remaining}, "
                        f"window_match={abs(reset_ts - current_reset_ts) <= 1}"
                    )

        except Exception as e:
            logger.error(f"Failed to process rate limit headers: {e}", exc_info=True)

    def _get_dynamic_threshold(self) -> int:
        """
        Calculate the dynamic threshold based on worker count and buffer.

        Returns:
            Threshold value for when to start waiting
        """
        # Detect worker count with priority order
        workers = int(os.getenv("CRUDCLIENT_WORKERS", 0))

        if not workers:
            workers = int(os.getenv("CELERY_CONCURRENCY", 0))

        if not workers:
            workers = int(os.getenv("PYTEST_XDIST_WORKER_COUNT", 0))

        if not workers:
            workers = os.cpu_count() or 1

        threshold = workers + self.buffer
        logger.debug(f"Dynamic threshold: workers={workers}, buffer={self.buffer}, total={threshold}")
        return threshold

    def get_delay_history(self) -> List[float]:
        """
        Get the history of rate limiting delays.

        Returns:
            List of delay durations in seconds
        """
        return self._delay_history.copy()

    def clear_delay_history(self) -> None:
        """Clear the delay history."""
        self._delay_history.clear()
