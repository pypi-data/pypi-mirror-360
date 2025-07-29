"""
OAuth token management utilities for testing.

This module provides a class for managing OAuth tokens, including creation,
validation, and refreshing of tokens.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class OAuthTokenManager:
    """
    OAuth token manager for handling token lifecycle.

    This class provides methods for creating, validating, and refreshing OAuth tokens,
    as well as managing users for password grant type.
    """

    def __init__(self) -> None:
        """
        Initialize an OAuth token manager.
        """
        # Token management
        self.access_tokens: Dict[str, Dict] = {}
        self.refresh_tokens: Dict[str, str] = {}  # refresh_token -> access_token
        self.authorization_codes: Dict[str, Dict] = {}
        self.current_access_token = "access_token"
        self.current_refresh_token = "refresh_token"
        self._token_counter = 0  # Counter to ensure unique tokens even with same timestamp

        # User management for password grant
        self.user_credentials: Dict[str, Dict] = {"user": {"password": "pass", "scopes": ["read", "write"]}}  # Renamed from self.users

    def initialize_default_token(self, client_id: str, scope: Optional[str]) -> None:
        """
        Initialize a default token for the OAuth server.

        Args:
            client_id: The client ID
            scope: The scope for the token
        """
        now = datetime.now()
        self.access_tokens[self.current_access_token] = {
            "client_id": client_id,
            "scope": scope,
            "expires_at": now + timedelta(hours=1),
            "token_type": "Bearer",
            "grant_type": "client_credentials",
        }

        self.refresh_tokens[self.current_refresh_token] = self.current_access_token

    def create_token(
        self,
        client_id: str,
        scope: Optional[str] = None,
        expires_in: int = 3600,
        token_type: str = "Bearer",
        grant_type: str = "client_credentials",
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new access token and refresh token pair.

        Args:
            client_id: The client ID
            scope: The scope for the token
            expires_in: The number of seconds until the token expires
            token_type: The token type (e.g., "Bearer")
            grant_type: The grant type used to obtain the token
            user: The username for password grant type

        Returns:
            A dictionary with the token response
        """
        now = datetime.now()
        self._token_counter += 1
        access_token = f"access_token_{now.timestamp()}_{self._token_counter}"
        refresh_token = f"refresh_token_{now.timestamp()}_{self._token_counter}"

        self.access_tokens[access_token] = {
            "client_id": client_id,
            "scope": scope,
            "expires_at": now + timedelta(seconds=expires_in),
            "token_type": token_type,
            "grant_type": grant_type,
            "user": user,
        }

        self.refresh_tokens[refresh_token] = access_token
        self.current_access_token = access_token
        self.current_refresh_token = refresh_token

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "token_type": token_type,
            "scope": scope or "",
        }

    def create_authorization_code(self, client_id: str, redirect_uri: str, scope: Optional[str] = None, state: Optional[str] = None) -> str:
        """
        Create a new authorization code.

        Args:
            client_id: The client ID
            redirect_uri: The redirect URI
            scope: The scope for the token
            state: The state parameter

        Returns:
            The authorization code
        """
        now = datetime.now()
        code = f"auth_code_{now.timestamp()}"

        self.authorization_codes[code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "expires_at": now + timedelta(minutes=10),
        }

        return code

    def validate_token(self, token: str) -> bool:
        """
        Check if a token is valid.

        Args:
            token: The token to validate

        Returns:
            True if the token is valid, False otherwise
        """
        if token not in self.access_tokens:
            return False

        token_data = self.access_tokens[token]
        if token_data["expires_at"] < datetime.now():
            return False

        return True

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            A dictionary with the new token response, or None if the refresh token is invalid
        """
        if refresh_token not in self.refresh_tokens:
            return None

        old_access_token = self.refresh_tokens[refresh_token]
        if old_access_token not in self.access_tokens:
            return None

        old_token_data = self.access_tokens[old_access_token]

        # Create a new token with the same properties
        return self.create_token(
            client_id=old_token_data["client_id"],
            scope=old_token_data["scope"],
            token_type=old_token_data["token_type"],
            grant_type="refresh_token",
            user=old_token_data.get("user"),
        )

    def revoke_token(self, token: str) -> bool:
        """
        Revoke an access token.

        Args:
            token: The token to revoke

        Returns:
            True if the token was revoked, False if it was not found
        """
        if token not in self.access_tokens:
            return False

        # Find and remove the refresh token associated with this access token
        refresh_token_to_remove = None
        for rt, at in self.refresh_tokens.items():
            if at == token:
                refresh_token_to_remove = rt
                break
        if refresh_token_to_remove:
            del self.refresh_tokens[refresh_token_to_remove]

        # Remove the access token itself
        del self.access_tokens[token]

        # If the revoked token was the current one, find a new current token
        if self.current_access_token == token:
            # Check if there are any tokens left after deletion
            if self.access_tokens:
                # Find the oldest token based on the timestamp in the token string
                # Format is "access_token_<timestamp>"
                tokens = list(self.access_tokens.keys())
                # Sort tokens by timestamp (if they have a timestamp)
                tokens_with_timestamp = []
                for token in tokens:
                    if "_" in token and token.split("_")[-1].replace(".", "").isdigit():
                        timestamp = float(token.split("_")[-1])
                        tokens_with_timestamp.append((token, timestamp))

                if tokens_with_timestamp:
                    # Sort by timestamp (ascending)
                    tokens_with_timestamp.sort(key=lambda x: x[1])
                    oldest_token = tokens_with_timestamp[0][0]
                    self.current_access_token = oldest_token
                else:
                    # If no tokens with timestamp, just pick the first one
                    self.current_access_token = tokens[0]

                # Find the corresponding refresh token for the new current access token
                new_refresh_token = ""
                for rt, at in self.refresh_tokens.items():
                    if at == self.current_access_token:
                        new_refresh_token = rt
                        break
                self.current_refresh_token = new_refresh_token
            else:
                # No more tokens left at all
                self.current_access_token = ""
                self.current_refresh_token = ""

        return True

    def add_user(self, username: str, password: str, scopes: List[str]) -> None:
        """
        Add a user for password grant type.

        Args:
            username: The username
            password: The password
            scopes: The scopes for the user
        """
        self.user_credentials[username] = {"password": password, "scopes": scopes}  # Store in user_credentials dict

    def validate_user(self, username: str, password: str) -> bool:
        """
        Validate user credentials.

        Args:
            username: The username
            password: The password

        Returns:
            True if the credentials are valid, False otherwise
        """
        user_data = self.user_credentials.get(username)  # Get from user_credentials dict
        if not user_data or user_data["password"] != password:
            return False
        return True
