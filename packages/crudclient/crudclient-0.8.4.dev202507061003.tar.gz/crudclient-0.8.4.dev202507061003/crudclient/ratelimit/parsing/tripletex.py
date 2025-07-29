"""
Tripletex-specific header parser for rate limit information.

Parses headers in the format:
- X-Rate-Limit-Remaining: number of requests remaining
- X-Rate-Limit-Reset: seconds until rate limit window resets
"""

import logging
from typing import Mapping, Optional, Tuple

logger = logging.getLogger(__name__)


class TripletexParser:
    """
    Parser for Tripletex rate limit headers.

    Extracts rate limit information from response headers using
    Tripletex's specific header format.
    """

    def parse(self, headers: Mapping[str, str]) -> Optional[Tuple[int, float]]:
        """
        Parse rate limit information from headers.

        Args:
            headers: Response headers dictionary (case-insensitive preferred)

        Returns:
            Tuple of (remaining_calls, seconds_until_reset) or None if not found
        """
        # Try to find headers with case-insensitive lookup
        remaining_str = None
        reset_str = None

        # Convert to lowercase for comparison
        headers_lower = {k.lower(): v for k, v in headers.items()}

        # Look for rate limit headers
        remaining_str = headers_lower.get("x-rate-limit-remaining")
        reset_str = headers_lower.get("x-rate-limit-reset")

        if remaining_str is None or reset_str is None:
            logger.debug(f"Rate limit headers not found. Got: remaining={remaining_str}, reset={reset_str}")
            return None

        try:
            # Parse values
            remaining = int(remaining_str)
            seconds_until_reset = float(reset_str)

            logger.debug(f"Parsed rate limit headers: remaining={remaining}, " f"reset_in={seconds_until_reset}s")

            return (remaining, seconds_until_reset)

        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse rate limit headers: remaining='{remaining_str}', " f"reset='{reset_str}'. Error: {e}")
            return None
