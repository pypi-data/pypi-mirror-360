import copy
from typing import Any, Callable, Dict, List, Optional, Type, Union

from crudclient.client import Client

# mypy: ignore-errors


class CrudBase:
    """Abstract base class defining the standard interface for CRUD operations"""

    def __init__(self, client: Optional[Client] = None, endpoint: str = "", model: Optional[Type[Any]] = None):
        """Initialize the CrudBase."""
        self.client = client
        self.endpoint = endpoint
        self.model = model

    def list(self, **kwargs: Any) -> List[Any]:
        """Retrieve a list of resources, potentially filtered or paginated."""
        raise NotImplementedError

    def get(self, id: Any, **kwargs: Any) -> Any:
        """Retrieve a single resource by its unique identifier."""
        raise NotImplementedError

    def create(self, data: Any, **kwargs: Any) -> Any:
        """Create a new resource."""
        raise NotImplementedError

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """Update an existing resource identified by its ID."""
        raise NotImplementedError

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """Delete a resource identified by its ID."""
        raise NotImplementedError


class StubCrud(CrudBase):
    """A stub implementation of CrudBase for testing, using an in-memory data store."""

    def configure_list(self, response: Optional[Any] = None, handler: Optional[Callable] = None) -> None:
        """Configure a static response or a dynamic handler for the `list` operation."""
        self._list_response = response
        self._list_handler = handler

    def configure_get(self, response: Optional[Any] = None, handler: Optional[Callable] = None) -> None:
        """Configure a static response or a dynamic handler for the `get` operation."""
        self._get_response = response
        self._get_handler = handler

    def configure_create(self, response: Optional[Any] = None, handler: Optional[Callable] = None) -> None:
        """Configure a static response or a dynamic handler for the `create` operation."""
        self._create_response = response
        self._create_handler = handler

    def __init__(
        self,
        client_or_name: Union[Client, str, None] = None,
        endpoint: str = "",
        model: Optional[Type[Any]] = None,
        default_data: Optional[Dict[str, Any]] = None,
        data_store: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        # Handle the case where the first argument is a string (name)
        """Initialize the StubCrud instance."""
        if isinstance(client_or_name, str):
            client = None
            # If the first argument is a string, use it as the endpoint
            if not endpoint:
                endpoint = client_or_name
        else:
            client = client_or_name

        super().__init__(client, endpoint, model)

        # Default data for responses
        self._default_data = default_data or {"id": 1, "name": "Stub Resource"}

        # In-memory data store for CRUD operations
        self._data_store = data_store if data_store is not None else {}

        # Next ID for auto-incrementing
        self._next_id = max([int(id_str) for id_str in self._data_store.keys() if id_str.isdigit()], default=0) + 1

        # Operation hooks
        self._before_list_hook: Optional[Callable] = None
        self._after_list_hook: Optional[Callable] = None
        self._before_get_hook: Optional[Callable] = None
        self._after_get_hook: Optional[Callable] = None
        self._before_create_hook: Optional[Callable] = None
        self._after_create_hook: Optional[Callable] = None
        self._before_update_hook: Optional[Callable] = None
        self._after_update_hook: Optional[Callable] = None
        self._before_delete_hook: Optional[Callable] = None
        self._after_delete_hook: Optional[Callable] = None

        # Configured responses and handlers
        self._list_response = None
        self._list_handler = None
        self._get_response = None
        self._get_handler = None
        self._create_response = None
        self._create_handler = None

    def list(self, **kwargs: Any) -> List[Any]:
        # Call before hook
        """Simulate retrieving a list of resources from the in-memory store."""
        if self._before_list_hook:
            self._before_list_hook(kwargs)

        # Use configured handler if available
        if self._list_handler:
            result = self._list_handler(**kwargs)
            # Convert to model instances if model is provided and result is a list of dicts
            if self.model and isinstance(result, list) and result and isinstance(result[0], dict):
                result = [self.model(**item) for item in result]
            return result

        # Use configured response if available
        if self._list_response is not None:
            return self._list_response

        # Apply filters
        filtered_data = list(self._data_store.values())

        for key, value in kwargs.items():
            if key in ("sort_by", "sort_desc", "page", "page_size"):
                continue

            filtered_data = [item for item in filtered_data if item.get(key) == value]

        # Apply sorting
        sort_by = kwargs.get("sort_by")
        sort_desc = kwargs.get("sort_desc", False)

        if sort_by:
            filtered_data.sort(key=lambda x: x.get(sort_by, ""), reverse=sort_desc)

        # Apply pagination
        page = kwargs.get("page", 1)
        page_size = kwargs.get("page_size")

        if page_size:
            start = (page - 1) * page_size
            end = start + page_size
            filtered_data = filtered_data[start:end]

        # Convert to model instances if model is provided
        result = filtered_data
        if self.model:
            result = [self.model(**item) for item in filtered_data]

        # Call after hook
        if self._after_list_hook:
            result = self._after_list_hook(result, kwargs)

        return result

    def get(self, id: Any, **kwargs: Any) -> Any:
        # Call before hook
        """Simulate retrieving a single resource by ID from the in-memory store."""
        if self._before_get_hook:
            self._before_get_hook(id, kwargs)

        # Use configured handler if available
        if self._get_handler:
            result = self._get_handler(id, **kwargs)
            # Convert to model instance if model is provided and result is a dict
            if self.model and isinstance(result, dict):
                result = self.model(**result)
            return result

        # Use configured response if available
        if self._get_response is not None:
            return self._get_response

        # Get the resource
        str_id = str(id)
        if str_id not in self._data_store:
            return None

        data = self._data_store[str_id]

        # Convert to model instance if model is provided
        result = data
        if self.model:
            result = self.model(**data)

        # Call after hook
        if self._after_get_hook:
            result = self._after_get_hook(result, id, kwargs)

        return result

    def create(self, data: Any, **kwargs: Any) -> Any:
        # Call before hook
        """Simulate creating a new resource in the in-memory store."""
        if self._before_create_hook:
            data = self._before_create_hook(data, kwargs)

        # Use configured handler if available
        if self._create_handler:
            result = self._create_handler(data, **kwargs)
            # Convert to model instance if model is provided and result is a dict
            if self.model and isinstance(result, dict):
                result = self.model(**result)
            return result

        # Use configured response if available
        if self._create_response is not None:
            return self._create_response

        # Convert model instance to dict if needed
        if hasattr(data, "__dict__"):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
        else:
            data_dict = copy.deepcopy(data)

        # Generate ID if not provided
        if "id" not in data_dict:
            data_dict["id"] = self._next_id
            self._next_id += 1

        # Store the resource
        str_id = str(data_dict["id"])
        self._data_store[str_id] = data_dict

        # Convert to model instance if model is provided
        result = data_dict
        if self.model:
            result = self.model(**data_dict)

        # Call after hook
        if self._after_create_hook:
            result = self._after_create_hook(result, kwargs)

        return result

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        # Call before hook
        """Simulate updating an existing resource in the in-memory store."""
        if self._before_update_hook:
            data = self._before_update_hook(id, data, kwargs)

        # Check if resource exists
        str_id = str(id)
        if str_id not in self._data_store:
            return None

        # Convert model instance to dict if needed
        if hasattr(data, "__dict__"):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
        else:
            data_dict = copy.deepcopy(data)

        # Update the resource
        existing_data = self._data_store[str_id]
        updated_data = copy.deepcopy(existing_data)
        updated_data.update(data_dict)

        # Ensure ID is preserved
        updated_data["id"] = id

        # Store the updated resource
        self._data_store[str_id] = updated_data

        # Convert to model instance if model is provided
        result = updated_data
        if self.model:
            result = self.model(**updated_data)

        # Call after hook
        if self._after_update_hook:
            result = self._after_update_hook(result, id, kwargs)

        return result

    def delete(self, id: Any, **kwargs: Any) -> bool:
        # Call before hook
        """Simulate deleting a resource from the in-memory store."""
        if self._before_delete_hook:
            self._before_delete_hook(id, kwargs)

        # Check if resource exists
        str_id = str(id)
        if str_id not in self._data_store:
            return False

        # Delete the resource
        del self._data_store[str_id]

        # Call after hook
        if self._after_delete_hook:
            self._after_delete_hook(id, kwargs)

        return True

    def set_before_list_hook(self, hook: Callable) -> None:
        """Set a hook to run before the list operation."""
        self._before_list_hook = hook

    def set_after_list_hook(self, hook: Callable) -> None:
        """Set a hook to run after the list operation, modifying the result."""
        self._after_list_hook = hook

    def set_before_get_hook(self, hook: Callable) -> None:
        """Set a hook to run before the get operation."""
        self._before_get_hook = hook

    def set_after_get_hook(self, hook: Callable) -> None:
        """Set a hook to run after the get operation, modifying the result."""
        self._after_get_hook = hook

    def set_before_create_hook(self, hook: Callable) -> None:
        """Set a hook to run before the create operation, modifying the input data."""
        self._before_create_hook = hook

    def set_after_create_hook(self, hook: Callable) -> None:
        """Set a hook to run after the create operation, modifying the result."""
        self._after_create_hook = hook

    def set_before_update_hook(self, hook: Callable) -> None:
        """Set a hook to run before the update operation, modifying the input data."""
        self._before_update_hook = hook

    def set_after_update_hook(self, hook: Callable) -> None:
        """Set a hook to run after the update operation, modifying the result."""
        self._after_update_hook = hook

    def set_before_delete_hook(self, hook: Callable) -> None:
        """Set a hook to run before the delete operation."""
        self._before_delete_hook = hook

    def set_after_delete_hook(self, hook: Callable) -> None:
        """Set a hook to run after the delete operation."""
        self._after_delete_hook = hook

    def verify_deleted(self, id: Any) -> bool:
        """Check if a resource with the given ID is absent from the data store."""
        str_id = str(id)
        return str_id not in self._data_store
