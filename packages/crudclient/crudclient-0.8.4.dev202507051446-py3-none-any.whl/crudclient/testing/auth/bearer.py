"""
Bearer authentication mock for testing.

This module provides a mock implementation of Bearer authentication
for testing API clients with token-based authentication.
"""

from datetime import datetime, timedelta
from re import Pattern
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)

from apiconfig.testing.auth_verification import AuthHeaderVerification

from crudclient.auth import AuthStrategy, BearerAuth
from crudclient.exceptions import AuthenticationError

from .base import AuthMockBase

if TYPE_CHECKING:
    from ..response_builder import MockResponse


class BearerAuthMock(AuthMockBase):
    """
    Mock implementation of Bearer authentication.

    This class provides a configurable mock for Bearer token authentication,
    supporting token validation, expiration, refresh, and various other
    authentication scenarios.
    """

    def __init__(self, token: str = "valid_token"):
        """
        Initialize a BearerAuthMock instance.

        Args:
            token: Initial bearer token value
        """
        super().__init__()
        self.token = token
        self.auth_strategy = BearerAuth(access_token=token)
        self.issued_tokens = [token]
        self.revoked_tokens: Set[str] = set()
        self.token_metadata: Dict[str, Dict] = {
            token: {
                "issued_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=1),
                "scopes": ["read", "write"],
                "user_id": "default_user",
                "client_id": "default_client",
            }
        }
        self.valid_token_prefixes: Set[str] = set()
        self.token_format_pattern: Optional[Pattern[str]] = None
        self.required_scopes: List[str] = []
        self.jwt_validation = False
        self.token_type = "access_token"  # Can be "access_token", "id_token", "refresh_token"

    def with_token(self, token: str) -> "BearerAuthMock":
        """
        Configure the mock with a specific token.

        Args:
            token: Bearer token value

        Returns:
            Self for method chaining
        """
        self.token = token
        self.auth_strategy = BearerAuth(access_token=token)
        self.issued_tokens = [token]
        self.token_metadata = {
            token: {
                "issued_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=1),
                "scopes": ["read", "write"],
                "user_id": "default_user",
                "client_id": "default_client",
            }
        }
        return self

    def with_token_metadata(
        self, user_id: Optional[str] = None, client_id: Optional[str] = None, scopes: Optional[List[str]] = None
    ) -> "BearerAuthMock":
        """
        Configure the mock with token metadata.

        Args:
            user_id: User ID associated with the token
            client_id: Client ID associated with the token
            scopes: Permission scopes associated with the token

        Returns:
            Self for method chaining
        """
        if self.token not in self.token_metadata:
            self.token_metadata[self.token] = {
                "issued_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=1),
                "scopes": ["read", "write"],
                "user_id": "default_user",
                "client_id": "default_client",
            }

        metadata = self.token_metadata[self.token]

        if user_id:
            metadata["user_id"] = user_id
        if client_id:
            metadata["client_id"] = client_id
        if scopes:
            metadata["scopes"] = scopes

        return self

    def with_token_expiration(self, expires_in_seconds: int = 3600, token: Optional[str] = None) -> "BearerAuthMock":
        """
        Configure the mock with token expiration.

        Args:
            expires_in_seconds: Number of seconds until the token expires
            token: Specific token to configure expiration for (defaults to current token)

        Returns:
            Self for method chaining
        """
        target_token = token or self.token
        if target_token not in self.token_metadata:
            self.token_metadata[target_token] = {
                "issued_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=expires_in_seconds),
                "scopes": ["read", "write"],
                "user_id": "default_user",
                "client_id": "default_client",
            }
        else:
            self.token_metadata[target_token]["expires_at"] = datetime.now() + timedelta(seconds=expires_in_seconds)

        # Update the base class expiry time for compatibility
        super().with_token_expiration(expires_in_seconds)
        return self

    def with_token_format_validation(self, pattern: str) -> "BearerAuthMock":
        """
        Configure the mock with token format validation.

        Args:
            pattern: Regular expression pattern for valid token format

        Returns:
            Self for method chaining
        """
        import re

        self.token_format_pattern = re.compile(pattern)
        return self

    def with_valid_token_prefix(self, prefix: str) -> "BearerAuthMock":
        """
        Configure the mock with a valid token prefix.

        Args:
            prefix: Valid token prefix

        Returns:
            Self for method chaining
        """
        self.valid_token_prefixes.add(prefix)
        return self

    def with_required_scopes(self, scopes: List[str]) -> "BearerAuthMock":
        """
        Configure the mock with required permission scopes.

        Args:
            scopes: List of required permission scopes

        Returns:
            Self for method chaining
        """
        self.required_scopes = scopes
        return self

    def with_jwt_validation(self) -> "BearerAuthMock":
        """
        Configure the mock to validate tokens as JWTs.

        Returns:
            Self for method chaining
        """
        self.jwt_validation = True
        return self

    def with_token_type(self, token_type: str) -> "BearerAuthMock":
        """
        Configure the mock with a specific token type.

        Args:
            token_type: Token type (e.g., "access_token", "id_token", "refresh_token")

        Returns:
            Self for method chaining
        """
        self.token_type = token_type
        return self

    def revoke_token(self, token: str) -> "BearerAuthMock":
        """
        Revoke a specific token.

        Args:
            token: Token to revoke

        Returns:
            Self for method chaining
        """
        if token in self.issued_tokens:
            self.revoked_tokens.add(token)
        return self

    def refresh(self) -> bool:
        """
        Attempt to refresh the token.

        Returns:
            True if the token was refreshed successfully, False otherwise
        """
        if not super().refresh():
            return False

        # Generate a new token
        new_token = f"{self.token}_refreshed_{self.refresh_attempts}"

        # Copy metadata from old token
        if self.token in self.token_metadata:
            old_metadata = self.token_metadata[self.token]
            self.token_metadata[new_token] = old_metadata.copy()
            # Update expiration
            self.token_metadata[new_token]["issued_at"] = datetime.now()
            self.token_metadata[new_token]["expires_at"] = datetime.now() + timedelta(hours=1)
        else:
            # Create new metadata if old token doesn't have any
            self.token_metadata[new_token] = {
                "issued_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=1),
                "scopes": ["read", "write"],
                "user_id": "default_user",
                "client_id": "default_client",
            }

        # Update token
        self.token = new_token
        self.auth_strategy = BearerAuth(access_token=new_token)
        self.issued_tokens.append(new_token)
        return True

    def verify_auth_header(self, header_value: str) -> bool:
        """Verify that the authentication header has the correct format."""
        try:
            AuthHeaderVerification.verify_bearer_auth_header(header_value)
        except AuthenticationError:
            return False

        token = header_value[7:]
        return self.validate_token(token)

    def validate_token(self, token: str) -> bool:
        """
        Validate a token.

        Args:
            token: Token to validate

        Returns:
            True if the token is valid, False otherwise
        """
        # Check if token has been issued
        if token not in self.issued_tokens:
            return False

        # Check if token has been revoked
        if token in self.revoked_tokens:
            return False

        # Check token format if pattern is set
        if self.token_format_pattern and not self.token_format_pattern.match(token):
            return False

        # Check token prefix if any are set
        if self.valid_token_prefixes and not any(token.startswith(prefix) for prefix in self.valid_token_prefixes):
            return False

        # Check token expiration
        if token in self.token_metadata:
            expires_at = self.token_metadata[token].get("expires_at")
            if expires_at and datetime.now() > expires_at:
                return False

            # Check scopes if required
            if self.required_scopes:
                token_scopes = self.token_metadata[token].get("scopes", [])
                if not all(scope in token_scopes for scope in self.required_scopes):
                    return False

        # JWT validation would go here if implemented
        if self.jwt_validation:
            # This would be a more complex validation in a real implementation
            # For now, we'll just check if the token looks like a JWT (has two dots)
            if token.count(".") != 2:
                return False

        return True

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the token is being used correctly.

        Args:
            token: The token to verify

        Returns:
            True if the token is being used correctly, False otherwise
        """
        return token in self.issued_tokens and token not in self.revoked_tokens

    def get_token_metadata(self, token: str) -> Optional[Dict]:
        """
        Get metadata for a specific token.

        Args:
            token: Token to get metadata for

        Returns:
            Token metadata or None if the token is not found
        """
        return self.token_metadata.get(token)

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers.

        Returns:
            Tuple of (header_name, header_value) or None if no token is available
        """
        if not self.token:
            return None
        return ("Authorization", f"Bearer {self.token}")

    def handle_auth_error(self, response: "MockResponse") -> bool:
        """
        Handle an authentication error.

        Args:
            response: Mock response with authentication error

        Returns:
            True if the error was handled successfully, False otherwise
        """
        # Check if the error is likely due to token expiration and if we can refresh
        is_expired = self.is_token_expired()
        if is_expired and self.can_refresh_token():
            # Attempt to refresh the token
            refreshed = self.refresh()
            return refreshed  # Return True if refresh succeeded, False otherwise

        # If not an expiration error or refresh is not possible/failed
        return False

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the underlying authentication strategy.

        Returns:
            BearerAuth instance
        """
        return self.auth_strategy
