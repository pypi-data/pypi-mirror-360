"""
Base Class for Authentication Mocks using a Builder-like Configuration.

This module provides `AuthMockBase`, the foundation for all specialized
authentication mock classes (e.g., `BasicAuthMock`, `OAuthMock`) in the
`crudclient` testing framework. It utilizes a **Builder pattern** variant
for configuration, offering a fluent, chainable interface (`with_...` methods)
to set up complex mock behaviors.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

if TYPE_CHECKING:
    from ..response_builder import MockResponse


class AuthMockBase(ABC):
    """
    Base class for authentication mocks using a **Builder pattern** for configuration.

    This class provides common state and behavior simulation logic for various
    authentication scenarios (failure, token expiration, refresh, MFA). It employs
    a fluent interface with chainable `with_...` methods, acting as a Builder
    to construct the desired configuration and state of the authentication mock
    before it's used in a test.

    Example Usage (Builder pattern)
    -------------------------------
    ```python
    mock_auth = ConcreteAuthMock() \\
        .with_failure(status_code=403, message="Forbidden") \\
        .fail_after(3)
    ```

    Specialized authentication mocks (e.g., `BasicAuthMock`, `OAuthMock`) inherit
    from this base, potentially adding their own specific configuration methods
    while leveraging the common builder infrastructure.

    Attributes
    ----------
    should_fail : bool
        If True, authentication will fail.
    failure_type : str
        Type of authentication failure (e.g., "invalid_token", "expired_token").
    failure_status_code : int
        HTTP status code to return for the failure.
    failure_message : str
        Error message to include in the response.
    token_expired : bool
        If True, the token is considered expired.
    token_expiry_time : Optional[datetime]
        The datetime when the token expires.
    refresh_token : Optional[str]
        The refresh token value.
    refresh_token_expired : bool
        If True, the refresh token is considered expired.
    refresh_attempts : int
        Current number of refresh attempts.
    max_refresh_attempts : int
        Maximum allowed refresh attempts.
    mfa_required : bool
        If True, multi-factor authentication is required.
    mfa_verified : bool
        If True, MFA has been verified.
    request_count : int
        Number of requests made.
    fail_after_requests : Optional[int]
        Number of successful requests after which authentication should fail.
    custom_headers : Dict[str, str]
        Custom headers to include in authentication responses.
    custom_params : Dict[str, str]
        Custom parameters to include in authentication responses.
    """

    should_fail: bool
    failure_type: str
    failure_status_code: int
    failure_message: str
    token_expired: bool
    token_expiry_time: Optional[datetime]
    refresh_token: Optional[str]
    refresh_token_expired: bool
    refresh_attempts: int
    max_refresh_attempts: int
    mfa_required: bool
    mfa_verified: bool
    request_count: int
    fail_after_requests: Optional[int]
    custom_headers: Dict[str, str]
    custom_params: Dict[str, str]

    def __init__(self) -> None:
        """Initialize the base authentication mock with default settings."""
        self.should_fail = False
        self.failure_type = "invalid_token"
        self.failure_status_code = 401
        self.failure_message = "Authentication failed"
        self.token_expired = False
        self.token_expiry_time = None
        self.refresh_token = None
        self.refresh_token_expired = False
        self.refresh_attempts = 0
        self.max_refresh_attempts = 3
        self.mfa_required = False
        self.mfa_verified = False
        self.request_count = 0
        self.fail_after_requests = None
        self.custom_headers = {}
        self.custom_params = {}

    def with_failure(self, failure_type: str = "invalid_token", status_code: int = 401, message: str = "Authentication failed") -> "AuthMockBase":
        """
        Configure the mock to simulate authentication failure.

        Parameters
        ----------
        failure_type : str, optional
            Type of authentication failure (e.g., "invalid_token", "expired_token").
            Defaults to "invalid_token".
        status_code : int, optional
            HTTP status code to return for the failure. Defaults to 401.
        message : str, optional
            Error message to include in the response. Defaults to "Authentication failed".

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.should_fail = True
        self.failure_type = failure_type
        self.failure_status_code = status_code
        self.failure_message = message
        return self

    def with_success(self) -> "AuthMockBase":
        """
        Configure the mock to simulate authentication success.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.should_fail = False
        return self

    def with_token_expiration(self, expires_in_seconds: int = 3600) -> "AuthMockBase":
        """
        Configure the mock to simulate token expiration.

        Parameters
        ----------
        expires_in_seconds : int, optional
            Number of seconds until the token expires. Defaults to 3600.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.token_expired = False
        self.token_expiry_time = datetime.now() + timedelta(seconds=expires_in_seconds)
        return self

    def with_expired_token(self) -> "AuthMockBase":
        """
        Configure the mock to simulate an already expired token.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.token_expired = True
        self.token_expiry_time = datetime.now() - timedelta(seconds=60)
        return self

    def with_refresh_token(self, refresh_token: str = "refresh_token", max_refresh_attempts: int = 3) -> "AuthMockBase":
        """
        Configure the mock with a refresh token.

        Parameters
        ----------
        refresh_token : str, optional
            The refresh token value. Defaults to "refresh_token".
        max_refresh_attempts : int, optional
            Maximum number of times the token can be refreshed. Defaults to 3.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.refresh_token = refresh_token
        self.refresh_token_expired = False
        self.refresh_attempts = 0
        self.max_refresh_attempts = max_refresh_attempts
        return self

    def with_expired_refresh_token(self) -> "AuthMockBase":
        """
        Configure the mock with an expired refresh token.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.refresh_token = "expired_refresh_token"
        self.refresh_token_expired = True
        return self

    def with_mfa_required(self, verified: bool = False) -> "AuthMockBase":
        """
        Configure the mock to require multi-factor authentication.

        Parameters
        ----------
        verified : bool, optional
            Whether MFA has been verified. Defaults to False.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.mfa_required = True
        self.mfa_verified = verified
        return self

    def fail_after(self, request_count: int) -> "AuthMockBase":
        """
        Configure the mock to fail after a specific number of requests.

        Parameters
        ----------
        request_count : int
            Number of successful requests before failing.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.fail_after_requests = request_count
        return self

    def with_custom_header(self, name: str, value: str) -> "AuthMockBase":
        """
        Add a custom header to the auth strategy.

        Parameters
        ----------
        name : str
            Header name.
        value : str
            Header value.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.custom_headers[name] = value
        return self

    def with_custom_param(self, name: str, value: str) -> "AuthMockBase":
        """
        Add a custom parameter to the auth strategy.

        Parameters
        ----------
        name : str
            Parameter name.
        value : str
            Parameter value.

        Returns
        -------
        AuthMockBase
            Self for method chaining.
        """
        self.custom_params[name] = value
        return self

    def is_token_expired(self) -> bool:
        """
        Check if the token is expired.

        Returns
        -------

        bool
            True if the token is expired, False otherwise.
        """
        if self.token_expired:
            return True
        if self.token_expiry_time is not None and datetime.now() > self.token_expiry_time:
            self.token_expired = True
            return True
        return False

    def can_refresh_token(self) -> bool:
        """
        Check if the token can be refreshed.

        Returns
        -------

        bool
            True if the token can be refreshed, False otherwise.
        """
        if not self.refresh_token:
            return False
        if self.refresh_token is not None and self.refresh_token_expired:
            return False
        if self.refresh_attempts >= self.max_refresh_attempts:
            return False
        return True

    def refresh(self) -> bool:
        """
        Attempt to refresh the token.

        Returns
        -------

        bool
            True if the token was refreshed successfully, False otherwise.
        """
        if not self.can_refresh_token():
            return False

        self.refresh_attempts += 1
        self.token_expired = False
        self.token_expiry_time = datetime.now() + timedelta(seconds=3600)
        return True

    def should_fail_auth(self) -> bool:
        """
        Determine if authentication should fail.

        Returns
        -------

        bool
            True if authentication should fail, False otherwise.
        """
        self.request_count += 1

        if self.should_fail:
            return True

        if self.fail_after_requests is not None and self.request_count > self.fail_after_requests:
            return True

        if self.is_token_expired() and not self.can_refresh_token():
            return True

        if self.mfa_required and not self.mfa_verified:
            return True

        return False

    def get_auth_error_response(self) -> Any:
        """
        Get the appropriate authentication error response.

        Returns
        -------

        Any
            A mock response object with appropriate error details.
        """
        error_type = self.failure_type
        status_code = self.failure_status_code

        if self.is_token_expired():
            error_type = "expired_token"
            status_code = 401
        elif self.mfa_required and not self.mfa_verified:
            error_type = "mfa_required"
            status_code = 401

        from ..response_builder import ResponseBuilder

        return ResponseBuilder.create_auth_error(error_type=error_type, status_code=status_code)

    @abstractmethod
    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers for the current token.

        Returns
        -------

        Optional[Tuple[str, str]]
            A tuple of (header_name, header_value) or None if no valid token.
        """

    @abstractmethod
    def handle_auth_error(self, response: "MockResponse") -> bool:
        """
        Handle authentication errors by attempting to refresh tokens or other recovery.

        Parameters
        ----------
        response : MockResponse
            The error response that triggered the auth error.

        Returns
        -------

        bool
            True if the error was handled and the request should be retried, False otherwise.
        """

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the authentication header has the correct format.

        Parameters
        ----------
        header_value : str
            The value of the authentication header.

        Returns
        -------

        bool
            True if the header is valid, False otherwise.
        """
        return True

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the token is being used correctly.

        Parameters
        ----------
        token : str
            The token to verify.

        Returns
        -------

        bool
            True if the token is being used correctly, False otherwise.
        """
        return True

    def verify_refresh_behavior(self, old_token: str, new_token: str) -> bool:
        """
        Verify that token refresh behavior is correct.

        Parameters
        ----------
        old_token : str
            The token before refresh.
        new_token : str
            The token after refresh.

        Returns
        -------

        bool
            True if the refresh behavior is correct, False otherwise.
        """
        return old_token != new_token
