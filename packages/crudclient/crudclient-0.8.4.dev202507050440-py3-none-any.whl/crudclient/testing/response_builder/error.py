"""
Error response builder utilities for mock client.

This module provides utilities for creating various types of error responses
commonly encountered in API interactions, such as validation errors,
rate limit errors, and authentication errors.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .basic import BasicResponseBuilder
from .response import MockResponse


class ErrorResponseBuilder:
    """
    Builder for creating standardized API error responses.

    This class provides static methods for generating various types of error responses
    that follow common API error patterns, including validation errors, rate limiting,
    and authentication errors.
    """

    @staticmethod
    def create_error_response(
        status_code: int = 400,
        message: str = "Bad Request",
        error_code: str = "BAD_REQUEST",
        details: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        """
        Create a standardized error response.

        Generates an error response with a consistent structure including message,
        error code, optional details, and a request ID for tracking.

        Args:
            status_code: HTTP status code for the error response
            message: Human-readable error message
            error_code: Machine-readable error code identifier
            details: Additional error details, typically for field-level errors
            request_id: Unique identifier for the request (generated if not provided)
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse instance representing an error response
        """
        error: Dict[str, Any] = {
            "message": message,
            "code": error_code,
        }

        if details:
            error["details"] = details

        if request_id:
            error["request_id"] = request_id
        else:
            error["request_id"] = str(uuid.uuid4())

        errors = [error]

        response_headers = {
            "Content-Type": "application/json",
        }

        # Add common error headers
        if status_code == 429:
            retry_after = random.randint(30, 120)
            response_headers["Retry-After"] = str(retry_after)
            response_headers["X-RateLimit-Reset"] = str(int((datetime.now() + timedelta(seconds=retry_after)).timestamp()))

        # Merge with custom headers if provided
        if headers:
            response_headers.update(headers)

        return BasicResponseBuilder.create_response(status_code=status_code, errors=errors, headers=response_headers)

    @staticmethod
    def create_validation_error(
        fields: Dict[str, str],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
    ) -> MockResponse:
        """
        Create a validation error response with field-specific error messages.

        Generates a structured validation error response that includes specific
        error messages for each invalid field.

        Args:
            fields: Dictionary mapping field names to error messages
            status_code: HTTP status code (defaults to 422 Unprocessable Entity)
            error_code: Machine-readable error code identifier
            message: Human-readable error message

        Returns:
            A MockResponse instance representing a validation error
        """
        details = []
        for field, error_msg in fields.items():
            details.append({"field": field, "message": error_msg, "code": "INVALID_FIELD"})

        return ErrorResponseBuilder.create_error_response(status_code=status_code, message=message, error_code=error_code, details=details)

    @staticmethod
    def create_rate_limit_error(
        limit: int = 100,
        remaining: int = 0,
        reset_seconds: int = 60,
    ) -> MockResponse:
        """
        Create a rate limit exceeded error response.

        Generates a rate limiting error response with appropriate headers
        indicating limits, remaining requests, and reset time.

        Args:
            limit: Maximum number of requests allowed in the time window
            remaining: Number of requests remaining in the current window
            reset_seconds: Seconds until the rate limit resets

        Returns:
            A MockResponse instance representing a rate limit error with
            appropriate rate limiting headers
        """
        reset_time = int((datetime.now() + timedelta(seconds=reset_seconds)).timestamp())

        headers = {
            "Content-Type": "application/json",
            "Retry-After": str(reset_seconds),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }

        return ErrorResponseBuilder.create_error_response(
            status_code=429,
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            details=[{"limit": limit, "remaining": remaining, "reset": reset_time}],
            request_id=str(uuid.uuid4()),
            headers=headers,
        )

    @staticmethod
    def create_auth_error(
        error_type: str = "invalid_token",
        status_code: int = 401,
    ) -> MockResponse:
        """
        Create an authentication error response.

        Generates an authentication error response with appropriate WWW-Authenticate
        headers based on the specified error type.

        Args:
            error_type: Type of authentication error (e.g., "invalid_token",
                           "expired_token", "insufficient_scope")
            status_code: HTTP status code (defaults to 401 Unauthorized)

        Returns:
            A MockResponse instance representing an authentication error with
            appropriate WWW-Authenticate headers
        """
        error_messages = {
            "invalid_token": "The access token is invalid",
            "expired_token": "The access token has expired",
            "insufficient_scope": "The access token does not have the required scope",
            "invalid_client": "Client authentication failed",
            "invalid_grant": "The provided authorization grant is invalid",
            "unauthorized_client": "The client is not authorized to use this grant type",
        }

        message = error_messages.get(error_type, "Authentication failed")

        headers = {"Content-Type": "application/json", "WWW-Authenticate": f'Bearer realm="api", error="{error_type}", error_description="{message}"'}

        return ErrorResponseBuilder.create_error_response(status_code=status_code, message=message, error_code=error_type.upper(), headers=headers)
