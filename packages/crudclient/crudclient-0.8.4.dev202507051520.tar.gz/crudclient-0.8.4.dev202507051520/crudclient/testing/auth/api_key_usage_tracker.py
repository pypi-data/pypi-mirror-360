"""
API Key usage tracking utilities for testing.

This module provides a class for tracking API key usage across endpoints.
"""

from typing import Dict, Optional


class ApiKeyUsageTracker:
    """
    API Key usage tracker for monitoring API key usage across endpoints.

    This class provides methods for tracking API key usage and retrieving
    usage statistics.
    """

    usage_tracking_enabled: bool
    usage_by_endpoint: Dict[str, int]
    usage_by_key: Dict[str, int]

    def __init__(self) -> None:
        """
        Initialize an API Key usage tracker.
        """
        self.usage_tracking_enabled = False
        self.usage_by_endpoint: Dict[str, int] = {}
        self.usage_by_key: Dict[str, int] = {}

    def enable_usage_tracking(self) -> None:
        """
        Enable usage tracking for API keys.
        """
        self.usage_tracking_enabled = True

    def initialize_key(self, api_key: str) -> None:
        """
        Initialize usage tracking for a specific API key.

        Args:
            api_key: The API key to initialize
        """
        if api_key not in self.usage_by_key:
            self.usage_by_key[api_key] = 0

    def track_request(self, api_key: str, endpoint: Optional[str] = None) -> None:
        """
        Track a request for usage tracking purposes.

        Args:
            api_key: The API key used for the request
            endpoint: The endpoint being accessed
        """
        if not self.usage_tracking_enabled:
            return

        if api_key not in self.usage_by_key:
            self.usage_by_key[api_key] = 0
        self.usage_by_key[api_key] += 1

        if endpoint:
            if endpoint not in self.usage_by_endpoint:
                self.usage_by_endpoint[endpoint] = 0
            self.usage_by_endpoint[endpoint] += 1

    def get_usage_stats(self) -> Dict:
        """
        Get usage statistics for API keys and endpoints.

        Returns:
            Dictionary with usage statistics
        """
        return {"by_key": self.usage_by_key, "by_endpoint": self.usage_by_endpoint, "total_requests": sum(self.usage_by_key.values())}
