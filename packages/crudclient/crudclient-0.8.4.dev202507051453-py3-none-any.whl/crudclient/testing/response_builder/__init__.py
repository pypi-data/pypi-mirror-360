from typing import Dict, Optional

from .response import MockResponse


class ResponseBuilder:
    """
    Utility class for creating common API error responses.

    Provides static methods to generate standardized mock responses for common
    API error scenarios like validation errors, rate limiting, and authentication failures.
    """

    @staticmethod
    def create_validation_error(
        fields: Optional[Dict[str, str]] = None,
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
    ) -> MockResponse:
        """
        Create a mock response for a validation error.

        Generates a standardized validation error response with field-specific error messages,
        following common REST API error patterns.

        Args:
            fields: Dictionary mapping field names to error messages
            status_code: HTTP status code for the response (typically 422 Unprocessable Entity)
            error_code: Error code identifier
            message: General error message

        Returns:
            A MockResponse instance with validation error details
        """
        if fields is None:
            fields = {"field": "Invalid value"}

        data = {"error": {"code": error_code, "message": message, "fields": fields}}

        return MockResponse(status_code=status_code, json_data=data, headers={"Content-Type": "application/json"})

    @staticmethod
    def create_rate_limit_error(
        limit: int = 100,
        remaining: int = 0,
        reset_seconds: int = 60,
        status_code: int = 429,
    ) -> MockResponse:
        """
        Create a mock response for a rate limit exceeded error.

        Generates a standardized rate limit error response with appropriate headers
        indicating limits, remaining requests, and reset time.

        Args:
            limit: Maximum number of requests allowed in the time window
            remaining: Number of requests remaining in the current time window
            reset_seconds: Seconds until the rate limit resets
            status_code: HTTP status code (typically 429 Too Many Requests)

        Returns:
            A MockResponse instance with rate limit error details and headers
        """
        data = {"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded. Please try again later."}}

        headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_seconds),
        }

        return MockResponse(status_code=status_code, json_data=data, headers=headers)

    @staticmethod
    def create_auth_error(error_type: str = "invalid_token", status_code: int = 401) -> MockResponse:
        """
        Create a mock response for an authentication error.

        Generates a standardized authentication error response. The response includes:
        - A `WWW-Authenticate` header with the format:
          `Bearer realm="api", error="{error_type}", error_description="{message}"`
        - A JSON body with the structure:
          `{"error": {"code": error_type.upper(), "message": message}}`

        Args:
            error_type: Type of authentication error. Supported values:
                        "invalid_token", "invalid_credentials", "missing_credentials",
                        "insufficient_scope", "mfa_required"
            status_code: HTTP status code (typically 401 Unauthorized)

        Returns:
            A MockResponse instance with authentication error details and headers
        """
        error_messages = {
            "invalid_token": "The access token is invalid or has expired",
            "invalid_credentials": "Invalid username or password",
            "missing_credentials": "Authentication credentials were not provided",
            "insufficient_scope": "The access token does not have the required scope",
            "mfa_required": "Multi-factor authentication is required",
        }

        message = error_messages.get(error_type, "Authentication failed")

        data = {"error": {"code": error_type.upper(), "message": message}}

        headers = {"Content-Type": "application/json", "WWW-Authenticate": f'Bearer error="{error_type}", error_description="{message}"'}

        return MockResponse(status_code=status_code, json_data=data, headers=headers)
