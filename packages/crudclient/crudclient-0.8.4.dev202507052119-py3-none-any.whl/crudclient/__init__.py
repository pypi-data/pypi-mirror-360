"""CrudClient Library.

A flexible and extensible client library for interacting with RESTful APIs.

This library provides a set of classes and utilities for building API clients
that follow the CRUD (Create, Read, Update, Delete) pattern. It includes support
for authentication, error handling, and data validation.

Main Components
---------------
- API: Base class for creating API clients with CRUD resources.
- Client: HTTP client for making API requests.
- ClientConfig: Configuration for the client.
- Crud: Base class for CRUD operations on API resources.
- ResourceGroup: Base class for grouping related CRUD resources and other ResourceGroups.
- AuthStrategy: Base class for authentication strategies.

Example
-------
```python
from crudclient import API, ClientConfig, ResourceGroup, Crud
from crudclient.auth import BearerAuth

class UsersCrud(Crud):
    _resource_path = "users"
    _datamodel = User

class PostsCrud(Crud):
    _resource_path = "posts"
    _datamodel = Post

class UserGroup(ResourceGroup[User]):
    _resource_path = "users"
    _datamodel = User

    def _register_child_endpoints(self):
        self.posts = PostsCrud(self.client, parent=self)

class MyAPI(API):
    def _register_endpoints(self) -> None:
        self.users = UsersCrud(self.client)

    def _register_groups(self) -> None:
        self.user_group = UserGroup(self.client)

# Create a configuration with bearer token authentication
config = ClientConfig(
    hostname="https://api.example.com",
    auth_strategy=BearerAuth(access_token="your_token")
)

# Initialize the API client
api = MyAPI(client_config=config)

# Use the API client
users = api.users.list()
# Or use resource groups for nested resources
user_posts = api.user_group.posts.list()
```
"""

import logging
from importlib.metadata import version

from apiconfig.utils.logging import setup_logging

from .api import API
from .auth import (
    ApiKeyAuth,
    AuthStrategy,
    AuthStrategyError,
    BasicAuth,
    BearerAuth,
    CustomAuth,
)
from .client import Client
from .config import ClientConfig
from .crud import Crud
from .exceptions import (
    ConfigurationError,  # Replaced ClientInitializationError, InvalidClientError
)
from .exceptions import DataValidationError  # Replaced ModelConversionError
from .exceptions import UnprocessableEntityError  # Replaced InvalidResponseError
from .exceptions import (  # Updated imports
    APIError,
    AuthenticationError,
    BadRequestError,
    ClientAuthenticationError,
    ConflictError,
    CrudClientError,
    ForbiddenError,
    InternalServerError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ResponseParsingError,
    ServiceUnavailableError,
)
from .groups import ResourceGroup
from .models import ApiResponse
from .types import JSONDict, JSONList, RawResponse

# Set up logging for the library.
# By default, the library will not emit any logs.
# It's up to the consuming application to configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__all__ = [  # Updated __all__
    "API",
    "Client",
    "ClientConfig",
    "Crud",
    "ResourceGroup",
    # Authentication classes
    "AuthStrategy",
    "AuthStrategyError",
    "BearerAuth",
    "BasicAuth",
    "ApiKeyAuth",
    "CustomAuth",
    # Exception classes
    "APIError",
    "ConfigurationError",  # Replaced InvalidClientError, ClientInitializationError
    "CrudClientError",
    "AuthenticationError",
    "NotFoundError",
    "UnprocessableEntityError",  # Replaced InvalidResponseError
    "DataValidationError",  # Replaced ModelConversionError
    "NetworkError",
    "ResponseParsingError",
    # Specific API Errors (optional to export all, but good for discoverability)
    "BadRequestError",
    "ClientAuthenticationError",
    "ForbiddenError",
    "ConflictError",
    "RateLimitError",
    "InternalServerError",
    "ServiceUnavailableError",
    # Models and types
    "ApiResponse",
    "JSONDict",
    "JSONList",
    "RawResponse",
    "setup_logging",
]

__version__ = version("crudclient")
