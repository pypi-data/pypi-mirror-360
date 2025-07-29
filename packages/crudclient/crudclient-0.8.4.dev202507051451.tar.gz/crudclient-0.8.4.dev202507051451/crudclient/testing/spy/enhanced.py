"""Enhanced spy components for detailed interaction recording and verification."""

import inspect
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from .method_call import MethodCall
from .spy_assertions import SpyAssertionsMixin


class CallRecord(MethodCall):
    """Represents a single recorded method call with enhanced details."""

    def __init__(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        timestamp: float,
        duration: Optional[float] = None,
        result: Any = None,
        exception: Optional[Exception] = None,
    ):
        """Initializes an enhanced record of a method call."""
        # Initialize the base MethodCall with the common attributes
        super().__init__(method_name, args, kwargs, result, exception)

        # Add enhanced attributes
        self.timestamp = timestamp
        self.duration = duration

        # Rename return_value to result for consistency with the enhanced spy implementation
        self.result = self.return_value
        delattr(self, "return_value")

        # Capture stack trace and caller info
        stack = inspect.stack()
        self.stack_trace = [f"{frame.filename}:{frame.lineno} in {frame.function}" for frame in stack[2:]]  # Skip this method and the spy method

        # Get caller info (the first frame that's not in this file)
        self.caller_info = None
        for frame in stack[2:]:
            if not frame.filename.endswith("enhanced.py"):
                self.caller_info = {
                    "filename": frame.filename,
                    "lineno": frame.lineno,
                    "function": frame.function,
                    "code_context": frame.code_context[0].strip() if frame.code_context else None,
                }
                break

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the call record."""
        args_str = ", ".join([repr(arg) for arg in self.args])
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in self.kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        timestamp_str = datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")

        if self.exception:
            result_str = f"raised {type(self.exception).__name__}: {self.exception}"
        else:
            result_str = f"returned {repr(self.result)}"

        duration_str = f" (took {self.duration:.6f}s)" if self.duration is not None else ""

        return f"{self.method_name}({all_args}) {result_str}{duration_str} at {timestamp_str}"


class EnhancedSpyBase(SpyAssertionsMixin):
    """Base class for enhanced spies providing call recording and retrieval logic."""

    def __init__(self) -> None:
        """Initializes the spy with empty call lists."""
        self._calls: List[CallRecord] = []
        self._method_calls: Dict[str, List[CallRecord]] = {}

    def _record_call(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        result: Any = None,
        exception: Optional[Exception] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Record a method call with its arguments and result."""
        timestamp = time.time()

        record = CallRecord(
            method_name=method_name, args=args, kwargs=kwargs, timestamp=timestamp, duration=duration, result=result, exception=exception
        )

        self._calls.append(record)

        if method_name not in self._method_calls:
            self._method_calls[method_name] = []

        self._method_calls[method_name].append(record)

    def get_calls(self, method_name: Optional[str] = None) -> List[CallRecord]:
        """Retrieve recorded calls."""
        if method_name is None:
            return self._calls

        return self._method_calls.get(method_name, [])

    def get_call_count(self, method_name: Optional[str] = None) -> int:
        """Get the number of times a method (or any method) was called."""
        return len(self.get_calls(method_name))

    def was_called(self, method_name: str) -> bool:
        """Check if the specified method was called at least once."""
        return method_name in self._method_calls and len(self._method_calls[method_name]) > 0

    def was_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> bool:
        """Check if the specified method was called with the exact arguments."""
        if not self.was_called(method_name):
            return False

        for call in self._method_calls[method_name]:
            # Check positional arguments
            if len(call.args) != len(args):
                continue

            args_match = all(a == b for a, b in zip(call.args, args))
            if not args_match:
                continue

            # Check keyword arguments
            kwargs_match = True
            for key, value in kwargs.items():
                if key not in call.kwargs or call.kwargs[key] != value:
                    kwargs_match = False
                    break

            if kwargs_match:
                return True

        return False

    # Assertion methods are inherited from SpyAssertionsMixin

    def reset(self) -> None:
        """Clears all recorded calls."""
        self._calls = []
        self._method_calls = {}


class MethodSpy:
    """Wraps a single method to spy on its calls."""

    def __init__(self, original_method: Callable, spy: EnhancedSpyBase, method_name: str, record_only: bool = False):
        """Initializes a spy for a specific method."""
        self.original_method = original_method
        self.spy = spy
        self.method_name = method_name
        self.record_only = record_only

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Handle calls to the spied method and record them."""
        start_time = time.time()
        result = None
        exception = None

        try:
            if not self.record_only:
                result = self.original_method(*args, **kwargs)
            return result
        except Exception as e:
            exception = e
            raise
        finally:
            duration = time.time() - start_time
            self.spy._record_call(method_name=self.method_name, args=args, kwargs=kwargs, result=result, exception=exception, duration=duration)


class ClassSpy(EnhancedSpyBase):
    """Spies on methods of a target object instance."""

    def __init__(self, target_object: Any, methods: Optional[List[str]] = None, record_only: bool = False):
        """Initializes a spy for an object instance."""
        super().__init__()
        self.target_object = target_object
        self.record_only = record_only

        # If no methods are specified, spy on all public methods
        if methods is None:
            methods = [name for name in dir(target_object) if callable(getattr(target_object, name)) and not name.startswith("_")]

        # Wrap each method with a spy
        for method_name in methods:
            original_method = getattr(target_object, method_name)
            if callable(original_method):
                spy_method = MethodSpy(original_method=original_method, spy=self, method_name=method_name, record_only=record_only)
                setattr(self, method_name, spy_method)

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the target object if not a spied method."""
        return getattr(self.target_object, name)


class FunctionSpy(EnhancedSpyBase):
    """Spies on calls to a standalone function."""

    def __init__(self, target_function: Callable, record_only: bool = False):
        """Initializes a spy for a standalone function."""
        super().__init__()
        self.target_function = target_function
        self.record_only = record_only

        # Get the function name
        self.method_name = target_function.__name__

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Handle calls to the spied function and record them."""
        start_time = time.time()
        result = None
        exception = None

        try:
            if not self.record_only:
                result = self.target_function(*args, **kwargs)
            return result
        except Exception as e:
            exception = e
            raise
        finally:
            duration = time.time() - start_time
            self._record_call(method_name=self.method_name, args=args, kwargs=kwargs, result=result, exception=exception, duration=duration)


class EnhancedSpyFactory:
    """Provides static methods to conveniently create different types of spies."""

    @staticmethod
    def create_class_spy(target_object: Any, methods: Optional[List[str]] = None, record_only: bool = False) -> ClassSpy:
        """Factory method to create a :class:`ClassSpy`."""
        return ClassSpy(target_object, methods, record_only)

    @staticmethod
    def create_function_spy(target_function: Callable, record_only: bool = False) -> FunctionSpy:
        """Factory method to create a :class:`FunctionSpy`."""
        return FunctionSpy(target_function, record_only)

    @staticmethod
    def patch_method(target_object: Any, method_name: str, record_only: bool = False) -> FunctionSpy:
        """Patch a method on an object with a :class:`FunctionSpy`."""
        original_method = getattr(target_object, method_name)
        spy = FunctionSpy(original_method, record_only)
        setattr(target_object, method_name, spy)
        return spy
