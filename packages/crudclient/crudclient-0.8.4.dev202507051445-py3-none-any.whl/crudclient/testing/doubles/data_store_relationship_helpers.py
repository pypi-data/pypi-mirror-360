# crudclient/testing/doubles/data_store_relationship_helpers.py
from datetime import datetime
from typing import Any, Dict, List


def perform_soft_delete(item: Dict[str, Any], deleted_field: str = "_deleted", updated_at_field: str = "_updated_at") -> None:
    """Mark an item as deleted (soft delete)."""
    item[deleted_field] = True
    item[updated_at_field] = datetime.now().isoformat()


def delete_items_by_indices(items: List[Dict[str, Any]], indices: List[int]) -> None:
    """Delete items from a list using their indices in reverse order."""
    for i in reversed(indices):
        del items[i]


def handle_one_to_one_cascade(
    source_key_value: Any,
    relationship: Any,  # Using Any to avoid circular import
    target_items: List[Dict[str, Any]],
    soft_delete: bool,
    deleted_field: str,
    updated_at_field: str,
) -> None:
    """Handle cascade delete for one-to-one relationships."""
    for i, target_item in enumerate(target_items):
        if target_item.get(relationship.target_key) == source_key_value:
            if soft_delete:
                perform_soft_delete(target_item, deleted_field, updated_at_field)
            else:
                del target_items[i]
            break


def handle_one_to_many_cascade(
    source_key_value: Any,
    relationship: Any,  # Using Any to avoid circular import
    target_items: List[Dict[str, Any]],
    soft_delete: bool,
    deleted_field: str,
    updated_at_field: str,
) -> None:
    """Handle cascade delete for one-to-many relationships."""
    indices_to_delete = []

    for i, target_item in enumerate(target_items):
        if target_item.get(relationship.target_key) == source_key_value:
            if soft_delete:
                perform_soft_delete(target_item, deleted_field, updated_at_field)
            else:
                indices_to_delete.append(i)

    if not soft_delete:
        delete_items_by_indices(target_items, indices_to_delete)


def handle_many_to_many_junction(
    source_key_value: Any,
    relationship: Any,  # Using Any to avoid circular import
    junction_items: List[Dict[str, Any]],
    soft_delete: bool,
    deleted_field: str,
    updated_at_field: str,
) -> List[Any]:
    """Handle junction table for many-to-many relationships and return target IDs."""
    junction_indices_to_delete = []
    target_ids = []

    for i, junction_item in enumerate(junction_items):
        source_junction_key = relationship.source_junction_key or ""
        target_junction_key = relationship.target_junction_key or ""

        if junction_item.get(source_junction_key) == source_key_value:
            target_id = junction_item.get(target_junction_key)
            if target_id is not None:
                target_ids.append(target_id)

            if soft_delete:
                perform_soft_delete(junction_item, deleted_field, updated_at_field)
            else:
                junction_indices_to_delete.append(i)

    if not soft_delete:
        delete_items_by_indices(junction_items, junction_indices_to_delete)

    return target_ids


def handle_many_to_many_targets(
    target_ids: List[Any],
    relationship: Any,  # Using Any to avoid circular import
    target_items: List[Dict[str, Any]],
    soft_delete: bool,
    deleted_field: str,
    updated_at_field: str,
) -> None:
    """Handle target items deletion for many-to-many relationships."""
    target_indices_to_delete = []

    for i, target_item in enumerate(target_items):
        target_key_value = target_item.get(relationship.target_key)
        if target_key_value in target_ids:
            if soft_delete:
                perform_soft_delete(target_item, deleted_field, updated_at_field)
            else:
                target_indices_to_delete.append(i)

    if not soft_delete:
        delete_items_by_indices(target_items, target_indices_to_delete)
