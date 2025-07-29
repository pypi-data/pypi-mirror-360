"""Exception classes for CRUD mock operations."""

from crudclient.exceptions import CrudClientError


class ConcurrencyError(CrudClientError):
    """Raised when a concurrency conflict is detected."""


class ValidationFailedError(CrudClientError):
    """Raised when validation of input data fails."""
