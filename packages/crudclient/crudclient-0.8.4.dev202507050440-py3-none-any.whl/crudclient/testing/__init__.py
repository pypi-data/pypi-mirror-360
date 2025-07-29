"""
Testing utilities for the crudclient library.

This module provides a framework for creating test doubles (mocks, stubs, fakes, spies)
for the crudclient library components (Client, API, CRUD, Auth, HTTPClient).
"""

from .auth import (
    ApiKeyAuthMock,
    AuthMockBase,
    BasicAuthMock,
    BearerAuthMock,
    CustomAuthMock,
    OAuthMock,
    create_api_key_auth_mock,
    create_basic_auth_mock,
    create_bearer_auth_mock,
    create_custom_auth_mock,
    create_oauth_mock,
)
from .core.client import MockClient
from .core.http_client import MockHTTPClient
from .doubles import DataStore, FakeAPI

# Import directly from the module file
from .exceptions import FakeAPIError  # Import separately
from .exceptions import (
    AuthStrategyError,
    CRUDOperationError,
    DataStoreError,
    MockConfigurationError,
    RequestNotConfiguredError,
    ResourceNotFoundError,
    SpyError,
    TestingError,
    VerificationError,
)
from .factory import MockClientFactory  # Corrected import path
from .response_builder import ResponseBuilder  # Import ResponseBuilder
from .response_builder.api_patterns import APIPatternBuilder  # Import APIPatternBuilder
from .response_builder.response import (
    MockResponse,  # Import MockResponse from response_builder
)
from .spy import MethodCall, SpyBase
from .verification import Verifier

__all__ = [
    # Main classes
    "MockClient",
    "MockHTTPClient",
    "MockClientFactory",
    "Verifier",
    "FakeAPI",
    "DataStore",
    "MethodCall",
    "SpyBase",
    "MockResponse",
    "APIPatternBuilder",
    "ResponseBuilder",
    # Auth mocks
    "ApiKeyAuthMock",
    "AuthMockBase",
    "BasicAuthMock",
    "BearerAuthMock",
    "CustomAuthMock",
    "OAuthMock",
    "create_api_key_auth_mock",
    "create_basic_auth_mock",
    "create_bearer_auth_mock",
    "create_custom_auth_mock",
    "create_oauth_mock",
    # Exceptions
    "TestingError",
    "MockConfigurationError",
    "VerificationError",
    "RequestNotConfiguredError",
    "AuthStrategyError",
    "CRUDOperationError",
    "DataStoreError",
    "ResourceNotFoundError",
    "SpyError",
    "FakeAPIError",  # Ensure FakeAPIError is in __all__
]
