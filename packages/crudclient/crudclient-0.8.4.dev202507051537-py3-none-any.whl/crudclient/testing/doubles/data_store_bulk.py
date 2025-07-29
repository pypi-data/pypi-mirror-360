# crudclient/testing/doubles/data_store_bulk.py
import copy
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .data_store_helpers import validate_item

if TYPE_CHECKING:
    from .data_store import DataStore  # Avoid circular import


def bulk_create_items(
    data_store: "DataStore",
    collection: str,
    items: List[Dict[str, Any]],
    skip_validation: bool = False,
) -> List[Dict[str, Any]]:
    """Creates multiple items in the specified collection."""
    created_items = []
    items_to_create = []

    # First validate all items to ensure atomicity
    if not skip_validation:
        temp_unique_constraints = copy.deepcopy(data_store.unique_constraints)
        try:
            for item in items:
                item_copy = copy.deepcopy(item)
                if "id" not in item_copy:
                    item_copy["id"] = str(uuid.uuid4())

                # Validate using temporary constraints to check for conflicts within the batch
                # Pass the data_store instance, but override constraints for batch check
                temp_data_store_view = copy.copy(data_store)  # Shallow copy is enough
                temp_data_store_view.unique_constraints = temp_unique_constraints
                validate_item(
                    temp_data_store_view,  # Pass modified view with temp constraints
                    collection,
                    item_copy,
                    add_to_constraints=True,  # Add to temp constraints for batch check
                )
                # Restore original constraints on the actual data_store instance
                # (validate_item might have added to the temp list if successful)
                items_to_create.append(item_copy)  # Store validated copy with potential new ID
            # If validation passes for all, proceed with creation using original items
            # (or copies if IDs were generated)
            if not items_to_create:  # If IDs were provided
                items_to_create = items

        except Exception as e:
            # If validation fails, re-raise the exception
            raise e
    else:
        items_to_create = items  # Skip validation, use original items

    # Then create all items using the main create method (which handles actual constraint update)
    for item_data in items_to_create:
        # Use the potentially ID-added item_data if validation ran, else original item
        # Pass skip_validation=True because batch validation was already done (or skipped)
        created_item = data_store.create(collection, item_data, skip_validation=True)
        created_items.append(created_item)

    return created_items


def bulk_update_items(
    data_store: "DataStore",
    collection: str,
    items: List[Dict[str, Any]],
    skip_validation: bool = False,
    check_version: bool = True,
) -> List[Optional[Dict[str, Any]]]:
    """Updates multiple items in the specified collection."""
    updated_items_results: List[Optional[Dict[str, Any]]] = []  # Added type annotation
    updates_to_perform = []  # Store tuples of (id, data_to_update)

    # First validate all items to ensure atomicity
    if not skip_validation:
        temp_unique_constraints = copy.deepcopy(data_store.unique_constraints)
        original_items_map = {item["id"]: item for item in data_store.get_collection(collection) if "id" in item}

        try:
            for item_update_data in items:
                item_id = item_update_data.get("id")
                if item_id is None:
                    # Cannot update without ID, mark as None in results later
                    continue

                existing_item = original_items_map.get(item_id)
                if not existing_item or existing_item.get(data_store.deleted_field, False):
                    # Item doesn't exist or is deleted, mark as None
                    continue

                # Prepare the potential updated state for validation
                prospective_update = copy.deepcopy(existing_item)
                prospective_update.update(item_update_data)

                # Remove the original item's value from temp constraints
                for constraint in temp_unique_constraints:
                    if constraint.collection is None or constraint.collection == collection:
                        constraint.remove_value(existing_item)

                # Validate the prospective update using temporary constraints
                # Pass the data_store instance, but override constraints for batch check
                temp_data_store_view = copy.copy(data_store)  # Shallow copy is enough
                temp_data_store_view.unique_constraints = temp_unique_constraints
                validate_item(
                    temp_data_store_view,  # Pass modified view with temp constraints
                    collection,
                    prospective_update,
                    add_to_constraints=True,  # Add updated value to temp constraints
                )
                # Restore original constraints on the actual data_store instance
                # (validate_item might have added to the temp list if successful)
                updates_to_perform.append((item_id, item_update_data))

        except Exception as e:
            # If validation fails, re-raise the exception
            raise e
    else:
        # Skip validation, prepare all updates with IDs
        updates_to_perform = [(item.get("id"), item) for item in items if item.get("id") is not None]

    # Then perform all updates
    update_map = {item_id: data for item_id, data in updates_to_perform}
    for item_data in items:  # Iterate original request order to maintain result order
        item_id = item_data.get("id")
        if item_id is None or item_id not in update_map:
            updated_items_results.append(None)
            continue

        # Use the main update method, skipping validation as it was done/skipped
        updated_item = data_store.update(
            collection,
            item_id,
            update_map[item_id],  # Use the validated data
            skip_validation=True,
            check_version=check_version,
        )
        updated_items_results.append(updated_item)

    return updated_items_results


def bulk_delete_items(
    data_store: "DataStore",
    collection: str,
    ids: List[Any],
    soft_delete: bool = False,
    cascade: bool = False,
) -> int:
    """Deletes multiple items by ID."""
    deleted_count = 0
    items_to_delete = []
    collection_data = data_store.get_collection(collection)
    ids_set = set(ids)  # Faster lookup

    # Pre-check: Find existing, non-deleted items matching the IDs
    for item in collection_data:
        item_id = item.get("id")
        if item_id in ids_set and not item.get(data_store.deleted_field, False):
            items_to_delete.append(item)  # Store the actual item

    # Perform delete on found items
    # Note: Still not fully atomic if cascade fails midway
    for item_to_delete in items_to_delete:
        item_id = item_to_delete.get("id")  # Get ID from the found item
        # The delete function internally handles checking if it's already deleted again,
        # but our pre-check avoids unnecessary calls.
        if data_store.delete(collection, item_id, soft_delete, cascade):
            deleted_count += 1

    return deleted_count
