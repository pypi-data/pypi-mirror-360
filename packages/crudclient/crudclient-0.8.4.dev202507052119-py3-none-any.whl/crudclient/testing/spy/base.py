"""Base components for the Test Spy pattern.

This module defines ``SpyBase`` which provides the core functionality for
recording method calls in test doubles.
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

from ..exceptions import SpyError
from .method_call import MethodCall


class SpyBase:
    """Base implementation for the **Test Spy pattern**.

    A Test Spy records information about how it was called during test
    execution.  Concrete spy classes should inherit from this base to leverage
    the call recording and verification infrastructure provided here.
    """

    def __init__(self) -> None:
        """Initialize the spy base."""
        self.calls: List[MethodCall] = []

    def _record_call(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        return_value: Optional[Any] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        """Record a method call."""
        call = MethodCall(method_name, args, kwargs, return_value, exception)
        self.calls.append(call)

    def _format_args_string(self, *args: Any, **kwargs: Any) -> str:
        """Format arguments as a string."""
        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{key}={value}" for key, value in kwargs.items())
        return ", ".join(filter(None, [args_str, kwargs_str]))

    def verify_called(self, method_name: str) -> None:
        """Verify that a method was called."""
        for call in self.calls:
            if call.method_name == method_name:
                return

        raise SpyError(f"Method {method_name} was not called")

    def verify_not_called(self, method_name: str) -> None:
        """Verify that a method was not called."""
        for call in self.calls:
            if call.method_name == method_name:
                raise SpyError(f"Method {method_name} was called")

    def verify_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Verify that a method was called with specific arguments."""
        for call in self.calls:
            if call.method_name == method_name:
                # Check positional arguments
                if len(args) > 0 and call.args != args:
                    continue

                # Check keyword arguments
                if kwargs and not all(key in call.kwargs and call.kwargs[key] == value for key, value in kwargs.items()):
                    continue

                return

        all_args = self._format_args_string(*args, **kwargs)
        raise SpyError(f"Method {method_name} was not called with arguments ({all_args})")

    def verify_call_count(self, method_name: str, count: int) -> None:
        """Verify that a method was called a specific number of times."""
        actual_count = sum(1 for call in self.calls if call.method_name == method_name)

        if actual_count != count:
            raise SpyError(f"Method {method_name} was called {actual_count} times, expected {count} times")

    def get_calls(self, method_name: str) -> List[MethodCall]:
        """Get all calls to a specific method."""
        return [call for call in self.calls if call.method_name == method_name]

    def clear_calls(self) -> None:
        """Clear all recorded calls."""
        self.calls = []

    # Deprecated methods for backward compatibility
    def assert_called(self, method_name: str) -> None:
        """Assert that a method was called (deprecated)."""
        warnings.warn(
            "assert_called is deprecated and will be removed in a future version. Use verify_called instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            self.verify_called(method_name)
        except SpyError as e:
            raise AssertionError(str(e))

    def assert_not_called(self, method_name: str) -> None:
        """Assert that a method was not called (deprecated)."""
        warnings.warn(
            "assert_not_called is deprecated and will be removed in a future version. Use verify_not_called instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            self.verify_not_called(method_name)
        except SpyError as e:
            raise AssertionError(str(e))

    def assert_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Assert that a method was called with specific arguments (deprecated)."""
        warnings.warn(
            "assert_called_with is deprecated and will be removed in a future version. Use verify_called_with instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            self.verify_called_with(method_name, *args, **kwargs)
        except SpyError as e:
            raise AssertionError(str(e))

    def assert_call_count(self, method_name: str, count: int) -> None:
        """Assert that a method was called a specific number of times (deprecated)."""
        warnings.warn(
            "assert_call_count is deprecated and will be removed in a future version. Use verify_call_count instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            self.verify_call_count(method_name, count)
        except SpyError as e:
            raise AssertionError(str(e))
