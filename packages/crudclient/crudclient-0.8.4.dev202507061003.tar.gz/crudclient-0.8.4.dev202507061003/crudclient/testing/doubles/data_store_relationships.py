# crudclient/testing/doubles/data_store_relationships.py
import copy
from typing import TYPE_CHECKING, Any, Dict, List

from .data_store_definitions import Relationship  # Import Relationship
from .data_store_relationship_helpers import (
    handle_many_to_many_junction,
    handle_many_to_many_targets,
    handle_one_to_many_cascade,
    handle_one_to_one_cascade,
)

# RelationshipType is now defined in this file
# from .data_store_helpers import RelationshipType # Removed import

if TYPE_CHECKING:
    # Avoid circular import with DataStore if Relationship definition moves
    # from .data_store import DataStore
    pass


class RelationshipType:
    """Defines the types of relationships between collections."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"


def include_related_data(
    collection: str,
    data: List[Dict[str, Any]],
    include_related: List[str],
    relationships: List[Relationship],  # Use imported Relationship
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str = "_deleted",
) -> List[Dict[str, Any]]:
    """Includes related data for a list of items based on defined relationships."""
    result = []
    for item in data:
        result.append(include_related_item(collection, item, include_related, relationships, collections, deleted_field))
    return result


def include_related_item(
    collection: str,
    item: Dict[str, Any],
    include_related: List[str],
    relationships: List[Relationship],  # Use imported Relationship
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str = "_deleted",
) -> Dict[str, Any]:
    """Includes related data for a single item based on defined relationships."""
    result = copy.deepcopy(item)

    for related_name in include_related:
        # Find the relationship definition
        relationship = None
        for rel in relationships:
            # Check both forward and bidirectional reverse relationships
            if (rel.source_collection == collection and rel.target_collection == related_name) or (
                rel.bidirectional and rel.target_collection == collection and rel.source_collection == related_name
            ):
                relationship = rel
                break

        if not relationship:
            # No relationship defined for this include, skip
            continue

        # Determine if we are looking forward (source=collection) or backward (target=collection)
        is_forward_relation = relationship.source_collection == collection

        # Get the related data based on relationship type
        if relationship.relationship_type == RelationshipType.ONE_TO_ONE:
            related_items = _get_related_one_to_one(item, relationship, collections, deleted_field, is_forward_relation, related_name)
            result[related_name] = copy.deepcopy(related_items[0]) if related_items else None

        elif relationship.relationship_type == RelationshipType.ONE_TO_MANY:
            related_items = _get_related_one_to_many(item, relationship, collections, deleted_field, is_forward_relation, related_name)
            if is_forward_relation:  # one-to-many returns a list
                result[related_name] = copy.deepcopy(related_items)
            else:  # many-to-one returns a single item or None
                result[related_name] = copy.deepcopy(related_items[0]) if related_items else None

        elif relationship.relationship_type == RelationshipType.MANY_TO_MANY:
            related_items = _get_related_many_to_many(item, relationship, collections, deleted_field, is_forward_relation, related_name)
            result[related_name] = copy.deepcopy(related_items)

    return result


# --- Helper functions for include_related_item ---


def _get_related_one_to_one(
    item: Dict[str, Any],
    relationship: Relationship,
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str,
    is_forward_relation: bool,
    related_name: str,
) -> List[Dict[str, Any]]:
    if is_forward_relation:
        target_collection_name = related_name
        source_key = relationship.source_key
        target_key = relationship.target_key
        item_key_value = item.get(source_key)
    else:  # Reverse relationship
        target_collection_name = relationship.source_collection
        source_key = relationship.target_key  # Key in the 'item' (which is the target in the relationship def)
        target_key = relationship.source_key  # Key in the related items (source in relationship def)
        item_key_value = item.get(source_key)

    if target_collection_name not in collections or item_key_value is None:
        return []

    target_items = collections[target_collection_name]
    return [i for i in target_items if i.get(target_key) == item_key_value and not i.get(deleted_field, False)]


def _get_related_one_to_many(
    item: Dict[str, Any],
    relationship: Relationship,
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str,
    is_forward_relation: bool,
    related_name: str,
) -> List[Dict[str, Any]]:
    if is_forward_relation:  # one(item)-to-many(related_name)
        target_collection_name = related_name
        source_key = relationship.source_key
        target_key = relationship.target_key
        item_key_value = item.get(source_key)
    else:  # many(related_name)-to-one(item)
        target_collection_name = relationship.source_collection
        source_key = relationship.target_key  # Key in the 'item'
        target_key = relationship.source_key  # Key in the related items
        item_key_value = item.get(source_key)

    if target_collection_name not in collections or item_key_value is None:
        return []

    target_items = collections[target_collection_name]
    return [i for i in target_items if i.get(target_key) == item_key_value and not i.get(deleted_field, False)]


def _get_related_many_to_many(
    item: Dict[str, Any],
    relationship: Relationship,
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str,
    is_forward_relation: bool,
    related_name: str,
) -> List[Dict[str, Any]]:
    if not relationship.junction_collection or relationship.junction_collection not in collections:
        return []

    junction_items = collections[relationship.junction_collection]

    if is_forward_relation:
        source_key = relationship.source_key
        junction_source_key = relationship.source_junction_key
        junction_target_key = relationship.target_junction_key
        target_collection_name = related_name
        target_key = relationship.target_key
        item_key_value = item.get(source_key)
    else:  # Reverse relationship
        source_key = relationship.target_key  # Key in the 'item'
        junction_source_key = relationship.target_junction_key  # Key in junction table pointing to 'item'
        junction_target_key = relationship.source_junction_key  # Key in junction table pointing to related items
        target_collection_name = relationship.source_collection
        target_key = relationship.source_key  # Key in the related items
        item_key_value = item.get(source_key)

    if item_key_value is None:
        return []

    # Find matching entries in the junction table
    junction_matches = [i for i in junction_items if i.get(junction_source_key or "") == item_key_value and not i.get(deleted_field, False)]

    # Get the IDs of the related items from the junction table
    related_ids = {i.get(junction_target_key or "") for i in junction_matches if i.get(junction_target_key or "") is not None}

    if target_collection_name not in collections:
        return []

    # Get the actual related items
    target_items = collections[target_collection_name]
    return [i for i in target_items if i.get(target_key) in related_ids and not i.get(deleted_field, False)]


def cascade_delete(
    collection: str,
    item: Dict[str, Any],
    relationships: List[Relationship],
    collections: Dict[str, List[Dict[str, Any]]],
    soft_delete: bool = False,
    deleted_field: str = "_deleted",
    updated_at_field: str = "_updated_at",
) -> None:
    # Find relationships where this collection is the source
    """Performs cascading deletes based on relationship definitions."""
    for relationship in relationships:
        if relationship.source_collection != collection or not relationship.cascade_delete:
            continue

        source_key_value = item.get(relationship.source_key)
        if source_key_value is None:
            continue

        target_collection = relationship.target_collection
        if target_collection not in collections:
            continue

        target_items = collections[target_collection]

        if relationship.relationship_type == RelationshipType.ONE_TO_ONE:
            handle_one_to_one_cascade(source_key_value, relationship, target_items, soft_delete, deleted_field, updated_at_field)

        elif relationship.relationship_type == RelationshipType.ONE_TO_MANY:
            handle_one_to_many_cascade(source_key_value, relationship, target_items, soft_delete, deleted_field, updated_at_field)

        elif relationship.relationship_type == RelationshipType.MANY_TO_MANY:
            # For many-to-many, we need to handle the junction table
            if not relationship.junction_collection:
                continue

            junction_collection = relationship.junction_collection
            if junction_collection not in collections:
                continue

            junction_items = collections[junction_collection]

            # Process junction table and get target IDs
            target_ids = handle_many_to_many_junction(source_key_value, relationship, junction_items, soft_delete, deleted_field, updated_at_field)

            # Handle target items if needed
            if relationship.cascade_delete and target_ids:
                handle_many_to_many_targets(target_ids, relationship, target_items, soft_delete, deleted_field, updated_at_field)
