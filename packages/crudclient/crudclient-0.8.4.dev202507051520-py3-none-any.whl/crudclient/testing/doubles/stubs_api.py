import copy
import uuid
from typing import Any, Dict, List, Optional, Type

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig

from .stubs_crud import StubCrud


class StubAPI(API):
    """A stub implementation of the API class for testing, managing multiple stubbed endpoints."""

    client_class = Client  # Can be overridden if needed, e.g., with StubClient

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, **kwargs: Any):
        """Initialize the StubAPI."""
        if client_config is None:
            # Provide a default config if none is given
            client_config = ClientConfig(hostname="https://stub.api.example.com")
        super().__init__(client, client_config, **kwargs)
        self.endpoints: Dict[str, StubCrud] = {}
        # Shared data store across all registered endpoints
        self._data_store: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def register_endpoint(self, name: str, endpoint: str, model: Optional[Type[Any]] = None, **kwargs: Any) -> StubCrud:
        # Initialize data store for this endpoint if it doesn't exist
        """Register a new stubbed CRUD endpoint associated with this API instance."""
        if name not in self._data_store:
            self._data_store[name] = {}

        # Create a stub CRUD for this endpoint, passing the specific part of the shared store
        crud = StubCrud(
            client_or_name=self.client, endpoint=endpoint, model=model, data_store=self._data_store[name], **kwargs  # Pass the specific store slice
        )

        # Store the CRUD and make it accessible as an attribute
        self.endpoints[name] = crud
        setattr(self, name, crud)

        return crud

    def _register_endpoints(self) -> None:
        """Internal method override; endpoints are registered via `register_endpoint`."""

    def __getattr__(self, name: str) -> Any:
        """Provide attribute-style access to registered `StubCrud` endpoints."""
        if name in self.endpoints:
            return self.endpoints[name]

        # Raise AttributeError for undefined attributes, consistent with standard Python behavior
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get_data_store(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Retrieve the complete, partitioned data store for all registered endpoints."""
        return self._data_store

    def clear_data_store(self) -> None:
        """Clear all data from the data stores of all registered endpoints and reset"""
        for endpoint_store in self._data_store.values():
            endpoint_store.clear()
        # Also reset next_id counters in each StubCrud instance if necessary
        for crud_instance in self.endpoints.values():
            crud_instance._next_id = 1  # Reset ID counter

    def populate_data_store(self, endpoint_name: str, data: List[Dict[str, Any]]) -> None:
        """Populate the data store for a specific registered endpoint with initial data."""
        if endpoint_name not in self._data_store:
            # If endpoint wasn't pre-registered, initialize its store part
            self._data_store[endpoint_name] = {}
            # Attempt to find the corresponding StubCrud instance to update its next_id
            crud_instance = self.endpoints.get(endpoint_name)
        else:
            crud_instance = self.endpoints.get(endpoint_name)

        max_id = 0
        for item in data:
            item_copy = copy.deepcopy(item)  # Avoid modifying original data
            if "id" not in item_copy:
                item_copy["id"] = str(uuid.uuid4())  # Use UUID if no ID

            str_id = str(item_copy["id"])
            self._data_store[endpoint_name][str_id] = item_copy

            # Track max numeric ID for potential next_id update
            if str_id.isdigit():
                max_id = max(max_id, int(str_id))

        # Update next_id in the corresponding StubCrud instance if found
        if crud_instance:
            crud_instance._next_id = max(crud_instance._next_id, max_id + 1)
