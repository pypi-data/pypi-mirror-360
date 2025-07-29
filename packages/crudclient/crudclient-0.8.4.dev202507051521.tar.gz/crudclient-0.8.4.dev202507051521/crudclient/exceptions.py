"""
Exception classes for crudclient.

Uses apiconfig exceptions directly via protocol support.
ApiConfig accepts requests.Request/Response objects natively.
"""

from typing import Any, Optional

# Import all apiconfig exceptions directly
from apiconfig.exceptions import APIConfigError as CrudClientError
from apiconfig.exceptions import (
    AuthenticationError,
    ConfigurationError,
)
from apiconfig.exceptions.http import ApiClientBadRequestError as BadRequestError
from apiconfig.exceptions.http import ApiClientConflictError as ConflictError
from apiconfig.exceptions.http import ApiClientError as APIError
from apiconfig.exceptions.http import ApiClientForbiddenError as ForbiddenError
from apiconfig.exceptions.http import (
    ApiClientInternalServerError as InternalServerError,
)
from apiconfig.exceptions.http import ApiClientNotFoundError as NotFoundError
from apiconfig.exceptions.http import ApiClientRateLimitError as RateLimitError
from apiconfig.exceptions.http import (
    ApiClientUnauthorizedError as ClientAuthenticationError,
)
from apiconfig.exceptions.http import (
    ApiClientUnprocessableEntityError as UnprocessableEntityError,
)
from apiconfig.exceptions.http import (
    create_api_client_error,
)
from pydantic import ValidationError as PydanticValidationError

# CrudClient-specific exceptions that apiconfig doesn't provide


class ClientInitializationError(ConfigurationError):
    """Error specifically during the initialization phase of the HTTP client.

    Raised when the client object cannot be instantiated.
    """


class InvalidClientError(ConfigurationError):
    """Error when operation requires a client but none is available."""


class NetworkError(CrudClientError):
    """Network connectivity error.

    Uses __cause__ for exception chaining instead of storing attributes.
    """

    def __init__(self, message: str, original_exception: Exception):
        super().__init__(message)
        self.original_exception = original_exception
        self.__cause__ = original_exception


class DataValidationError(CrudClientError):
    """Error related to data validation.

    Uses __cause__ for pydantic error chaining.
    """

    def __init__(
        self,
        message: str,
        data: Any,
        pydantic_error: Optional[PydanticValidationError] = None,
    ) -> None:
        # Include data info in message
        super().__init__(f"{message} (data type: {type(data).__name__})")
        self.data = data
        self.pydantic_error = pydantic_error
        if pydantic_error:
            self.__cause__ = pydantic_error


class ModelConversionError(CrudClientError):
    """Error converting response to model."""


class ResponseParsingError(CrudClientError):
    """Error parsing response.

    Uses __cause__ for original exception chaining.
    """

    def __init__(self, message: str, original_exception: Exception, response: Any = None):
        super().__init__(message)
        self.original_exception = original_exception
        self.response = response
        self.__cause__ = original_exception


class MultipleResourcesFoundError(NotFoundError):
    """Multiple resources found when expecting one.

    Inherits from NotFoundError for compatibility with error handling
    that catches NotFoundError.
    """


class DeprecatedEndpointError(CrudClientError):
    """Endpoint is deprecated and should not be used."""


# Temporary compatibility mapping
ServiceUnavailableError = InternalServerError

__all__ = [
    # Base exceptions
    "CrudClientError",
    "AuthenticationError",
    "ConfigurationError",
    "APIError",
    # HTTP status exceptions
    "BadRequestError",
    "ClientAuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    # CrudClient specific
    "ClientInitializationError",
    "InvalidClientError",
    "NetworkError",
    "DataValidationError",
    "ModelConversionError",
    "ResponseParsingError",
    "MultipleResourcesFoundError",
    "DeprecatedEndpointError",
    "ServiceUnavailableError",
    # Factory function
    "create_api_client_error",
]
