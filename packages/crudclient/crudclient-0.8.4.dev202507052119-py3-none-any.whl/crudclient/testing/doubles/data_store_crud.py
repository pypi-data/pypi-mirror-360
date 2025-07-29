# crudclient/testing/doubles/data_store_crud.py
import copy
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .data_store_helpers import (  # Removed include_related_*, apply_sorting, cascade_delete; apply_sorting, # Moved; cascade_delete, # Moved
    apply_field_selection,
    apply_filters,
    apply_pagination,
    validate_item,
)
from .data_store_relationships import cascade_delete  # Added import
from .data_store_relationships import include_related_data, include_related_item
from .data_store_sorting import apply_sorting  # Added import for sorting helper

if TYPE_CHECKING:
    from .data_store import DataStore  # Avoid circular import


def list_items(
    data_store: "DataStore",
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
    """Lists items from a collection with filtering, sorting, pagination,"""
    data = data_store.get_collection(collection)

    # Filter out soft-deleted items unless explicitly included
    if not include_deleted and data_store.deleted_field:
        data = [item for item in data if not item.get(data_store.deleted_field, False)]

    # Apply filters
    if filters:
        data = apply_filters(data, filters)

    # Get total count before pagination
    total_count = len(data)

    # Apply sorting
    if sort_by:
        data = apply_sorting(data, sort_by, sort_desc)

    # Apply pagination
    if page_size:
        data, pagination = apply_pagination(data, page, page_size)
    else:
        pagination = {"page": 1, "page_size": total_count, "total_count": total_count, "total_pages": 1}

    # Apply field selection
    if fields:
        data = apply_field_selection(data, fields)

    # Include related data if requested
    if include_related:
        data = include_related_data(collection, data, include_related, data_store.relationships, data_store.collections, data_store.deleted_field)

    # Return a deep copy to prevent modification of the original data
    return {"data": copy.deepcopy(data), "meta": pagination}


def get_item(
    data_store: "DataStore",
    collection: str,
    id: Any,
    include_deleted: bool = False,
    include_related: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Gets a single item by ID."""
    data = data_store.get_collection(collection)

    for item in data:
        if item.get("id") == id:
            # Check if item is soft-deleted
            if not include_deleted and item.get(data_store.deleted_field, False):
                return None

            result = copy.deepcopy(item)

            # Include related data if requested
            if include_related:
                result = include_related_item(
                    collection, result, include_related, data_store.relationships, data_store.collections, data_store.deleted_field
                )

            # Apply field selection
            if fields:
                result = {k: v for k, v in result.items() if k in fields}

            return result

    return None


def create_item(data_store: "DataStore", collection: str, data: Dict[str, Any], skip_validation: bool = False) -> Dict[str, Any]:
    """Creates a single item in a collection."""
    collection_data = data_store.get_collection(collection)

    # Create a copy to avoid modifying the original
    new_item = copy.deepcopy(data)

    # Generate ID if not provided
    if "id" not in new_item:
        new_item["id"] = str(uuid.uuid4())

    # Add version if tracking is enabled
    if data_store.version_field:
        new_item[data_store.version_field] = 1

    # Add timestamps if tracking is enabled
    if data_store.track_timestamps:
        now = datetime.now().isoformat()
        new_item[data_store.created_at_field] = now
        new_item[data_store.updated_at_field] = now

    # Validate the item
    if not skip_validation:
        # Pass the whole data_store instance now
        validate_item(data_store, collection, new_item)

    # Add the item to the collection
    collection_data.append(new_item)

    # Return a deep copy to prevent modification of the original
    return copy.deepcopy(new_item)


def update_item(
    data_store: "DataStore", collection: str, id: Any, data: Dict[str, Any], skip_validation: bool = False, check_version: bool = True
) -> Optional[Dict[str, Any]]:
    """Updates a single item by ID."""
    collection_data = data_store.get_collection(collection)

    for i, item in enumerate(collection_data):
        if item.get("id") == id:
            # Check if item is soft-deleted
            if item.get(data_store.deleted_field, False):
                return None

            # Check version if enabled
            if check_version and data_store.version_field:
                current_version = item.get(data_store.version_field, 1)
                if data_store.version_field in data:
                    provided_version = data.get(data_store.version_field)
                    if provided_version != current_version:
                        raise ValueError(f"Version conflict: expected {current_version}, got {provided_version}")

            # Create a copy of the original item
            updated_item = copy.deepcopy(item)

            # Update with new data
            updated_item.update(data)

            # Ensure ID is preserved
            updated_item["id"] = id

            # Update version if tracking is enabled
            if data_store.version_field:
                updated_item[data_store.version_field] = item.get(data_store.version_field, 1) + 1

            # Update timestamp if tracking is enabled
            if data_store.track_timestamps and data_store.updated_at_field:
                updated_item[data_store.updated_at_field] = datetime.now().isoformat()

            # Validate the updated item
            if not skip_validation:
                # First remove the old item's values from unique constraints
                for constraint in data_store.unique_constraints:
                    if constraint.collection is None or constraint.collection == collection:
                        constraint.remove_value(item)

                # Then validate the new item (pass the whole data_store instance)
                # The validate_item function now handles adding the value to constraints if valid
                validate_item(data_store, collection, updated_item)

            # Replace the item in the collection
            collection_data[i] = updated_item

            return copy.deepcopy(updated_item)

    return None


def delete_item(data_store: "DataStore", collection: str, id: Any, soft_delete: bool = False, cascade: bool = False) -> bool:
    """Deletes a single item by ID."""
    collection_data = data_store.get_collection(collection)

    for i, item in enumerate(collection_data):
        if item.get("id") == id:
            # Check if already soft-deleted
            if item.get(data_store.deleted_field, False):
                return False

            # Handle cascading deletes if enabled
            if cascade:
                cascade_delete(
                    collection,
                    item,
                    data_store.relationships,
                    data_store.collections,
                    soft_delete,
                    data_store.deleted_field,
                    data_store.updated_at_field,
                )

            if soft_delete:
                # Perform soft delete
                item[data_store.deleted_field] = True
                item[data_store.updated_at_field] = datetime.now().isoformat()

                # Add to deleted items collection
                if collection not in data_store.deleted_items:
                    data_store.deleted_items[collection] = []
                data_store.deleted_items[collection].append(copy.deepcopy(item))
            else:
                # Perform hard delete
                # Remove the item's values from unique constraints
                for constraint in data_store.unique_constraints:
                    if constraint.collection is None or constraint.collection == collection:
                        constraint.remove_value(item)

                del collection_data[i]

            return True

    return False
