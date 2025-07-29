"""Data structure for representing a recorded method call."""

from typing import Any, Dict, Optional, Tuple


class MethodCall:
    """Record of a method call for verification."""

    def __init__(
        self, method_name: str, args: Tuple[Any, ...], kwargs: Dict[str, Any], return_value: Any = None, exception: Optional[Exception] = None
    ):
        """Initialize a method call record."""
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs
        self.return_value = return_value
        self.exception = exception

    def __repr__(self) -> str:
        """String representation of the method call."""
        args_str = ", ".join([repr(arg) for arg in self.args])
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in self.kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        if self.exception:
            result = f" -> raised {self.exception.__class__.__name__}({self.exception})"
        else:
            result = f" -> returned {repr(self.return_value)}" if self.return_value is not None else ""

        return f"{self.method_name}({all_args}){result}"
