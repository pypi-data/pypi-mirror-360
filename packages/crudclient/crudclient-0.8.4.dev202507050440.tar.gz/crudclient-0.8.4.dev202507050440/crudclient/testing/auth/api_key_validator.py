"""
API Key validation utilities for testing.

This module provides a class for validating API keys with support for
key format validation, expiration, and revocation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Pattern, Set


class ApiKeyValidator:
    """
    API Key validator with support for key format validation, expiration, and revocation.

    This class provides methods for validating API keys against various rules,
    including key format, expiration, and revocation.
    """

    def __init__(self) -> None:
        """
        Initialize an API Key validator.
        """
        self.valid_keys: Set[str] = set()
        self.key_format_pattern: Optional[Pattern] = None
        self.key_metadata: Dict[str, Dict] = {}
        self.revoked_keys: Set[str] = set()

    def add_valid_key(self, api_key: str) -> None:
        """
        Add a valid API key.

        Args:
            api_key: The API key to add
        """
        self.valid_keys.add(api_key)

    def set_key_metadata(
        self,
        api_key: str,
        owner: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        tier: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        """
        Set metadata for a specific API key.

        Args:
            api_key: The API key to set metadata for
            owner: Owner of the API key
            permissions: List of permissions associated with the key
            tier: Service tier associated with the key
            expires_at: Expiration time for the key
        """
        if api_key not in self.key_metadata:
            self.key_metadata[api_key] = {
                "issued_at": datetime.now(),
                "expires_at": None,
                "owner": "default_user",
                "permissions": ["read", "write"],
                "tier": "standard",
            }

        metadata = self.key_metadata[api_key]

        if owner:
            metadata["owner"] = owner
        if permissions:
            metadata["permissions"] = permissions
        if tier:
            metadata["tier"] = tier
        if expires_at is not None:
            metadata["expires_at"] = expires_at

    def set_key_format_pattern(self, pattern: Pattern) -> None:
        """
        Set a regex pattern that valid API keys must match.

        Args:
            pattern: Regular expression pattern for API key validation
        """
        self.key_format_pattern = pattern

    def revoke_key(self, api_key: str) -> None:
        """
        Revoke a specific API key.

        Args:
            api_key: The API key to revoke
        """
        if api_key in self.valid_keys:
            self.revoked_keys.add(api_key)

    def validate_key(self, api_key: str) -> bool:
        """
        Validate an API key against all configured rules.

        Args:
            api_key: The API key to validate

        Returns:
            True if the key is valid, False otherwise
        """
        # Check if key is valid
        if api_key not in self.valid_keys:
            return False

        # Check if key has been revoked
        if api_key in self.revoked_keys:
            return False

        # Check key format if pattern is set
        if self.key_format_pattern and not self.key_format_pattern.match(api_key):
            return False

        # Check key expiration
        if api_key in self.key_metadata:
            expires_at = self.key_metadata[api_key].get("expires_at")
            if expires_at and datetime.now() > expires_at:
                return False

        return True
