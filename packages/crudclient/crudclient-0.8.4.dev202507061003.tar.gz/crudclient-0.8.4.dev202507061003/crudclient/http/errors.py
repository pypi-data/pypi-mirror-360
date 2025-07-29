"""Error Handling Module for CrudClient.

This module provides centralized error handling functionality for the CrudClient library.
It contains classes and functions for processing HTTP error responses and mapping them
to appropriate exceptions.

Classes
-------
- ErrorHandler: Centralizes error processing logic for HTTP responses.
"""

import logging
from typing import Any, Dict, Type, cast

import requests

# First-party imports grouped and sorted
from ..exceptions import (
    APIError,
    BadRequestError,
    ClientAuthenticationError,
    ConflictError,
    CrudClientError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralizes error processing logic for HTTP responses.

    This class provides methods for handling error responses from API calls,
    extracting error information, and raising appropriate exceptions based on
    status codes.

    Attributes
    ----------
    status_code_to_exception (Dict[int, Type[CrudClientError]]): Mapping of HTTP status
        codes to exception types.
    """

    def __init__(self) -> None:
        """Initialize the ErrorHandler with default status code to exception mappings."""
        self.status_code_to_exception: Dict[int, Type[CrudClientError]] = {
            400: BadRequestError,
            401: ClientAuthenticationError,  # Changed
            403: ForbiddenError,
            404: NotFoundError,
            409: ConflictError,  # Added
            422: UnprocessableEntityError,  # Changed
            429: RateLimitError,  # Added
            500: InternalServerError,
            # 502: APIError, # Removed
            503: ServiceUnavailableError,
        }

    def handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses from the API.

        This method attempts to extract error information from the response and raises
        appropriate exceptions based on the status code.

        Parameters
        ----------
        response : requests.Response
            The response object from the API.

        Raises
        ------
        AuthenticationError
            If the status code is 401 (Unauthorized) or 403 (Forbidden).
        NotFoundError
            If the status code is 404 (Not Found).
        DataValidationError
            If the status code is 422 (Unprocessable Entity).
        CrudClientError
            For other error status codes.
        TypeError
            If response is not a requests.Response object.
        """
        # Check if response is a valid Response object or a mock of one
        is_response = isinstance(response, requests.Response)
        is_response_mock = hasattr(response, "_mock_spec") and requests.Response in getattr(response, "_mock_spec", [])

        if not (is_response or is_response_mock):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        try:
            error_data = response.json()
        except requests.exceptions.JSONDecodeError as json_err:
            logger.warning(
                "Failed to parse JSON from error response: %s",
                json_err,
                exc_info=True,
            )
            error_data = response.text

        status_code = response.status_code
        logger.error(
            "HTTP error occurred: Status Code: %s, Response Body: %s",
            status_code,
            error_data,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            exception_class = self.status_code_to_exception.get(status_code, APIError)

            error_message = f"HTTP error {status_code}: {error_data}"

            # No specific elif needed for UnprocessableEntityError, handled by issubclass(APIError)
            if issubclass(exception_class, APIError):  # Handles ClientAuthenticationError, UnprocessableEntityError, etc.
                # Cast to Any to handle protocol mismatch - apiconfig will extract what it needs
                raise exception_class(error_message, request=cast(Any, response.request), response=cast(Any, response)) from e
            else:  # Handle non-APIError custom exceptions if registered
                logger.warning("Status code %s mapped to non-APIError subclass %s.", status_code, exception_class.__name__)
                # Attempt to raise with standard APIError args, might fail if signature differs
                try:
                    # Base CrudClientError only takes message
                    raise exception_class(error_message) from e
                except TypeError:
                    logger.error(
                        "Failed to instantiate custom non-APIError %s with standard args. Falling back to APIError.",
                        exception_class.__name__,
                        exc_info=True,
                    )
                    # Fallback to generic APIError
                    # Cast to Any to handle protocol mismatch - apiconfig will extract what it needs
                    raise APIError(error_message, request=cast(Any, response.request), response=cast(Any, response)) from e

        logger.warning("Error handler reached end without raising specific exception for status %s.", status_code)
        # Cast to Any to handle protocol mismatch - apiconfig will extract what it needs
        raise APIError(
            f"Request failed with status code {status_code}: {error_data}",
            request=cast(Any, response.request),
            response=cast(Any, response),
        )

    def register_status_code_handler(self, status_code: int, exception_class: Type[CrudClientError]) -> None:
        """Register a custom exception handler for a specific HTTP status code.

        This allows users to override or extend the default behavior for handling
        specific HTTP error codes by providing their own CrudClientError subclass.

        Parameters
        ----------
        status_code : int
            The integer HTTP status code (e.g., 409).
        exception_class : Type[CrudClientError]
            The subclass of CrudClientError to be raised when this status code is encountered.

        Raises
        ------
        TypeError
            If `status_code` is not an integer or if `exception_class`
            is not a type or not a subclass of `CrudClientError`.

        Example
        -------
        >>> class ConflictError(APIError):
        ...     pass
        ...
        >>> error_handler = ErrorHandler()
        >>> error_handler.register_status_code_handler(409, ConflictError)
        """
        if not isinstance(status_code, int):
            raise TypeError(f"status_code must be an integer, got {type(status_code).__name__}")

        if not isinstance(exception_class, type) or not issubclass(exception_class, CrudClientError):
            raise TypeError("exception_class must be a subclass of CrudClientError, got " f"{type(exception_class).__name__}")
        if not issubclass(exception_class, APIError):
            logger.warning(
                "Registering non-APIError subclass %s for status code %s. " "Ensure its signature matches usage in handle_error_response.",
                exception_class.__name__,
                status_code,
            )

        self.status_code_to_exception[status_code] = exception_class
