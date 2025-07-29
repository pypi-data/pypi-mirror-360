"""Core mock implementations for the crudclient testing framework.

This module provides mock implementations of the fundamental client and HTTP
components.
"""

from .client import MockClient
from .http_client import MockHTTPClient

__all__ = [
    "MockClient",
    "MockHTTPClient",
]
