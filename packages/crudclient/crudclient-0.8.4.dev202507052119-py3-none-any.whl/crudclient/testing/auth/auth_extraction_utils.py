"""
Authentication extraction utilities for testing.

This module provides helper methods for extracting authentication information
from headers and tokens.
"""

import base64
import json
from typing import Any, Dict, Tuple, cast


class AuthExtractionUtils:
    """
    Helper methods for extracting authentication information.

    This class provides static methods for extracting credentials, tokens,
    and JWT payloads from authentication headers and tokens.
    """

    @staticmethod
    def extract_basic_auth_credentials(header_value: str) -> Tuple[str, str]:
        """
        Extract username and password from a Basic Auth header.

        Args:
            header_value: The value of the Authorization header

        Returns:
            A tuple of (username, password)

        Raises:
            ValueError: If the header is not a valid Basic Auth header
        """
        if not header_value.startswith("Basic "):
            raise ValueError("Not a Basic Auth header")

        try:
            # Extract the base64-encoded credentials
            encoded_credentials = header_value[6:]  # Skip "Basic "
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")

            # Split into username and password
            if ":" not in decoded_credentials:
                raise ValueError("Invalid Basic Auth format")

            username, password = decoded_credentials.split(":", 1)
            return username, password
        except Exception as e:
            raise ValueError(f"Invalid Basic Auth header: {str(e)}")

    @staticmethod
    def extract_bearer_token(header_value: str) -> str:
        """
        Extract token from a Bearer Auth header.

        Args:
            header_value: The value of the Authorization header

        Returns:
            The Bearer token

        Raises:
            ValueError: If the header is not a valid Bearer Auth header
        """
        if not header_value.startswith("Bearer "):
            raise ValueError("Not a Bearer Auth header")

        # Extract the token
        token = header_value[7:]  # Skip "Bearer "
        if not token:
            raise ValueError("Empty Bearer token")

        return token

    @staticmethod
    def extract_jwt_payload(token: str) -> Dict[str, Any]:
        """
        Extract and decode the payload from a JWT token.

        Args:
            token: The JWT token

        Returns:
            The decoded JWT payload as a dictionary

        Raises:
            ValueError: If the token is not a valid JWT
            TypeError: If the provided token is not a string
        """
        if not isinstance(token, str):
            raise TypeError(f"Expected token to be a string, but got {type(token).__name__}")

        # Split the token into parts
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Not a valid JWT token")

        try:
            # Decode the payload (second part)
            payload_base64 = parts[1]

            # Add padding if needed
            padding = len(payload_base64) % 4
            if padding:
                payload_base64 += "=" * (4 - padding)

            # Decode and parse as JSON
            payload_json = base64.b64decode(payload_base64).decode("utf-8")
            return cast(Dict[str, Any], json.loads(payload_json))
        except Exception as e:
            raise ValueError(f"Invalid JWT payload: {str(e)}")
