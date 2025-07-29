"""Utilities for simulating API rate limiting in tests."""

import time
from typing import Any, Dict, List, Optional, Tuple


def get_current_time() -> float:
    """Return the current time in seconds."""

    return time.time()


class RateLimitHelper:
    """Helper for simulating rate limiting behavior in tests."""

    limit: int
    window_seconds: int
    remaining_header: str
    limit_header: str
    reset_header: str
    retry_after_header: str
    burst_limit: Optional[int]
    burst_window_seconds: int
    tiered_limits: Optional[List[Dict[str, Any]]]
    tier_header: Optional[str]
    requests: List[float]
    burst_requests: List[float]
    tiered_requests: Dict[str, List[float]]
    _last_reset: float
    _current_tier: Optional[str]

    def __init__(
        self,
        limit: int = 60,
        window_seconds: int = 60,
        remaining_header: str = "X-RateLimit-Remaining",
        limit_header: str = "X-RateLimit-Limit",
        reset_header: str = "X-RateLimit-Reset",
        retry_after_header: str = "Retry-After",
        burst_limit: Optional[int] = None,
        burst_window_seconds: Optional[int] = None,
        tiered_limits: Optional[List[Dict[str, Any]]] = None,
        tier_header: Optional[str] = None,
    ) -> None:
        """Initialize rate limit helper with configuration options.

        This constructor sets up the rate limit helper with configuration for
        standard rate limits, burst limits, and tiered limits. It supports
        customization of header names to match different API implementations.

        Args:
            limit: Maximum number of requests allowed in the standard window
            window_seconds: Time window in seconds for the standard rate limit
            remaining_header: Header name for remaining requests count
            limit_header: Header name for the rate limit value
            reset_header: Header name for the rate limit reset timestamp
            retry_after_header: Header name for retry after seconds value
            burst_limit: Optional burst limit for short time periods
                (useful for simulating APIs that have both long-term and
                short-term rate limits)
            burst_window_seconds: Window for burst limit in seconds
                (defaults to window_seconds / 10 if not provided)
            tiered_limits: Optional list of tier configurations with 'name',
                'limit', and 'window' keys for simulating different rate limits
                for different API access tiers
            tier_header: Header name for tier information in responses
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.remaining_header = remaining_header
        self.limit_header = limit_header
        self.reset_header = reset_header
        self.retry_after_header = retry_after_header
        self.burst_limit = burst_limit
        self.burst_window_seconds = burst_window_seconds or (window_seconds // 10)
        self.tiered_limits = tiered_limits
        self.tier_header = tier_header

        # Request tracking
        self.requests: List[float] = []
        self.burst_requests: List[float] = []
        self.tiered_requests: Dict[str, List[float]] = {}
        if tiered_limits:
            for tier in tiered_limits:
                tier_name = str(tier["name"])
                self.tiered_requests[tier_name] = []

        self._last_reset = get_current_time()
        self._current_tier: Optional[str] = None

    def check_rate_limit(self, tier: Optional[str] = None) -> Tuple[bool, Dict[str, str]]:
        """Check if the rate limit has been exceeded and generate appropriate headers.

        This method determines whether a request should be allowed based on the
        configured rate limits and the history of previous requests. It also
        generates appropriate rate limit headers that would be returned by a
        rate-limited API, including information about remaining requests,
        limit values, and reset times.

        Args:
            tier: Optional tier name to check against tiered limits
                (if tiered limits are configured)

        Returns:
            Tuple containing:
                - Boolean indicating whether the request is allowed (True) or
                  should be rate limited (False)
                - Dictionary of rate limit headers that would be included in
                  the API response
        """
        now = get_current_time()

        # Set current tier if provided
        if tier and self.tiered_limits:
            self._current_tier = tier

        # Clean up expired requests
        self._clean_expired_requests(now)

        # Check all limits
        standard_limited = self._check_standard_limit()
        burst_limited = self._check_burst_limit(now)
        tier_limited, tier_info = self._check_tier_limit(now)

        # Determine if request is allowed
        is_allowed = not (standard_limited or burst_limited or tier_limited)

        # Record this request if allowed
        if is_allowed:
            self._record_request(now, tier_info.get("name"))

        # Calculate reset times
        reset_times = self._calculate_reset_times(now, burst_limited, tier_limited, tier_info)

        # Generate response headers
        headers = self._generate_headers(now, is_allowed, reset_times, tier_info)

        return is_allowed, headers

    def _clean_expired_requests(self, now: float) -> None:
        # Standard window
        self.requests = [t for t in self.requests if now - t < self.window_seconds]

        # Burst window
        if self.burst_limit is not None:
            self.burst_requests = [t for t in self.burst_requests if now - t < self.burst_window_seconds]

    def _check_standard_limit(self) -> bool:
        return len(self.requests) >= self.limit

    def _check_burst_limit(self, now: float) -> bool:
        if self.burst_limit is None:
            return False
        return len(self.burst_requests) >= self.burst_limit

    def _check_tier_limit(self, now: float) -> Tuple[bool, Dict[str, Any]]:
        tier_info: Dict[str, Any] = {"name": None, "limit": self.limit, "window": self.window_seconds, "requests": []}

        # If no tier configuration or current tier, use standard limits
        if not (self.tiered_limits and self._current_tier):
            return False, tier_info

        # Find matching tier configuration
        for tier_config in self.tiered_limits:
            if str(tier_config["name"]) == self._current_tier:
                tier_name = str(tier_config["name"])
                tier_info["name"] = tier_name
                tier_info["limit"] = int(tier_config["limit"])
                tier_info["window"] = int(tier_config.get("window", self.window_seconds))

                # Initialize tier requests list if not exists
                if tier_name not in self.tiered_requests:
                    self.tiered_requests[tier_name] = []

                # Remove old requests
                self.tiered_requests[tier_name] = [t for t in self.tiered_requests[tier_name] if now - t < tier_info["window"]]

                tier_info["requests"] = self.tiered_requests[tier_name]

                # Check if tier limit exceeded
                return len(self.tiered_requests[tier_name]) >= tier_info["limit"], tier_info

        # No matching tier found
        return False, tier_info

    def _record_request(self, now: float, tier_name: Optional[str]) -> None:
        # Standard tracking
        self.requests.append(now)

        # Burst tracking
        if self.burst_limit is not None:
            self.burst_requests.append(now)

        # Tier tracking
        if tier_name and tier_name in self.tiered_requests:
            self.tiered_requests[tier_name].append(now)

    def _calculate_reset_times(self, now: float, burst_limited: bool, tier_limited: bool, tier_info: Dict[str, Any]) -> Dict[str, Optional[int]]:
        result: Dict[str, Optional[int]] = {"standard": None, "burst": None, "tier": None, "effective": None}

        # Standard reset time
        if self.requests:
            oldest_request = min(self.requests)
            result["standard"] = int(oldest_request + self.window_seconds)
        else:
            result["standard"] = int(now + self.window_seconds)

        # Burst reset time
        if burst_limited and self.burst_requests:
            oldest_burst = min(self.burst_requests)
            result["burst"] = int(oldest_burst + self.burst_window_seconds)

        # Tier reset time
        tier_name = tier_info.get("name")
        tier_window = tier_info.get("window", self.window_seconds)  # Default to standard window
        if tier_limited and tier_name and tier_name in self.tiered_requests and self.tiered_requests[tier_name]:
            oldest_tier = min(self.tiered_requests[tier_name])
            result["tier"] = int(oldest_tier + tier_window)

        # Calculate effective (earliest) reset time
        effective_time = result["standard"]

        # Safe comparison with burst reset time
        if result["burst"] is not None and effective_time is not None and result["burst"] < effective_time:
            effective_time = result["burst"]
        elif result["burst"] is not None and effective_time is None:
            effective_time = result["burst"]

        # Safe comparison with tier reset time
        if result["tier"] is not None and effective_time is not None and result["tier"] < effective_time:
            effective_time = result["tier"]
        elif result["tier"] is not None and effective_time is None:
            effective_time = result["tier"]

        result["effective"] = effective_time
        return result

    def _generate_headers(self, now: float, is_allowed: bool, reset_times: Dict[str, Optional[int]], tier_info: Dict[str, Any]) -> Dict[str, str]:
        # Ensure we have a valid reset time (should never be None in practice)
        effective_reset = reset_times["effective"] or int(now + self.window_seconds)

        headers = {
            self.remaining_header: str(max(0, self.limit - len(self.requests))),
            self.limit_header: str(self.limit),
            self.reset_header: str(effective_reset),
        }

        # Add retry-after header if rate limited
        if not is_allowed:
            retry_after = effective_reset - int(now)
            headers[self.retry_after_header] = str(max(1, retry_after))

        # Add tier information
        tier_name = tier_info.get("name")
        if self.tier_header and tier_name:
            headers[self.tier_header] = tier_name

        # Add burst limit information
        if self.burst_limit is not None:
            headers["X-Burst-Limit"] = str(self.burst_limit)
            headers["X-Burst-Remaining"] = str(max(0, self.burst_limit - len(self.burst_requests)))
            if reset_times["burst"] is not None:
                headers["X-Burst-Reset"] = str(reset_times["burst"])

        # Add tier limit information
        if tier_name:
            tier_limit = tier_info.get("limit", self.limit)  # Default to standard limit
            headers["X-Tier-Limit"] = str(tier_limit)

            remaining = 0
            if tier_name in self.tiered_requests:
                remaining = max(0, tier_limit - len(self.tiered_requests[tier_name]))
            headers["X-Tier-Remaining"] = str(remaining)

            if reset_times["tier"] is not None:
                headers["X-Tier-Reset"] = str(reset_times["tier"])

        return headers

    def set_tier(self, tier: str) -> None:
        """Set the current tier for rate limiting.

        This method sets the current tier to use for rate limiting checks,
        allowing tests to simulate different API access tiers with different
        rate limits.

        Args:
            tier: Tier name to use for rate limiting
                (must match a tier name in the configured tiered limits)

        Raises:
            ValueError: If the specified tier is not found in the configured
                tiered limits
        """
        if self.tiered_limits:
            for tier_config in self.tiered_limits:
                if str(tier_config["name"]) == tier:
                    self._current_tier = tier
                    return
        raise ValueError(f"Tier '{tier}' not found in configured tiered limits")
