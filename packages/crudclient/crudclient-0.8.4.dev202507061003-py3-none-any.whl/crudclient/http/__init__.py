"""
HTTP Module for CrudClient.

This package contains modules for handling HTTP operations in the CrudClient library.
It provides a modular architecture with clear separation of concerns for HTTP operations.
"""

from .client import HttpClient
from .errors import ErrorHandler
from .request import RequestFormatter
from .response import ResponseHandler
from .retry import RetryHandler
from .retry_conditions import RetryCondition, RetryEvent
from .retry_strategies import (
    ExponentialBackoffStrategy,
    FixedRetryStrategy,
    RetryStrategy,
)
from .session import SessionManager

__all__ = [
    "HttpClient",
    "SessionManager",
    "RequestFormatter",
    "ResponseHandler",
    "ErrorHandler",
    "RetryHandler",
    "RetryStrategy",
    "FixedRetryStrategy",
    "ExponentialBackoffStrategy",
    "RetryCondition",
    "RetryEvent",
]
