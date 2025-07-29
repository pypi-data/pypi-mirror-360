"""
Rate limiting functionality for crudclient.

.. warning::
    **EXPERIMENTAL FEATURE**: This rate limiting module is experimental and subject to change.

    The rate limiting functionality is designed to prevent HTTP 429 errors by coordinating
    requests across multiple processes. However, it should be considered experimental:

    - API compatibility may change in future releases
    - Only Tripletex API headers are currently supported
    - File-based state storage may have edge cases in high-concurrency scenarios
    - Performance characteristics are still being evaluated

    Use with caution in production environments and monitor for any issues.

Provides cross-process rate limiting to prevent API rate limit errors.
"""

import warnings
from typing import Optional

from crudclient.config import ClientConfig

from .facade import RateLimiter


def get_rate_limiter(config: ClientConfig) -> Optional[RateLimiter]:
    """
    Get a rate limiter instance based on the configuration.

    Args:
        config: Configuration object that may have rate limiting enabled

    Returns:
        RateLimiter instance if enabled, None otherwise
    """
    if not hasattr(config, "_rate_limiter_enabled") or not config._rate_limiter_enabled:
        return None

    # Emit experimental feature warning
    warnings.warn(
        "Rate limiting is an EXPERIMENTAL feature that may change in future releases. "
        "Use with caution in production. See crudclient.ratelimit documentation for details.",
        FutureWarning,
        stacklevel=2,
    )

    # Get configuration parameters
    state_path = getattr(config, "_rate_limiter_state_path", None)
    buffer = getattr(config, "_rate_limiter_buffer", 10)
    track_delays = getattr(config, "_rate_limiter_track_delays", False)
    buffer_time = getattr(config, "_rate_limiter_buffer_time", 1.0)

    return RateLimiter(api_host=config.base_url, state_path=state_path, buffer=buffer, track_delays=track_delays, buffer_time=buffer_time)


__all__ = ["get_rate_limiter", "RateLimiter"]
