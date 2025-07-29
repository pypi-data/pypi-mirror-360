"""
Specific utilities for verifying authentication error responses and headers.

This module provides the `AuthErrorVerification` class containing static methods
focused on checking the structure and content of common authentication-related
error response bodies and standard rate limit headers.

These methods are typically used internally by higher-level verification helpers
(e.g., those in `apiconfig.testing.auth_verification`) or can be used directly for fine-grained checks.
They raise `VerificationError` upon failure.
"""

from typing import Any, Dict, Optional

from ..exceptions import VerificationError  # Import VerificationError


class AuthErrorVerification:
    """
    Provides static methods focused on verifying auth error responses and rate limits.

    Contains specific checks for the content of error response bodies and the
    presence/values of standard rate limit headers.
    Methods raise `VerificationError` if checks fail.
    """

    @staticmethod
    def verify_auth_error_response(
        response: Dict[str, Any], expected_status: int = 401, expected_error: Optional[str] = None, expected_error_description: Optional[str] = None
    ) -> None:
        """
        Verify the structure and content of an authentication error response body.

        Checks if the `response` dictionary (representing the parsed JSON body)
        contains expected keys (like 'status', 'error', 'error_description') and
        if their values match the provided expected values.

        Args:
            response: The dictionary representing the parsed JSON error response body.
            expected_status: The expected HTTP status code (often checked separately,
                             but can be verified if present in the response body, e.g., response['status']).
                             Defaults to 401.
            expected_error: Optional expected value for the 'error' field (e.g., "invalid_token").
            expected_error_description: Optional expected value for the 'error_description' field.

        Raises:
            VerificationError: If the response structure is incorrect or if provided
                               expected values do not match the actual values in the response.

        Example:
            >>> error_resp = {"status": 401, "error": "invalid_request", "error_description": "Missing credentials"}
            >>> AuthErrorVerification.verify_auth_error_response(error_resp, expected_status=401, expected_error="invalid_request")
            >>> try:
            ...     AuthErrorVerification.verify_auth_error_response(error_resp, expected_error="invalid_token")
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        # Check status code
        if "status_code" in response:
            if response["status_code"] != expected_status:
                raise VerificationError(f"Expected status code {expected_status}, got {response['status_code']}")

        # Check error code
        if expected_error and "error" in response:
            if response["error"] != expected_error:
                raise VerificationError(f"Expected error code '{expected_error}', got '{response['error']}'")

        # Check error description
        if expected_error_description and "error_description" in response:
            if response["error_description"] != expected_error_description:
                raise VerificationError(f"Expected error description '{expected_error_description}', got '{response['error_description']}'")

    @staticmethod
    def verify_rate_limit_headers(
        headers: Dict[str, str], expected_limit: Optional[int] = None, expected_remaining: Optional[int] = None, expected_reset: Optional[int] = None
    ) -> None:
        """
        Verify the presence and optionally the values of standard rate limit headers.

        Checks for headers like 'X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset'.
        If expected values are provided, compares them against the header values (after
        converting header values to integers).

        Args:
            headers: Dictionary of response headers (case-insensitive keys recommended).
            expected_limit: Optional integer value for 'X-RateLimit-Limit'.
            expected_remaining: Optional integer value for 'X-RateLimit-Remaining'.
            expected_reset: Optional integer value for 'X-RateLimit-Reset' (Unix timestamp).

        Raises:
            VerificationError: If a header corresponding to an expected value is missing,
                               cannot be parsed as an integer, or does not match the
                               provided expected value.

        Example:
            >>> rate_limit_headers = {"X-RateLimit-Limit": "100", "X-RateLimit-Remaining": "99", "X-RateLimit-Reset": "1678886400"}
            >>> AuthErrorVerification.verify_rate_limit_headers(rate_limit_headers, expected_limit=100, expected_remaining=99)
            >>> try:
            ...     AuthErrorVerification.verify_rate_limit_headers(rate_limit_headers, expected_limit=50)
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
            >>> try: # Check for missing header if expectation is set
            ...     AuthErrorVerification.verify_rate_limit_headers({"X-RateLimit-Limit": "100"}, expected_remaining=99)
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        # Check for standard rate limit headers
        rate_limit_headers = {"X-RateLimit-Limit": expected_limit, "X-RateLimit-Remaining": expected_remaining, "X-RateLimit-Reset": expected_reset}

        for header, expected_value in rate_limit_headers.items():
            if expected_value is not None:
                if header not in headers:
                    raise VerificationError(f"Missing rate limit header: {header}")

                try:
                    actual_value = int(headers[header])
                    if actual_value != expected_value:
                        raise VerificationError(f"Expected {header} to be {expected_value}, got {actual_value}")
                except ValueError:
                    raise VerificationError(f"Rate limit header {header} is not an integer: {headers[header]}")
