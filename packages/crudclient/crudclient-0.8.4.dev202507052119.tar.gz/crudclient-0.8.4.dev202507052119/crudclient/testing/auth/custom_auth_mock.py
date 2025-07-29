"""
Custom authentication mock for testing.

This module provides a mock for Custom Authentication strategy with enhanced
validation capabilities for headers and parameters.
"""

import time
from typing import Callable, Dict, List, Optional, Tuple

from crudclient.auth import AuthStrategy, CustomAuth

from ..response_builder.response import MockResponse
from ..spy.enhanced import EnhancedSpyBase, FunctionSpy
from .base import AuthMockBase


# Inherit from both EnhancedSpyBase (for spying) and AuthMockBase (for auth mock state/config)
class CustomAuthMock(EnhancedSpyBase, AuthMockBase):
    """
    Mock for Custom Authentication strategy with enhanced capabilities.

    This class provides a configurable mock implementation of the Custom Authentication
    strategy, with support for header and parameter callbacks, validation, and error simulation.
    """

    def __init__(
        self, header_callback: Optional[Callable[[], Dict[str, str]]] = None, param_callback: Optional[Callable[[], Dict[str, str]]] = None
    ) -> None:
        """
        Initialize a Custom Authentication mock.

        Args:
            header_callback: Callback function that returns authentication headers
            param_callback: Callback function that returns authentication parameters
        """
        # Initialize both base classes
        EnhancedSpyBase.__init__(self)
        AuthMockBase.__init__(self)

        # --- Callback Handling with Spying ---
        # Store original callbacks separately if needed, wrap provided ones with FunctionSpy
        self._original_header_callback = header_callback
        self._original_param_callback = param_callback

        # Default callbacks if none provided
        def default_header_callback() -> Dict[str, str]:
            return {"X-Custom-Auth": "custom_value"}

        if header_callback is None and param_callback is None:
            self._original_header_callback = default_header_callback

        # Wrap callbacks with FunctionSpy
        self.header_callback_spy = FunctionSpy(self._original_header_callback, record_only=False) if self._original_header_callback else None
        # FunctionSpy records calls internally, no need to set .spy

        self.param_callback_spy = FunctionSpy(self._original_param_callback, record_only=False) if self._original_param_callback else None
        # FunctionSpy records calls internally, no need to set .spy

        # Use the spied callbacks (or lambdas if None) for the actual auth strategy
        safe_spied_header_callback: Callable[[], Dict[str, str]] = self.header_callback_spy if self.header_callback_spy else lambda: {}
        spied_param_callback = self.param_callback_spy if self.param_callback_spy else None

        self.auth_strategy = CustomAuth(header_callback=safe_spied_header_callback, param_callback=spied_param_callback)

        # Additional properties for enhanced functionality
        self.expected_headers: Dict[str, str] = {}
        self.expected_params: Dict[str, str] = {}
        self.required_headers: List[str] = []
        self.required_params: List[str] = []
        self.header_validators: Dict[str, Callable[[str], bool]] = {}
        self.param_validators: Dict[str, Callable[[str], bool]] = {}

    def with_header_callback(self, callback: Callable[[], Dict[str, str]]) -> "CustomAuthMock":
        """
        Set the header callback for the Custom Auth mock.

        Args:
            callback: Callback function that returns authentication headers

        Returns:
            Self for method chaining
        """
        self._original_header_callback = callback
        self.header_callback_spy = FunctionSpy(callback, record_only=False)
        # FunctionSpy records calls internally, no need to set .spy
        # Use the new spied callback
        spied_param_callback = self.param_callback_spy if self.param_callback_spy else None
        self.auth_strategy = CustomAuth(header_callback=self.header_callback_spy, param_callback=spied_param_callback)
        return self

    def with_param_callback(self, callback: Callable[[], Dict[str, str]]) -> "CustomAuthMock":
        """
        Set the parameter callback for the Custom Auth mock.

        Args:
            callback: Callback function that returns authentication parameters

        Returns:
            Self for method chaining
        """
        self._original_param_callback = callback
        self.param_callback_spy = FunctionSpy(callback, record_only=False)
        # FunctionSpy records calls internally, no need to set .spy
        # Use the new spied callback
        safe_spied_header_callback: Callable[[], Dict[str, str]] = self.header_callback_spy if self.header_callback_spy else lambda: {}
        self.auth_strategy = CustomAuth(header_callback=safe_spied_header_callback, param_callback=self.param_callback_spy)
        return self

    def with_expected_header(self, name: str, value: str) -> "CustomAuthMock":
        """
        Set an expected header for validation.

        Args:
            name: Header name
            value: Expected header value

        Returns:
            Self for method chaining
        """
        self.expected_headers[name] = value
        return self

    def with_expected_param(self, name: str, value: str) -> "CustomAuthMock":
        """
        Set an expected parameter for validation.

        Args:
            name: Parameter name
            value: Expected parameter value

        Returns:
            Self for method chaining
        """
        self.expected_params[name] = value
        return self

    def with_required_header(self, name: str) -> "CustomAuthMock":
        """
        Add a required header for validation.

        Args:
            name: Required header name

        Returns:
            Self for method chaining
        """
        if name not in self.required_headers:
            self.required_headers.append(name)
        return self

    def with_required_param(self, name: str) -> "CustomAuthMock":
        """
        Add a required parameter for validation.

        Args:
            name: Required parameter name

        Returns:
            Self for method chaining
        """
        if name not in self.required_params:
            self.required_params.append(name)
        return self

    def with_header_validator(self, name: str, validator: Callable[[str], bool]) -> "CustomAuthMock":
        """
        Add a custom validator for a header.

        Args:
            name: Header name
            validator: Function that validates the header value

        Returns:
            Self for method chaining
        """
        self.header_validators[name] = validator
        return self

    def with_param_validator(self, name: str, validator: Callable[[str], bool]) -> "CustomAuthMock":
        """
        Add a custom validator for a parameter.

        Args:
            name: Parameter name
            validator: Function that validates the parameter value

        Returns:
            Self for method chaining
        """
        self.param_validators[name] = validator
        return self

    def verify_headers(self, headers: Dict[str, str]) -> bool:
        """
        Verify that the headers meet all requirements.

        Args:
            headers: The headers to verify

        Returns:
            True if the headers are valid, False otherwise
        """
        # Record the call to this verification method
        start_time = time.time()
        result = False
        exception = None
        try:
            result = True  # Assume true initially
            # Check required headers
            for name in self.required_headers:
                if name not in headers:
                    result = False
                    break
            if not result:
                return False  # Early exit

            # Check expected header values
            for name, expected_value in self.expected_headers.items():
                if name not in headers or headers[name] != expected_value:
                    result = False
                    break
            if not result:
                return False  # Early exit

            # Apply custom validators
            for name, validator in self.header_validators.items():
                if name in headers and not validator(headers[name]):
                    result = False
                    break
            if not result:
                return False  # Early exit

            return result  # Return the final result
        except Exception as e:
            exception = e
            raise
        finally:
            duration = time.time() - start_time
            self._record_call(method_name="verify_headers", args=(headers,), kwargs={}, result=result, exception=exception, duration=duration)

    def verify_params(self, params: Dict[str, str]) -> bool:
        """
        Verify that the parameters meet all requirements.

        Args:
            params: The parameters to verify

        Returns:
            True if the parameters are valid, False otherwise
        """
        start_time = time.time()
        result = True  # Assume success initially
        exception = None
        try:
            # Check required parameters
            for name in self.required_params:
                if name not in params:
                    result = False
                    break  # Exit loop on first failure
            if not result:
                return False  # Return early

            # Check expected parameter values
            for name, expected_value in self.expected_params.items():
                if name not in params or params[name] != expected_value:
                    result = False
                    break  # Exit loop on first failure
            if not result:
                return False  # Return early

            # Apply custom validators
            for name, validator in self.param_validators.items():
                if name in params and not validator(params[name]):
                    result = False
                    break  # Exit loop on first failure
            if not result:
                return False  # Return early

            # If we reach here, all checks passed
            return True

        except Exception as e:
            exception = e
            result = False  # Verification failed due to exception
            raise  # Re-raise the exception after recording
        finally:
            # Record the call regardless of outcome
            duration = time.time() - start_time
            # Result is False if any check failed or an exception occurred
            final_result = result and exception is None
            self._record_call(method_name="verify_params", args=(params,), kwargs={}, result=final_result, exception=exception, duration=duration)
            # If an exception occurred, the raise above will propagate it.
            # If no exception, the return value from the try block (or early return) is used.

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured CustomAuth strategy
        """
        return self.auth_strategy

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers for the current token.

        Returns:
            None for CustomAuthMock as headers are applied via callbacks
        """
        # Headers are applied via the header_callback in the actual strategy.
        # This method signature in the mock base doesn't perfectly align.
        return None

    def handle_auth_error(self, response: MockResponse) -> bool:
        """
        Handle authentication errors.

        Args:
            response: The error response that triggered the auth error

        Returns:
            False as no standard refresh mechanism is defined for custom auth
        """
        # No standard refresh mechanism defined for generic custom auth mock
        return False
