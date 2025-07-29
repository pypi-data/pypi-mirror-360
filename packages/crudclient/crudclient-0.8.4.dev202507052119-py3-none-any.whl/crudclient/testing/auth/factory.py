"""
Factory functions for creating authentication mocks.

This module provides factory functions for creating pre-configured authentication mocks
with enhanced validation, rate limiting, and OAuth capabilities.
"""

from typing import Callable, Dict, List, Optional

from .api_key import ApiKeyAuthMock
from .basic import BasicAuthMock
from .bearer import BearerAuthMock
from .custom import CustomAuthMock, OAuthMock


def create_basic_auth_mock(
    username: str = "user", password: str = "pass", case_sensitive: bool = True, max_attempts: Optional[int] = None
) -> BasicAuthMock:
    """
    Create a Basic Authentication mock with enhanced validation.

    This factory function creates a pre-configured BasicAuthMock instance with
    the specified settings, providing a convenient way to create mocks for testing.

    Args:
        username: The username for authentication
        password: The password for authentication
        case_sensitive: Whether username validation should be case-sensitive
        max_attempts: Maximum number of authentication attempts before failing

    Returns:
        A configured BasicAuthMock instance
    """
    mock = BasicAuthMock(username=username, password=password)

    if not case_sensitive:
        mock.with_case_insensitive_username()

    if max_attempts is not None:
        mock.with_max_attempts(max_attempts)

    return mock


def create_bearer_auth_mock(
    token: str = "valid_token",
    expires_in_seconds: Optional[int] = None,
    scopes: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    client_id: Optional[str] = None,
) -> BearerAuthMock:
    """
    Create a Bearer Authentication mock with token validation and expiration.

    This factory function creates a pre-configured BearerAuthMock instance with
    the specified settings, providing a convenient way to create mocks for testing.

    Args:
        token: The bearer token for authentication
        expires_in_seconds: Token expiration time in seconds (None for no expiration)
        scopes: List of scopes associated with the token
        user_id: User ID associated with the token
        client_id: Client ID associated with the token

    Returns:
        A configured BearerAuthMock instance
    """
    mock = BearerAuthMock(token=token)

    if expires_in_seconds is not None:
        mock.with_token_expiration(expires_in_seconds)

    if scopes is not None or user_id is not None or client_id is not None:
        mock.with_token_metadata(user_id=user_id, client_id=client_id, scopes=scopes)

    return mock


def create_api_key_auth_mock(
    api_key: str = "valid_api_key",
    header_name: Optional[str] = "X-API-Key",
    param_name: Optional[str] = None,
    rate_limit: bool = False,
    requests_per_period: int = 100,
    period_seconds: int = 3600,
    track_usage: bool = False,
    expires_in_seconds: Optional[int] = None,
) -> ApiKeyAuthMock:
    """
    Create an API Key Authentication mock with validation and rate limiting.

    This factory function creates a pre-configured ApiKeyAuthMock instance with
    the specified settings, providing a convenient way to create mocks for testing.

    Args:
        api_key: The API key for authentication
        header_name: Name of the header for API key (None if using param)
        param_name: Name of the query parameter for API key (None if using header)
        rate_limit: Whether to enable rate limiting
        requests_per_period: Number of requests allowed per period
        period_seconds: Rate limit period in seconds
        track_usage: Whether to enable usage tracking
        expires_in_seconds: API key expiration time in seconds (None for no expiration)

    Returns:
        A configured ApiKeyAuthMock instance
    """
    mock = ApiKeyAuthMock(api_key=api_key, header_name=header_name, param_name=param_name)

    if rate_limit:
        mock.with_rate_limiting(requests_per_period, period_seconds)

    if track_usage:
        mock.with_usage_tracking()

    if expires_in_seconds is not None:
        mock.with_key_metadata(expires_in_seconds=expires_in_seconds)

    return mock


def create_custom_auth_mock(
    header_callback: Optional[Callable[[], Dict[str, str]]] = None,
    param_callback: Optional[Callable[[], Dict[str, str]]] = None,
    required_headers: Optional[List[str]] = None,
    required_params: Optional[List[str]] = None,
) -> CustomAuthMock:
    """
    Create a Custom Authentication mock with enhanced validation.

    This factory function creates a pre-configured CustomAuthMock instance with
    the specified settings, providing a convenient way to create mocks for testing.

    Args:
        header_callback: Callback function that returns authentication headers
        param_callback: Callback function that returns authentication parameters
        required_headers: List of required header names
        required_params: List of required parameter names

    Returns:
        A configured CustomAuthMock instance
    """
    mock = CustomAuthMock(header_callback=header_callback, param_callback=param_callback)

    if required_headers:
        mock.with_required_headers(required_headers)  # type: ignore[attr-defined]

    if required_params:
        mock.with_required_params(required_params)  # type: ignore[attr-defined]

    return mock


def create_oauth_mock(
    client_id: str = "client_id",
    client_secret: str = "client_secret",
    grant_type: str = "authorization_code",
    scope: str = "read write",
    token_url: str = "https://example.com/oauth/token",
    authorize_url: Optional[str] = "https://example.com/oauth/authorize",
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> OAuthMock:
    """
    Create an OAuth Authentication mock with support for different grant types and scopes.

    This factory function creates a pre-configured OAuthMock instance with
    the specified settings, providing a convenient way to create mocks for testing.

    Args:
        client_id: OAuth client ID
        client_secret: OAuth client secret
        grant_type: OAuth grant type (authorization_code, client_credentials, password, etc.)
        scope: OAuth scope string (space-separated)
        token_url: URL for token endpoint
        authorize_url: URL for authorization endpoint
        access_token: Custom access token (None for default)
        refresh_token: Custom refresh token (None for default)

    Returns:
        A configured OAuthMock instance
    """
    mock = OAuthMock(client_id=client_id, client_secret=client_secret, token_url=token_url, authorize_url=authorize_url, scope=scope)

    mock.with_grant_type(grant_type)

    if access_token:
        mock.with_access_token(access_token)

    if refresh_token:
        mock.with_refresh_token(refresh_token)

    return mock
