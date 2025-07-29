# No longer need direct imports of copy, uuid, datetime here
from typing import Any, Callable, Dict, List, Optional, Union

# Import delegated functions
from .data_store_bulk import bulk_create_items, bulk_delete_items, bulk_update_items
from .data_store_crud import create_item, delete_item, get_item, list_items, update_item

# Import definitions used in type hints and initialization
from .data_store_definitions import (  # ValidationException, # Not directly used here
    Relationship,
    UniqueConstraint,
    ValidationRule,
)

# Import helpers used directly (only RelationshipType needed for define_relationship)
from .data_store_relationships import RelationshipType  # Updated import location

# No longer need direct imports of other helpers or relationship/sorting functions


class DataStore:
    """An in-memory data store simulating a relational database backend."""

    def __init__(self) -> None:  # Added return type annotation
        """Initializes an empty DataStore."""
        self.collections: Dict[str, List[Dict[str, Any]]] = {}
        self.relationships: List[Relationship] = []
        self.validation_rules: List[ValidationRule] = []
        self.unique_constraints: List[UniqueConstraint] = []
        self.deleted_items: Dict[str, List[Dict[str, Any]]] = {}  # For soft deletes
        self.version_field = "_version"
        self.deleted_field = "_deleted"
        self.created_at_field = "_created_at"
        self.updated_at_field = "_updated_at"
        self.track_timestamps = True

    def get_collection(self, name: str) -> List[Dict[str, Any]]:
        """Retrieves a collection by name, creating it if it doesn't exist."""
        if name not in self.collections:
            self.collections[name] = []

        return self.collections[name]

    def define_relationship(self, source_collection: str, target_collection: str, relationship_type: str, **kwargs: Any) -> "DataStore":
        """Defines a relationship between two collections, simulating foreign keys."""
        relationship = Relationship(
            source_collection=source_collection, target_collection=target_collection, relationship_type=relationship_type, **kwargs
        )
        self.relationships.append(relationship)

        # For many-to-many relationships, create the junction collection if it doesn't exist
        if relationship_type == RelationshipType.MANY_TO_MANY and relationship.junction_collection:
            self.get_collection(relationship.junction_collection)

        return self

    def add_validation_rule(
        self, field: str, validator_func: Callable[[Any], bool], error_message: str, collection: Optional[str] = None
    ) -> "DataStore":
        """Adds a custom validation rule for a specific field within a collection."""
        rule = ValidationRule(field=field, validator_func=validator_func, error_message=error_message, collection=collection)
        self.validation_rules.append(rule)
        return self

    def add_unique_constraint(
        self, fields: Union[str, List[str]], error_message: Optional[str] = None, collection: Optional[str] = None
    ) -> "DataStore":
        """Adds a unique constraint across one or more fields within a collection."""
        constraint = UniqueConstraint(fields=fields, error_message=error_message, collection=collection)
        self.unique_constraints.append(constraint)

        # Initialize the constraint with existing values
        if collection:
            if collection in self.collections:
                for item in self.collections[collection]:
                    constraint.validate(item)
        else:
            for collection_items in self.collections.values():
                for item in collection_items:
                    constraint.validate(item)

        return self

    def set_timestamp_tracking(self, enabled: bool) -> "DataStore":
        """Enables or disables automatic timestamp tracking for item creation and updates."""
        self.track_timestamps = enabled
        return self

    # --- Core CRUD Operations (Delegated) ---

    def list(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[Union[str, List[str]]] = None,
        sort_desc: Union[bool, List[bool]] = False,
        page: int = 1,
        page_size: Optional[int] = None,
        include_deleted: bool = False,
        include_related: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Lists items from a collection with filtering, sorting, and pagination."""
        return list_items(
            data_store=self,
            collection=collection,
            filters=filters,
            sort_by=sort_by,
            sort_desc=sort_desc,
            page=page,
            page_size=page_size,
            include_deleted=include_deleted,
            include_related=include_related,
            fields=fields,
        )

    def get(
        self,
        collection: str,
        id: Any,
        include_deleted: bool = False,
        include_related: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a single item from a collection by its primary identifier ('id')."""
        return get_item(
            data_store=self,
            collection=collection,
            id=id,
            include_deleted=include_deleted,
            include_related=include_related,
            fields=fields,
        )

    def create(self, collection: str, data: Dict[str, Any], skip_validation: bool = False) -> Dict[str, Any]:
        # Note: create_item handles validation internally based on skip_validation
        """Creates a new item in the specified collection."""
        return create_item(
            data_store=self,
            collection=collection,
            data=data,
            skip_validation=skip_validation,
        )

    def update(
        self, collection: str, id: Any, data: Dict[str, Any], skip_validation: bool = False, check_version: bool = True
    ) -> Optional[Dict[str, Any]]:
        # Note: update_item handles validation internally based on skip_validation
        """Updates an existing item in a collection identified by its ID."""
        return update_item(
            data_store=self,
            collection=collection,
            id=id,
            data=data,
            skip_validation=skip_validation,
            check_version=check_version,
        )

    def delete(self, collection: str, id: Any, soft_delete: bool = False, cascade: bool = False) -> bool:
        """Deletes an item from a collection by its ID."""
        return delete_item(
            data_store=self,
            collection=collection,
            id=id,
            soft_delete=soft_delete,
            cascade=cascade,
        )

    # --- Bulk Operations (Delegated) ---

    def bulk_create(
        self,
        collection: str,
        items: List[Dict[str, Any]],
        skip_validation: bool = False,
    ) -> List[Dict[str, Any]]:
        """Creates multiple items in the specified collection efficiently."""
        return bulk_create_items(
            data_store=self,
            collection=collection,
            items=items,
            skip_validation=skip_validation,
        )

    def bulk_update(
        self,
        collection: str,
        items: List[Dict[str, Any]],
        skip_validation: bool = False,
        check_version: bool = True,
    ) -> List[Optional[Dict[str, Any]]]:
        """Updates multiple items in the specified collection efficiently."""
        return bulk_update_items(
            data_store=self,
            collection=collection,
            items=items,
            skip_validation=skip_validation,
            check_version=check_version,
        )

    def bulk_delete(
        self,
        collection: str,
        ids: List[Any],
        soft_delete: bool = False,
        cascade: bool = False,
    ) -> int:
        """Deletes multiple items from a collection identified by their IDs."""
        return bulk_delete_items(
            data_store=self,
            collection=collection,
            ids=ids,
            soft_delete=soft_delete,
            cascade=cascade,
        )

    # Note: _validate_item method removed as it was unused and internal validation
    # is handled by the validate_item helper or within specific methods.
