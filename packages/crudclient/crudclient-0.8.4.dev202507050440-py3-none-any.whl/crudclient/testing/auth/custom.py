"""
Custom authentication mock for testing.

This module provides mocks for Custom Authentication strategies with support
for OAuth grant types, scopes, and advanced authentication scenarios.
"""

from .custom_auth_mock import CustomAuthMock

# Re-export the classes from their respective modules
from .oauth_mock import OAuthMock

__all__ = ["OAuthMock", "CustomAuthMock"]
