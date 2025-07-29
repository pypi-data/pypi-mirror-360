"""
API Key authentication mock for testing.

This module provides a mock for API Key Authentication strategy with support
for key validation, rate limiting, and usage tracking.
"""

import re
from datetime import datetime, timedelta
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from apiconfig.testing.auth_verification import AuthHeaderVerification

from crudclient.auth import ApiKeyAuth, AuthStrategy
from crudclient.exceptions import AuthenticationError

from .api_key_rate_limiter import ApiKeyRateLimiter
from .api_key_usage_tracker import ApiKeyUsageTracker
from .api_key_validator import ApiKeyValidator
from .base import AuthMockBase

if TYPE_CHECKING:
    from ..response_builder.response import MockResponse

T = TypeVar("T", bound="ApiKeyAuthMock")


class ApiKeyAuthMock(AuthMockBase):
    """
    Mock for API Key Authentication strategy with enhanced validation and rate limiting.

    This class provides a configurable mock implementation of the API Key Authentication
    strategy, with support for key validation, rate limiting, and usage tracking.

    Attributes
    ----------
    api_key : str
        The API key used by this mock.
    header_name : Optional[str]
        The name of the header used for API key authentication.
    param_name : Optional[str]
        The name of the query parameter used for API key authentication.
    validator : ApiKeyValidator
        Validator component for API keys.
    rate_limiter : ApiKeyRateLimiter
        Rate limiter component for API keys.
    usage_tracker : ApiKeyUsageTracker
        Usage tracker component for API keys.
    auth_strategy : ApiKeyAuth
        The underlying ApiKeyAuth strategy instance.
    """

    api_key: str
    header_name: Optional[str]
    param_name: Optional[str]
    validator: ApiKeyValidator
    rate_limiter: ApiKeyRateLimiter
    usage_tracker: ApiKeyUsageTracker
    auth_strategy: ApiKeyAuth

    def __init__(self, api_key: str = "valid_api_key", header_name: Optional[str] = "X-API-Key", param_name: Optional[str] = None) -> None:
        """
        Initialize an API Key Authentication mock.

        Parameters
        ----------
        api_key : str, optional
            The default API key. Defaults to "valid_api_key".
        header_name : Optional[str], optional
            Name of the header for API key (None if using param). Defaults to "X-API-Key".
        param_name : Optional[str], optional
            Name of the query parameter for API key (None if using header). Defaults to None.

        Raises
        ------
        ValueError
            If neither header_name nor param_name is provided.
        """
        super().__init__()
        self.api_key = api_key
        self.header_name = header_name
        self.param_name = param_name

        self.validator = ApiKeyValidator()
        self.rate_limiter = ApiKeyRateLimiter()
        self.usage_tracker = ApiKeyUsageTracker()

        self.validator.add_valid_key(api_key)
        self.validator.set_key_metadata(api_key=api_key, owner="default_user", permissions=["read", "write"], tier="standard")
        self.rate_limiter.initialize_key(api_key)
        self.usage_tracker.initialize_key(api_key)

        if header_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, header_name=header_name)
        elif param_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, param_name=param_name)
        else:
            raise ValueError("Either header_name or param_name must be provided")

    def with_api_key(self, api_key: str) -> "ApiKeyAuthMock":
        """
        Set the API key for the API Key Auth mock.

        Parameters
        ----------
        api_key : str
            The API key to use.

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        self.api_key = api_key
        self.validator.add_valid_key(api_key)
        self.validator.set_key_metadata(api_key=api_key, owner="default_user", permissions=["read", "write"], tier="standard")
        self.rate_limiter.initialize_key(api_key)
        self.usage_tracker.initialize_key(api_key)

        if self.header_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, header_name=self.header_name)
        elif self.param_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, param_name=self.param_name)

        return self

    def with_additional_valid_key(self, api_key: str) -> "ApiKeyAuthMock":
        """
        Add an additional valid API key.

        Parameters
        ----------
        api_key : str
            An additional valid API key.

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        self.validator.add_valid_key(api_key)
        self.validator.set_key_metadata(api_key=api_key, owner="default_user", permissions=["read", "write"], tier="standard")
        self.rate_limiter.initialize_key(api_key)
        self.usage_tracker.initialize_key(api_key)
        return self

    def with_key_metadata(
        self,
        api_key: Optional[str] = None,
        owner: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        tier: Optional[str] = None,
        expires_in_seconds: Optional[int] = None,
    ) -> "ApiKeyAuthMock":
        """
        Set metadata for a specific API key or the current key.

        Parameters
        ----------
        api_key : Optional[str], optional
            The API key to set metadata for (defaults to the current key).
        owner : Optional[str], optional
            Owner of the API key.
        permissions : Optional[List[str]], optional
            List of permissions associated with the key.
        tier : Optional[str], optional
            Service tier associated with the key.
        expires_in_seconds : Optional[int], optional
            Number of seconds until the key expires.

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        target_key = api_key or self.api_key
        expires_at = None
        if expires_in_seconds is not None:
            expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)

        self.validator.set_key_metadata(api_key=target_key, owner=owner, permissions=permissions, tier=tier, expires_at=expires_at)
        return self

    def with_key_format_validation(self, pattern: str) -> "ApiKeyAuthMock":
        """
        Set a regex pattern that valid API keys must match.

        Parameters
        ----------
        pattern : str
            Regular expression pattern for API key validation.

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        self.validator.set_key_format_pattern(re.compile(pattern))
        return self

    def revoke_key(self, api_key: Optional[str] = None) -> "ApiKeyAuthMock":
        """
        Revoke a specific API key or the current key.

        Parameters
        ----------
        api_key : Optional[str], optional
            The API key to revoke (defaults to the current key).

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        target_key = api_key or self.api_key
        self.validator.revoke_key(target_key)
        return self

    def with_rate_limiting(self, requests_per_period: int = 100, period_seconds: int = 3600) -> "ApiKeyAuthMock":
        """
        Enable rate limiting for API keys.

        Parameters
        ----------
        requests_per_period : int, optional
            Number of requests allowed per period. Defaults to 100.
        period_seconds : int, optional
            Period length in seconds. Defaults to 3600.

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        self.rate_limiter.enable_rate_limiting(requests_per_period=requests_per_period, period_seconds=period_seconds)
        return self

    def with_usage_tracking(self) -> "ApiKeyAuthMock":
        """
        Enable usage tracking for API keys.

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        self.usage_tracker.enable_usage_tracking()
        return self

    def as_header(self, header_name: str = "X-API-Key") -> "ApiKeyAuthMock":
        """
        Configure the API Key Auth to use a header.

        Parameters
        ----------
        header_name : str, optional
            Name of the header for the API key. Defaults to "X-API-Key".

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        self.header_name = header_name
        self.param_name = None
        self.auth_strategy = ApiKeyAuth(api_key=self.api_key, header_name=header_name)
        return self

    def as_param(self, param_name: str = "api_key") -> "ApiKeyAuthMock":
        """
        Configure the API Key Auth to use a query parameter.

        Parameters
        ----------
        param_name : str, optional
            Name of the query parameter for the API key. Defaults to "api_key".

        Returns
        -------
        ApiKeyAuthMock
            Self for method chaining.
        """
        self.header_name = None
        self.param_name = param_name
        self.auth_strategy = ApiKeyAuth(api_key=self.api_key, param_name=param_name)
        return self

    def track_request(self, api_key: str, endpoint: Optional[str] = None) -> bool:
        """
        Track a request for rate limiting and usage tracking purposes.

        Parameters
        ----------
        api_key : str
            The API key used for the request.
        endpoint : Optional[str], optional
            The endpoint being accessed (for usage tracking).

        Returns
        -------
        bool
            True if the request is within rate limits, False otherwise.
        """
        self.usage_tracker.track_request(api_key, endpoint)

        return self.rate_limiter.track_request(api_key)

    def validate_key(self, api_key: str) -> bool:
        """
        Validate an API key against all configured rules.

        Parameters
        ----------
        api_key : str
            The API key to validate.

        Returns
        -------
        bool
            True if the key is valid, False otherwise.
        """
        if not self.validator.validate_key(api_key):
            return False

        if self.rate_limiter.rate_limit_enabled:
            if not self.track_request(api_key):
                return False
        elif self.usage_tracker.usage_tracking_enabled:
            self.usage_tracker.track_request(api_key)

        return True

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the API Key header has the correct format and key is valid.

        Parameters
        ----------
        header_value : str
            The value of the API key header.

        Returns
        -------
        bool
            True if the header is valid, False otherwise.
        """
        if not self.header_name:
            return False

        try:
            AuthHeaderVerification.verify_api_key_header(header_value)
        except AuthenticationError:
            return False

        return self.validate_key(header_value)

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the API key is being used correctly.

        Parameters
        ----------
        token : str
            The API key to verify.

        Returns
        -------
        bool
            True if the key is being used correctly, False otherwise.
        """
        return self.validate_key(token)

    def get_usage_stats(self) -> Dict:
        """
        Get usage statistics for API keys and endpoints.

        Returns
        -------
        Dict
            Dictionary with usage statistics.
        """
        return self.usage_tracker.get_usage_stats()

    def get_rate_limit_status(self, api_key: Optional[str] = None) -> Dict:
        """
        Get rate limit status for a specific API key or the current key.

        Parameters
        ----------
        api_key : Optional[str], optional
            The API key to get status for (defaults to the current key).

        Returns
        -------
        Dict
            Dictionary with rate limit status.
        """
        target_key = api_key or self.api_key
        return self.rate_limiter.get_rate_limit_status(target_key)

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns
        -------
        AuthStrategy
            The configured ApiKeyAuth strategy.
        """
        return self.auth_strategy

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers for the current API key.

        Returns
        -------
        Optional[Tuple[str, str]]
            A tuple of (header_name, api_key) or None if using param auth.
        """
        if self.header_name and self.api_key:
            return (self.header_name, self.api_key)
        return None

    def handle_auth_error(self, response: "MockResponse") -> bool:
        """
        Handle authentication errors (API keys don't have a refresh mechanism).

        Parameters
        ----------
        response : MockResponse
            The error response that triggered the auth error.

        Returns
        -------
        bool
            Always False for API keys as they don't have a refresh mechanism.
        """
        return False
