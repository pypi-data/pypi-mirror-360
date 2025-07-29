"""
Exceptions for the crudclient testing framework.

This module defines exceptions that can be raised by the testing framework.
"""

from typing import Any, Dict, Optional


class TestingError(Exception):
    """Base class for all testing framework exceptions."""


class MockConfigurationError(TestingError):
    """Raised when there is an error in the mock configuration."""


class VerificationError(TestingError):
    """Raised when a verification fails."""


class RequestNotConfiguredError(MockConfigurationError):
    """Raised when a request is made that has not been configured."""


class AuthStrategyError(TestingError):
    """Raised when there is an error with an auth strategy."""


class CRUDOperationError(TestingError):
    """Raised when there is an error with a CRUD operation."""


class DataStoreError(TestingError):
    """Raised when there is an error with the data store."""


class ResourceNotFoundError(DataStoreError):
    """Raised when a resource is not found in the data store."""


class SpyError(TestingError):
    """Raised when there is an error with a spy."""


class FakeAPIError(TestingError):
    """Raised when there is an error with the FakeAPI."""

    def __init__(self, status_code: int, detail: Any, headers: Optional[Dict[str, str]] = None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}
        super().__init__(f"FakeAPI Error {status_code}: {detail}")
