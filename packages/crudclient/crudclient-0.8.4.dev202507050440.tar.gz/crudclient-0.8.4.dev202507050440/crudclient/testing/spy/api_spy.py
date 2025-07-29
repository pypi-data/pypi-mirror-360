"""Concrete Test Spy for the ``API`` Interface using Enhanced Spying."""

from typing import Any, Optional, Type

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig

from ..exceptions import VerificationError  # Import VerificationError
from .enhanced import ClassSpy, EnhancedSpyBase


# Note: This class now primarily acts as a wrapper and provider of specific assertions.
# The core spying mechanism (call recording, basic assertions) is handled by ClassSpy/EnhancedSpyBase.
class ApiSpy(EnhancedSpyBase):  # Inherit from EnhancedSpyBase for assertions and call storage
    """A Test Spy specifically for the :class:`crudclient.api.API` interface."""

    # client_class is part of the original API, keep it if needed for target API instantiation
    client_class = Client

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, **kwargs: Any):
        """Initialize an :class:`ApiSpy` instance."""
        # 1. Create the actual API instance that will be spied upon
        # Use the provided client/config or defaults
        if client_config is None and client is None:
            # Provide a default config if neither client nor config is given
            client_config = ClientConfig(hostname="https://example.com/api")  # Default hostname

        # Define a minimal concrete API class to instantiate
        class ConcreteAPI(API):
            def _register_endpoints(self) -> None:
                # Minimal implementation for the abstract method
                pass

        # Instantiate the concrete target API
        target_api = ConcreteAPI(client=client, client_config=client_config, **kwargs)

        # 2. Initialize the EnhancedSpyBase part (for storing calls, assertions)
        super().__init__()

        # 3. Create the ClassSpy wrapper around the target API
        # Specify methods to spy on. Let's focus on 'register_endpoint'.
        # '_register_endpoints' is protected, usually not spied on directly.
        api_methods_to_spy = [
            "register_endpoint",
            # Add other relevant public methods of API if needed
        ]
        # Note: We don't explicitly spy on __getattr__ here. We'll handle it below.
        self._spy_wrapper = ClassSpy(target_object=target_api, methods=api_methods_to_spy)

        # Store the target API for direct access if needed (e.g., for __getattr__)
        self._target_api = target_api

    # Delegate method calls and attribute access
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the spy wrapper, base class, or target API."""
        # Priority 1: Is it a method being spied on by the wrapper?
        if hasattr(self._spy_wrapper, name) and callable(getattr(self._spy_wrapper, name)):
            method_spy = getattr(self._spy_wrapper, name)
            # Ensure the MethodSpy instance within ClassSpy records calls to *this* ApiSpy instance
            if hasattr(method_spy, "spy"):
                method_spy.spy = self
            return method_spy

        # Priority 2: Is it an attribute of the EnhancedSpyBase itself (e.g., assertion methods)?
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass  # Not found in base, continue searching

        # Priority 3: Is it an attribute of the *target* API object (e.g., a registered endpoint)?
        # Delegate to the target API's __getattr__ or direct attribute access.
        try:
            return getattr(self._target_api, name)
        except AttributeError:
            # If not found anywhere, raise the error
            raise AttributeError(f"'{type(self).__name__}' object (or its target) has no attribute '{name}'")

    # --- Custom Assertions specific to API interactions ---
    # These methods now operate on the self.get_calls() list inherited from EnhancedSpyBase,
    # which contains CallRecord objects.

    # Note: The original implementations of _register_endpoints, register_endpoint, __getattr__ are removed.
    # The ClassSpy mechanism handles intercepting 'register_endpoint'.
    # Our custom __getattr__ handles delegation appropriately.

    # Example: Adjusting assert_endpoint_registered

    def verify_endpoint_registered(self, name: str) -> None:
        """Verify that an endpoint with the given name was registered."""
        # Access self.get_calls() provided by EnhancedSpyBase, filtered by method name
        for call in self.get_calls("register_endpoint"):  # call is now a CallRecord
            # Endpoint name is typically the first positional argument
            if call.args and call.args[0] == name:
                return

        raise VerificationError(f"Endpoint {name} was not registered via register_endpoint")

    # Adjust other custom assertions similarly...
    def verify_endpoint_registered_with_model(self, name: str, model: Type[Any]) -> None:
        """Verify that an endpoint was registered with a specific model."""
        for call in self.get_calls("register_endpoint"):
            if call.args and call.args[0] == name and "model" in call.kwargs and call.kwargs["model"] == model:
                return

        raise VerificationError(f"Endpoint {name} was not registered via register_endpoint with model {model.__name__}")


# (Removed commented out original methods)
