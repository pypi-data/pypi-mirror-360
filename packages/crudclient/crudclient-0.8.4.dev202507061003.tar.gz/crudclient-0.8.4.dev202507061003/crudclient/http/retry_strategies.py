import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid potential circular imports if strategies need complex types
    pass


class RetryStrategy(ABC):
    """Abstract base class for retry delay strategies."""

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry attempt.

        Args:
            attempt: The current retry attempt number (starting from 1).

        Returns:
            The calculated delay in seconds.

        Raises:
            TypeError: If attempt is not an integer.
            ValueError: If attempt is less than 1.
        """


class FixedRetryStrategy(RetryStrategy):
    """A retry strategy with a fixed delay between attempts."""

    delay: float

    def __init__(self, delay: float = 1.0) -> None:
        """Initializes the FixedRetryStrategy.

        Args:
            delay: The fixed delay in seconds between retries. Must be non-negative.

        Raises:
            ValueError: If delay is negative.
        """
        if not isinstance(delay, (int, float)) or delay < 0:
            raise ValueError("delay must be a non-negative number")
        self.delay = delay

    def get_delay(self, attempt: int) -> float:
        """Returns the fixed delay.

        Args:
            attempt: The current retry attempt number (starting from 1).

        Returns:
            The fixed delay in seconds.

        Raises:
            TypeError: If attempt is not an integer.
            ValueError: If attempt is less than 1.
        """
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")
        if attempt < 1:
            raise ValueError(f"attempt must be a positive integer, got {attempt}")
        return self.delay


class ExponentialBackoffStrategy(RetryStrategy):
    """A retry strategy with exponentially increasing delay, optionally with jitter."""

    base_delay: float
    max_delay: float
    factor: float
    jitter: bool

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        factor: float = 2.0,
        jitter: bool = True,
    ) -> None:
        """Initializes the ExponentialBackoffStrategy.

        Args:
            base_delay: The initial delay in seconds. Must be positive.
            max_delay: The maximum delay in seconds. Must be non-negative and >= base_delay.
            factor: The multiplier for the delay. Must be greater than 1.
            jitter: Whether to add random jitter to the delay.

        Raises:
            ValueError: If base_delay, max_delay, or factor have invalid values.
            TypeError: If jitter is not a boolean.
        """
        if not isinstance(base_delay, (int, float)) or base_delay <= 0:
            raise ValueError("base_delay must be a positive number")
        if not isinstance(max_delay, (int, float)) or max_delay < base_delay:
            raise ValueError("max_delay must be non-negative and >= base_delay")
        if not isinstance(factor, (int, float)) or factor <= 1:
            raise ValueError("factor must be a number greater than 1")
        if not isinstance(jitter, bool):
            raise TypeError("jitter must be a boolean")

        self.base_delay = base_delay
        self.max_delay = max_delay
        self.factor = factor
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculates delay using exponential backoff with optional jitter.

        The delay is calculated as `min(base_delay * (factor ** (attempt - 1)), max_delay)`.
        If jitter is enabled, a random variation is added.

        Args:
            attempt: The current retry attempt number (starting from 1).

        Returns:
            The calculated delay in seconds, capped at max_delay.

        Raises:
            TypeError: If attempt is not an integer.
            ValueError: If attempt is less than 1.
        """
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")
        if attempt < 1:
            raise ValueError(f"attempt must be a positive integer, got {attempt}")

        # Calculate exponential backoff
        delay = min(self.base_delay * (self.factor ** (attempt - 1)), self.max_delay)

        # Add jitter if enabled (up to 25% variation around the delay)
        if self.jitter:
            delay = delay * (0.75 + 0.5 * random.random())

        # Ensure delay doesn't exceed max_delay after jitter
        return min(delay, self.max_delay)
