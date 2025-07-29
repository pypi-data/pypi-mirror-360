"""Concrete Test Spy for the ``CrudBase`` Interface using Enhanced Spying."""

from typing import Any, Optional

# Assuming Client or a suitable mock/spy is available for injection
from crudclient.client import Client
from crudclient.crud.base import Crud as CrudBase

from ..exceptions import VerificationError  # Import VerificationError
from .enhanced import ClassSpy, EnhancedSpyBase, MethodSpy


# Note: This class now primarily acts as a wrapper and provider of specific assertions.
# The core spying mechanism (call recording, basic assertions) is handled by ClassSpy/EnhancedSpyBase.
class CrudSpy(EnhancedSpyBase):  # Inherit from EnhancedSpyBase for assertions and call storage
    """A Test Spy specifically for the :class:`crudclient.crud.base.Crud` interface."""

    # _resource_path is part of the target CrudBase instance, not the spy itself.

    def __init__(self, client: Client, resource_path: str = "/test", datamodel: Optional[type] = None, **kwargs: Any):
        """Initialize a :class:`CrudSpy` instance."""
        # 1. Create the actual CrudBase instance that will be spied upon
        # CrudBase requires a client.
        if client is None:
            raise ValueError("A client instance (real, spy, or mock) must be provided to CrudSpy")
        target_crud: CrudBase = CrudBase(client)
        # Set resource path and datamodel on the target instance
        target_crud._resource_path = resource_path
        target_crud._datamodel = datamodel
        # Apply any other kwargs relevant to CrudBase if needed

        # 2. Initialize the EnhancedSpyBase part (for storing calls, assertions)
        super().__init__()

        # 3. Create the ClassSpy wrapper around the target CrudBase instance
        crud_methods_to_spy = [
            "list",
            "get",
            "create",
            "update",
            "delete",
            "bulk_create",
            "bulk_update",
            "bulk_delete",
            # Add other relevant public methods of CrudBase if needed
        ]
        self._spy_wrapper = ClassSpy(target_object=target_crud, methods=crud_methods_to_spy)

        # Store the target CrudBase instance
        self._target_crud = target_crud

        # Ensure the MethodSpy instances within ClassSpy record calls to *this* CrudSpy
        for method_name in crud_methods_to_spy:
            if hasattr(self._spy_wrapper, method_name):
                spy_method = getattr(self._spy_wrapper, method_name)
                if isinstance(spy_method, MethodSpy):
                    spy_method.spy = self

    # Delegate method calls and attribute access
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the spy wrapper, base class, or target CrudBase."""
        # Priority 1: Is it a method being spied on by the wrapper?
        if hasattr(self._spy_wrapper, name) and callable(getattr(self._spy_wrapper, name)):
            spy_method = getattr(self._spy_wrapper, name)
            if isinstance(spy_method, MethodSpy):
                spy_method.spy = self
            return spy_method

        # Priority 2: Is it an attribute of the EnhancedSpyBase itself?
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass

        # Priority 3: Is it an attribute of the *target* CrudBase object?
        try:
            return getattr(self._target_crud, name)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object (or its target) has no attribute '{name}'")

    # --- Custom Assertions specific to Crud interactions ---
    # These methods now operate on the self.get_calls() list inherited from EnhancedSpyBase,
    # which contains CallRecord objects.

    # Note: The original implementations of list, get, create, etc. are removed.
    # The ClassSpy mechanism handles intercepting these calls on the target_crud.

    def verify_resource_created(self, data: Any) -> None:
        """Verify that a resource was created with specific data."""
        for call in self.get_calls("create"):  # Filter by method name
            # Data is typically the first positional argument for create
            if call.args and call.args[0] == data:
                return
        raise VerificationError(f"Resource with data {data} was not created")

    def verify_resource_updated(self, id: Any, data: Any) -> None:
        """Verify that a resource was updated with a specific ID and data."""
        for call in self.get_calls("update"):
            # ID and data are typically the first two positional arguments for update
            if call.args and len(call.args) >= 2 and call.args[0] == id and call.args[1] == data:
                return
        raise VerificationError(f"Resource with ID {id} was not updated with data {data}")

    def verify_resource_deleted(self, id: Any) -> None:
        """Verify that a resource was deleted with the given ID."""
        for call in self.get_calls("delete"):
            # ID is typically the first positional argument for delete
            if call.args and call.args[0] == id:
                return
        raise VerificationError(f"Resource with ID {id} was not deleted")


# (Removed commented out original methods)
