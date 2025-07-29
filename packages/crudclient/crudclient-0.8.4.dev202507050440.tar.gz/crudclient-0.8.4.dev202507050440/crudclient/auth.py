"""Authentication strategies for CrudClient.

This module re-exports authentication strategies from the apiconfig library,
providing a unified interface for various authentication mechanisms.

Migration Notice
----------------
As of version 0.8.0, all authentication strategies have been migrated to use
the apiconfig library. This provides enhanced features like token validation,
expiration handling, and stricter input validation.

Available strategies
--------------------
- BearerAuth: For Bearer token authentication (OAuth 2.0, JWT tokens)
- BasicAuth: For HTTP Basic Authentication (username/password)
- ApiKeyAuth: For API key authentication (headers or query parameters)
- CustomAuth: For custom authentication mechanisms
- AuthStrategy: Base class for creating custom strategies
- AuthStrategyError: Exception for authentication-related errors

Breaking Changes
----------------
- BearerAuth now uses `access_token=` parameter instead of `token=`
- Empty credentials now raise AuthStrategyError instead of being silently accepted
- Custom header names are no longer supported in BearerAuth (use CustomAuth instead)

Examples
--------
```python
from crudclient.auth import BearerAuth, ApiKeyAuth, AuthStrategyError
from crudclient import ClientConfig, Client

# Bearer token authentication
auth_strategy = BearerAuth(access_token="your_access_token")

# API key authentication
api_auth = ApiKeyAuth(
    api_key="your_api_key",
    header_name="X-API-Key"
)

# Use it in your client configuration
config = ClientConfig(
    hostname="https://api.example.com",
    auth_strategy=auth_strategy
)
client = Client(config)

# Handle authentication errors
try:
    invalid_auth = BearerAuth(access_token="")
except AuthStrategyError as e:
    print(f"Authentication error: {e}")
```

Notes
-----
For detailed documentation on each strategy, see the apiconfig library documentation.
"""

from typing import Any, Literal, Optional, Tuple, Union, overload

from apiconfig.auth.base import AuthStrategy
from apiconfig.auth.strategies.api_key import ApiKeyAuth
from apiconfig.auth.strategies.basic import BasicAuth
from apiconfig.auth.strategies.bearer import BearerAuth
from apiconfig.auth.strategies.custom import CustomAuth
from apiconfig.exceptions.auth import AuthStrategyError


@overload
def create_auth_strategy(auth_type: Literal["bearer"], token: str) -> BearerAuth:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: Literal["basic"], token: str) -> BasicAuth:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: Literal["basic"], token: Tuple[str, str]) -> BasicAuth:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: Literal["none"], token: Any = None) -> None:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: str, token: None = None) -> None:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: str, token: Union[str, Tuple[str, str]]) -> AuthStrategy:  # noqa: E704
    ...


def create_auth_strategy(auth_type: str, token: Optional[Union[str, Tuple[str, str]]] = None) -> Optional[AuthStrategy]:
    """
    Create an authentication strategy based on the specified type.

    This function is provided for backward compatibility with the old-style configuration.
    It creates an appropriate AuthStrategy instance based on the auth_type and token.

    Parameters
    ----------
    auth_type : str
        The type of authentication to use. Can be "bearer", "basic", or "none".
    token : Optional[Union[str, Tuple[str, str]]], optional
        The token to use for authentication, if applicable.
        For basic auth, this can be either a string (username with empty password) or a tuple of (username, password).
        For bearer auth, this must be a string.

    Returns
    -------
    Optional[AuthStrategy]
        An instance of the appropriate AuthStrategy subclass, or None if auth_type is "none" or token is None.

    Raises
    ------
    ValueError
        If an unsupported auth_type is provided.
    TypeError
        If the token type doesn't match the requirements for the specified auth_type.
    """
    if auth_type == "none" or token is None:
        return None

    if auth_type == "bearer":
        if not isinstance(token, str):
            raise TypeError(f"Bearer auth token must be a string, got {type(token).__name__}")
        return BearerAuth(access_token=token)
    elif auth_type == "basic":
        if isinstance(token, tuple) and len(token) == 2:
            return BasicAuth(username=token[0], password=token[1])
        elif isinstance(token, str):
            return BasicAuth(username=token, password="")
        else:
            raise TypeError(f"Basic auth token must be a string or tuple, got {type(token).__name__}")

    if not isinstance(token, str):
        raise TypeError(f"Custom auth token must be a string, got {type(token).__name__}")
    return BearerAuth(access_token=token)


__all__ = ["AuthStrategy", "AuthStrategyError", "BearerAuth", "BasicAuth", "ApiKeyAuth", "CustomAuth", "create_auth_strategy"]
