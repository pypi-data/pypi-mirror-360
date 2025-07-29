from typing import Any, Dict, List, Optional, Type, Union

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.doubles.data_store_definitions import (
    ValidationException,  # Import ValidationException
)
from crudclient.testing.exceptions import FakeAPIError  # Corrected import path

from .data_store import DataStore


class FakeCrud:
    """Internal helper simulating a single CRUD endpoint's operations for `FakeAPI`."""

    def __init__(self, database: DataStore, collection: str, model: Optional[Type[Any]] = None):
        """Initialize a FakeCrud instance (typically called by `FakeAPI.register_endpoint`)."""
        self.database = database
        self.collection = collection
        self.model = model

    def list(self, **kwargs: Any) -> Any:
        # Extract pagination, sorting, and filtering parameters
        """Simulates listing items, delegating to `DataStore.list`."""
        filters = kwargs.pop("filters", {})
        sort_by = kwargs.pop("sort_by", None)
        sort_desc = kwargs.pop("sort_desc", False)
        page = kwargs.pop("page", 1)
        page_size = kwargs.pop("page_size", None)
        include_deleted = kwargs.pop("include_deleted", False)
        include_related = kwargs.pop("include_related", None)
        fields = kwargs.pop("fields", None)

        # Add remaining kwargs to filters
        filters.update(kwargs)

        # Get data from database
        result = self.database.list(
            self.collection,
            filters=filters,
            sort_by=sort_by,
            sort_desc=sort_desc,
            page=page,
            page_size=page_size,
            include_deleted=include_deleted,
            include_related=include_related,
            fields=fields,
        )

        data = result["data"]

        # Convert to model instances if model is provided
        if self.model:
            data = [self.model(**item) for item in data]

        return data

    def get(self, id: Any, **kwargs: Any) -> Any:
        """Simulates retrieving a single item by ID, delegating to `DataStore.get`."""
        include_deleted = kwargs.pop("include_deleted", False)
        include_related = kwargs.pop("include_related", None)
        fields = kwargs.pop("fields", None)

        data = self.database.get(
            self.collection,
            id,
            include_deleted=include_deleted,
            include_related=include_related,
            fields=fields,
        )

        if data is None:
            # Raise 404 instead of returning None
            raise FakeAPIError(status_code=404, detail=f"{self.collection} with id {id} not found")

        # Convert to model instance if model is provided
        if self.model:
            return self.model(**data)

        return data

    def create(self, data: Any, **kwargs: Any) -> Any:
        """Simulates creating an item, delegating to `DataStore.create`."""
        skip_validation = kwargs.pop("skip_validation", False)

        # Convert model instance to dict if needed
        if hasattr(data, "__dict__"):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
        else:
            data_dict = data

        try:
            created_data = self.database.create(self.collection, data_dict, skip_validation=skip_validation)
        except ValidationException as e:
            # Raise 422 for validation errors
            raise FakeAPIError(status_code=422, detail=e.errors) from e

        # Convert to model instance if model is provided
        if self.model:
            return self.model(**created_data)

        return created_data

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """Simulates updating an item by ID, delegating to `DataStore.update`."""
        skip_validation = kwargs.pop("skip_validation", False)
        check_version = kwargs.pop("check_version", True)

        # Convert model instance to dict if needed
        if hasattr(data, "__dict__"):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
        else:
            data_dict = data

        try:
            updated_data = self.database.update(self.collection, id, data_dict, skip_validation=skip_validation, check_version=check_version)
        except ValidationException as e:
            # Raise 422 for validation errors
            raise FakeAPIError(status_code=422, detail=e.errors) from e
        except ValueError as e:
            # Assume ValueError is primarily for version conflicts here
            # Raise 409 Conflict
            raise FakeAPIError(status_code=409, detail=str(e)) from e

        if updated_data is None:
            # Raise 404 if update didn't find the item (and didn't raise other errors)
            raise FakeAPIError(status_code=404, detail=f"{self.collection} with id {id} not found")

        # Convert to model instance if model is provided
        if self.model:
            return self.model(**updated_data)

        return updated_data

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """Simulates deleting an item by ID, delegating directly to `DataStore.delete`."""
        soft_delete = kwargs.pop("soft_delete", False)
        cascade = kwargs.pop("cascade", False)

        return self.database.delete(self.collection, id, soft_delete=soft_delete, cascade=cascade)

    def bulk_create(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """Simulates creating multiple items, delegating to `DataStore.bulk_create`."""
        skip_validation = kwargs.pop("skip_validation", False)

        # Convert model instances to dicts if needed
        data_dicts = []
        for item in data:
            if hasattr(item, "__dict__"):
                data_dict = {k: v for k, v in item.__dict__.items() if not k.startswith("_")}
            else:
                data_dict = item

            data_dicts.append(data_dict)

        # Note: Bulk operations might require more nuanced error handling for partial failures.
        # For now, catch ValidationException during the whole bulk operation.
        # A real API might return a 207 Multi-Status or similar.
        try:
            created_data = self.database.bulk_create(self.collection, data_dicts, skip_validation=skip_validation)
        except ValidationException as e:
            # Raise 422 for validation errors during bulk create
            raise FakeAPIError(status_code=422, detail=e.errors) from e

        # Convert to model instances if model is provided
        if self.model:
            return [self.model(**item) for item in created_data]

        return created_data

    def bulk_update(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """Simulates updating multiple items, delegating to `DataStore.bulk_update`."""
        skip_validation = kwargs.pop("skip_validation", False)
        check_version = kwargs.pop("check_version", True)

        # Convert model instances to dicts if needed
        data_dicts = []
        for item in data:
            if hasattr(item, "__dict__"):
                data_dict = {k: v for k, v in item.__dict__.items() if not k.startswith("_")}
            else:
                data_dict = item

            data_dicts.append(data_dict)

        # Similar note for bulk update regarding partial failures and error reporting.
        try:
            updated_data = self.database.bulk_update(self.collection, data_dicts, skip_validation=skip_validation, check_version=check_version)
        except ValidationException as e:
            # Raise 422 for validation errors during bulk update
            raise FakeAPIError(status_code=422, detail=e.errors) from e
        except ValueError as e:
            # Raise 409 for version conflicts during bulk update
            raise FakeAPIError(status_code=409, detail=str(e)) from e

        # Convert to model instances if model is provided
        if self.model:
            return [self.model(**item) if item is not None else None for item in updated_data]

        return updated_data

    def bulk_delete(self, ids: List[Any], **kwargs: Any) -> int:
        """Simulates deleting multiple items by ID, delegating to `DataStore.bulk_delete`."""
        soft_delete = kwargs.pop("soft_delete", False)
        cascade = kwargs.pop("cascade", False)

        return self.database.bulk_delete(self.collection, ids, soft_delete=soft_delete, cascade=cascade)


class FakeAPI(API):
    """A test double (fake) implementation of `crudclient.api.API` for testing."""

    client_class = Client

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, **kwargs: Any):
        """Initialize a FakeAPI instance."""
        if client_config is None:
            client_config = ClientConfig(hostname="https://api.example.com")
        super().__init__(client, client_config, **kwargs)
        self.database = DataStore()
        self.endpoints: Dict[str, FakeCrud] = {}

    def register_endpoint(self, name: str, endpoint: str, model: Optional[Type[Any]] = None, **kwargs: Any) -> FakeCrud:
        """Registers a simulated CRUD endpoint, making it accessible as an attribute."""
        crud = FakeCrud(self.database, name, model)
        self.endpoints[name] = crud
        setattr(self, name, crud)
        return crud

    def define_relationship(self, source_collection: str, target_collection: str, relationship_type: str, **kwargs: Any) -> "FakeAPI":
        """Convenience method to define a relationship in the underlying DataStore."""
        self.database.define_relationship(
            source_collection=source_collection, target_collection=target_collection, relationship_type=relationship_type, **kwargs
        )
        return self

    def add_validation_rule(self, field: str, validator_func: Any, error_message: str, collection: Optional[str] = None) -> "FakeAPI":
        """Convenience method to add a validation rule to the underlying DataStore."""
        self.database.add_validation_rule(field=field, validator_func=validator_func, error_message=error_message, collection=collection)
        return self

    def add_unique_constraint(
        self, fields: Union[str, List[str]], error_message: Optional[str] = None, collection: Optional[str] = None
    ) -> "FakeAPI":
        """Convenience method to add a unique constraint to the underlying DataStore."""
        self.database.add_unique_constraint(fields=fields, error_message=error_message, collection=collection)
        return self

    def set_timestamp_tracking(self, enabled: bool) -> "FakeAPI":
        """Convenience method to configure timestamp tracking in the underlying DataStore."""
        self.database.set_timestamp_tracking(enabled)
        return self

    def __getattr__(self, name: str) -> Any:
        """Provides access to registered endpoints via attribute lookup."""
        if name in self.endpoints:
            return self.endpoints[name]

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _register_endpoints(self) -> None:
        """Register default endpoints. This is a no-op in FakeAPI."""
