"""
Type definitions for the rate limiter module.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class StorageBackend(ABC):
    """
    Abstract base class for rate limiter storage backends.

    Implementations must provide thread-safe and process-safe
    storage operations for rate limit state.
    """

    @abstractmethod
    def __enter__(self) -> "StorageBackend":
        """Enter context manager and acquire any necessary locks."""

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and release any locks."""

    @abstractmethod
    def read(self) -> Dict[str, Any]:
        """Read the current state from storage."""

    @abstractmethod
    def write(self, state: Dict[str, Any]) -> None:
        """Write state to storage."""
