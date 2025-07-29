"""
OAuth authentication mock for testing.

This module provides a mock for OAuth Authentication strategy with support
for different grant types, scopes, and advanced authentication scenarios.
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional, Tuple

from apiconfig.testing.auth_verification import AuthHeaderVerification

from crudclient.auth import AuthStrategy, CustomAuth
from crudclient.exceptions import AuthenticationError

from .base import AuthMockBase
from .oauth_grant_handler import OAuthGrantHandler
from .oauth_scope_validator import OAuthScopeValidator
from .oauth_token_manager import OAuthTokenManager

if TYPE_CHECKING:
    from ..response_builder.response import MockResponse


class OAuthMock(AuthMockBase):
    """
    Mock for OAuth Authentication with support for different grant types and scopes.

    This class provides a configurable mock implementation of OAuth Authentication,
    supporting various grant types, token management, and scope validation.
    """

    client_id: str
    client_secret: str
    token_url: str
    authorize_url: Optional[str]
    redirect_uri: Optional[str]
    scope: Optional[str]
    token_manager: OAuthTokenManager
    scope_validator: OAuthScopeValidator
    grant_handler: OAuthGrantHandler
    auth_strategy: CustomAuth

    def __init__(
        self,
        client_id: str = "client_id",
        client_secret: str = "client_secret",
        token_url: str = "https://example.com/oauth/token",
        authorize_url: Optional[str] = "https://example.com/oauth/authorize",
        redirect_uri: Optional[str] = "https://app.example.com/callback",
        scope: Optional[str] = "read write",
    ) -> None:
        """
        Initialize an OAuth Authentication mock.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            token_url: URL for token endpoint
            authorize_url: URL for authorization endpoint
            redirect_uri: Redirect URI for authorization code flow
            scope: Space-separated list of scopes
        """
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.authorize_url = authorize_url
        self.redirect_uri = redirect_uri
        self.scope = scope

        # Initialize components
        self.token_manager = OAuthTokenManager()
        self.scope_validator = OAuthScopeValidator()
        self.grant_handler = OAuthGrantHandler(self.token_manager, self.scope_validator)

        # Initialize with a default token
        self.token_manager.initialize_default_token(client_id, scope)

        # Create auth strategy
        self.auth_strategy = CustomAuth(header_callback=lambda: {"Authorization": f"Bearer {self.token_manager.current_access_token}"})

    def with_client_credentials(self, client_id: str, client_secret: str) -> "OAuthMock":
        """
        Set the client credentials for the OAuth mock.

        Args:
            client_id: The client ID
            client_secret: The client secret

        Returns:
            Self for method chaining
        """
        self.client_id = client_id
        self.client_secret = client_secret
        return self

    def with_token_url(self, token_url: str) -> "OAuthMock":
        """
        Set the token URL for the OAuth mock.

        Args:
            token_url: The token URL

        Returns:
            Self for method chaining
        """
        self.token_url = token_url
        return self

    def with_authorize_url(self, authorize_url: str) -> "OAuthMock":
        """
        Set the authorize URL for the OAuth mock.

        Args:
            authorize_url: The authorize URL

        Returns:
            Self for method chaining
        """
        self.authorize_url = authorize_url
        return self

    def with_redirect_uri(self, redirect_uri: str) -> "OAuthMock":
        """
        Set the redirect URI for the OAuth mock.

        Args:
            redirect_uri: The redirect URI

        Returns:
            Self for method chaining
        """
        self.redirect_uri = redirect_uri
        return self

    def with_scope(self, scope: str) -> "OAuthMock":
        """
        Set the scope for the OAuth mock.

        Args:
            scope: The scope

        Returns:
            Self for method chaining
        """
        self.scope = scope
        return self

    def with_grant_type(self, grant_type: str) -> "OAuthMock":
        """
        Set the grant type for the OAuth mock.

        Args:
            grant_type: The grant type

        Returns:
            Self for method chaining
        """
        self.grant_handler.set_default_grant_type(grant_type)
        return self

    def with_access_token(self, access_token: str) -> "OAuthMock":
        """
        Set the access token for the OAuth mock.

        Args:
            access_token: The access token

        Returns:
            Self for method chaining
        """
        # Create a new token with the specified value
        now = datetime.now()
        self.token_manager.access_tokens[access_token] = {
            "client_id": self.client_id,
            "scope": self.scope,
            "expires_at": now + timedelta(hours=1),
            "token_type": "Bearer",
            "grant_type": self.grant_handler.grant_type,
        }

        # Update the current token
        self.token_manager.current_access_token = access_token

        # Update the auth strategy
        self.auth_strategy = CustomAuth(header_callback=lambda: {"Authorization": f"Bearer {access_token}"})

        return self

    def with_refresh_token(self, refresh_token: str = "refresh_token", max_refresh_attempts: int = 3) -> "OAuthMock":
        """
        Set the refresh token for the OAuth mock.

        Args:
            refresh_token: The refresh token
            max_refresh_attempts: Maximum number of refresh attempts allowed

        Returns:
            Self for method chaining
        """
        # Link the refresh token to the current access token
        self.token_manager.refresh_tokens[refresh_token] = self.token_manager.current_access_token
        self.token_manager.current_refresh_token = refresh_token
        # Also update the base class state for consistency
        super().with_refresh_token(refresh_token, max_refresh_attempts)
        return self

    def with_token_expiration(self, expires_in_seconds: int = 3600) -> "OAuthMock":
        """
        Set the token expiration for the OAuth mock.

        Args:
            expires_in_seconds: The number of seconds until the token expires

        Returns:
            Self for method chaining
        """
        # Update the expiration time for the current token
        token_data = self.token_manager.access_tokens[self.token_manager.current_access_token]
        token_data["expires_at"] = datetime.now() + timedelta(seconds=expires_in_seconds)

        return self

    def with_expired_token(self) -> "OAuthMock":
        """
        Set the token to be expired.

        Returns:
            Self for method chaining
        """
        # Set the token to expire in the past
        return self.with_token_expiration(-3600)

    def with_required_scopes(self, scopes: List[str]) -> "OAuthMock":
        """
        Set the required scopes for the OAuth mock.

        Args:
            scopes: The required scopes

        Returns:
            Self for method chaining
        """
        self.scope_validator.set_required_scopes(scopes)
        return self

    def with_available_scopes(self, scopes: List[str]) -> "OAuthMock":
        """
        Set the available scopes for the OAuth mock.

        Args:
            scopes: The available scopes

        Returns:
            Self for method chaining
        """
        self.scope_validator.set_available_scopes(scopes)
        return self

    def with_user(self, username: str, password: str, scopes: List[str]) -> "OAuthMock":
        """
        Add a user for password grant type.

        Args:
            username: The username
            password: The password
            scopes: The scopes for the user

        Returns:
            Self for method chaining
        """
        self.token_manager.add_user(username, password, scopes)
        return self

    def verify_auth_header(self, header_value: str) -> bool:
        """Verify that the Bearer Auth header has the correct format and token is valid."""
        try:
            AuthHeaderVerification.verify_bearer_auth_header(header_value)
        except AuthenticationError:
            return False

        token = header_value[7:]
        return self.token_manager.validate_token(token)

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the token is being used correctly.

        Args:
            token: The token to verify

        Returns:
            True if the token is being used correctly, False otherwise
        """
        return self.token_manager.validate_token(token)

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured CustomAuth strategy
        """
        return self.auth_strategy

    # --- Method Overrides & Implementations ---

    def is_token_expired(self) -> bool:
        """
        Check if the current access token is expired using the token manager.

        Returns:
            True if the token is expired, False otherwise
        """
        token = self.token_manager.current_access_token
        if not token or token not in self.token_manager.access_tokens:
            return True  # No valid current token or token unknown
        token_data = self.token_manager.access_tokens[token]
        # Check if 'expires_at' exists and is in the past
        expires_at = token_data.get("expires_at")
        return expires_at is not None and expires_at < datetime.now()

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers for the current token.

        Returns:
            A tuple of (header_name, header_value) or None if no valid token
        """
        token = self.token_manager.current_access_token
        # Use the overridden is_token_expired to check status
        if not token or self.is_token_expired():
            return None
        return ("Authorization", f"Bearer {token}")

    def handle_auth_error(self, response: "MockResponse") -> bool:
        """
        Attempt to refresh the token if it's expired and refreshable.

        Args:
            response: The error response that triggered the auth error

        Returns:
            True if the error was handled and the request should be retried, False otherwise
        """
        # Use the overridden is_token_expired and base can_refresh_token
        if self.is_token_expired() and self.can_refresh_token():
            # Attempt to refresh via the token manager
            new_token_info = self.token_manager.refresh_token(self.token_manager.current_refresh_token)

            if new_token_info and "access_token" in new_token_info:
                # Update base class state for consistency
                self.refresh_attempts += 1  # Track attempt via base
                # Update the auth_strategy with the new token from token_manager
                self.auth_strategy = CustomAuth(header_callback=lambda: {"Authorization": f"Bearer {self.token_manager.current_access_token}"})
                return True  # Refresh succeeded
            else:
                # Refresh failed via token manager
                return False

        # If not an expiration error or refresh is not possible/failed
        return False
