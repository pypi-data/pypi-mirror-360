"""
Mock authentication implementations for the crudclient testing framework.

This module provides mock implementations of the authentication strategies,
including Basic, Bearer, API Key, and Custom auth, along with factory functions
and verification helpers.
"""

from .api_key import ApiKeyAuthMock
from .base import AuthMockBase
from .basic import BasicAuthMock
from .bearer import BearerAuthMock
from .custom import CustomAuthMock, OAuthMock
from .factory import (
    create_api_key_auth_mock,
    create_basic_auth_mock,
    create_bearer_auth_mock,
    create_custom_auth_mock,
    create_oauth_mock,
)

__all__ = [
    # Base class
    "AuthMockBase",
    # Auth mock classes
    "BasicAuthMock",
    "BearerAuthMock",
    "ApiKeyAuthMock",
    "CustomAuthMock",
    "OAuthMock",
    # Factory functions
    "create_basic_auth_mock",
    "create_bearer_auth_mock",
    "create_api_key_auth_mock",
    "create_custom_auth_mock",
    "create_oauth_mock",
]
