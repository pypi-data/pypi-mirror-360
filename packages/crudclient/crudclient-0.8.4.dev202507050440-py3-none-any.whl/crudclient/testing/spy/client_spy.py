"""Concrete Test Spy for the ``Client`` Interface using Enhanced Spying."""

from typing import Any, Dict, Union

from crudclient.client import Client
from crudclient.config import ClientConfig

from ..exceptions import VerificationError  # Import VerificationError
from .enhanced import ClassSpy, EnhancedSpyBase


# Note: This class now primarily acts as a wrapper and provider of specific assertions.
# The core spying mechanism (call recording, basic assertions) is handled by ClassSpy/EnhancedSpyBase.
class ClientSpy(EnhancedSpyBase):  # Inherit from EnhancedSpyBase for assertions and call storage
    """A Test Spy specifically for the :class:`crudclient.client.Client` interface."""

    def __init__(self, config: Union[ClientConfig, Dict[str, Any]], **kwargs: Any):
        """Initialize a :class:`ClientSpy` instance."""
        # 1. Create the actual client instance that will be spied upon
        target_client = Client(config, **kwargs)

        # 2. Initialize the EnhancedSpyBase part (for storing calls, assertions)
        super().__init__()

        # 3. Create the ClassSpy wrapper around the target client
        # We need to explicitly list the methods of the Client class to spy on
        client_methods = [
            "get",
            "post",
            "put",
            "delete",
            "patch",
            # Add other relevant public methods of Client if needed
        ]
        self._spy_wrapper = ClassSpy(target_object=target_client, methods=client_methods)

        # Store the target client if direct access is ever needed (usually not)
        self._target_client = target_client

    # Delegate method calls to the spy wrapper
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the spy wrapper or base class."""
        # If it's a method we are spying on, get it from the wrapper
        if hasattr(self._spy_wrapper, name) and callable(getattr(self._spy_wrapper, name)):
            # The ClassSpy needs access to *this* instance's _record_call
            # We need to bind the MethodSpy's spy attribute to self
            method_spy = getattr(self._spy_wrapper, name)
            method_spy.spy = self  # Ensure MethodSpy records calls to *this* ClientSpy instance
            return method_spy
        # Otherwise, try getting it from the base class (EnhancedSpyBase) or raise AttributeError
        try:
            return super().__getattribute__(name)
        except AttributeError:
            # If not found in EnhancedSpyBase, maybe it's a property of the target client?
            # This part might need refinement depending on Client's attributes vs methods.
            # For now, prioritize spied methods and base class attributes.
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    # --- Custom Assertions specific to Client interactions ---
    # These methods now operate on the self._calls list inherited from EnhancedSpyBase,
    # which contains CallRecord objects.

    # Note: The original implementations of get, post, put, delete, patch are removed.
    # The ClassSpy mechanism handles intercepting these calls on the target_client.

    # Example: Adjusting assert_endpoint_called
    def verify_endpoint_called(self, endpoint: str) -> None:
        """Verify that an endpoint was called via any HTTP method."""
        # Access self.get_calls() provided by EnhancedSpyBase
        for call in self.get_calls():  # call is now a CallRecord
            # Endpoint is typically the first positional argument
            if call.args and call.args[0] == endpoint:
                return

        raise VerificationError(f"Endpoint {endpoint} was not called")

    # Adjust other custom assertions similarly...
    def verify_endpoint_called_with_method(self, method: str, endpoint: str) -> None:
        """Verify that an endpoint was called with a specific HTTP method."""
        for call in self.get_calls(method):  # Filter by method name using get_calls(method)
            if call.args and call.args[0] == endpoint:
                return

        raise VerificationError(f"Endpoint {endpoint} was not called with method {method}")

    def verify_json_payload_sent(self, method: str, endpoint: str, expected_json: Any) -> None:
        """Verify that a JSON payload was sent to an endpoint using ``method``."""
        for call in self.get_calls(method):
            if call.args and call.args[0] == endpoint and "json" in call.kwargs and call.kwargs["json"] == expected_json:
                return

        raise VerificationError(f"JSON payload {expected_json} was not sent to {endpoint} with method {method}")

    # --- Deprecated/Removed methods ---
    # The following methods are handled by ClassSpy/EnhancedSpyBase or are no longer needed

    # get, post, put, delete, patch methods are removed (handled by ClassSpy wrapper)

    # _record_call is handled by EnhancedSpyBase/MethodSpy

    # delegate attribute is removed (handled by ClassSpy target_object)

    # We keep the custom assertions, adapting them as needed.
    # Basic assertions (assert_called, assert_called_with, etc.) come from SpyAssertionsMixin via EnhancedSpyBase.


# (Removed commented out and leftover code from previous version)
