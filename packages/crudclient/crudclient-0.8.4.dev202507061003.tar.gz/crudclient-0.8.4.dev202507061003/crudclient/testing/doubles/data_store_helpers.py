# import copy # No longer used directly here
import re
from typing import (  # Removed Union, datetime
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)

# RelationshipType class moved to data_store_relationships.py


if TYPE_CHECKING:  # Relationship import no longer needed
    # from .data_store_definitions import Relationship # RelationshipType moved
    from .data_store import DataStore  # Import DataStore for type hinting


def apply_filters(data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Applies various filters to a list of dictionaries."""
    filtered_data = []

    for item in data:
        match = True

        for key, value in filters.items():
            item_value: Optional[Any] = None  # Declare once before if/else
            # Handle nested keys with dot notation
            if "." in key:
                parts = key.split(".")
                current_val: Any = item
                for part in parts:
                    if isinstance(current_val, dict) and part in current_val:
                        current_val = current_val[part]
                    else:
                        current_val = None
                        break
                item_value = current_val
            else:
                item_value = item.get(key)

            # Handle different filter types
            if callable(value):
                # Function filter
                if not value(item_value):
                    match = False
                    break
            elif isinstance(value, dict):
                # Operator filter
                if not apply_operator_filter(item_value, value):
                    match = False
                    break
            elif isinstance(value, str) and value.startswith("regex:"):
                # Regex filter
                pattern = value[6:]
                # Nested check to ensure item_value is str before regex search
                if isinstance(item_value, str):
                    if not re.search(pattern, item_value):
                        match = False
                        break
                else:  # If not a string, it's not a match for regex
                    match = False
                    break
            elif item_value != value:
                # Exact match filter
                match = False
                break

        if match:
            filtered_data.append(item)

    return filtered_data


def _op_eq(value: Any, op_value: Any) -> bool:
    """Check if value equals op_value."""
    return bool(value == op_value)


def _op_ne(value: Any, op_value: Any) -> bool:
    """Check if value does not equal op_value."""
    return bool(value != op_value)


def _op_gt(value: Any, op_value: Any) -> bool:
    """Check if value is greater than op_value."""
    return bool(value > op_value)


def _op_gte(value: Any, op_value: Any) -> bool:
    """Check if value is greater than or equal to op_value."""
    return bool(value >= op_value)


def _op_lt(value: Any, op_value: Any) -> bool:
    """Check if value is less than op_value."""
    return bool(value < op_value)


def _op_lte(value: Any, op_value: Any) -> bool:
    """Check if value is less than or equal to op_value."""
    return bool(value <= op_value)


def _op_in(value: Any, op_value: Any) -> bool:
    """Check if value is in op_value."""
    return bool(value in op_value)


def _op_exists(value: Any, op_value: bool) -> bool:
    """Check if value exists (is not None) when op_value is True,"""
    if op_value:
        return bool(value is not None)
    return bool(value is None)


def _op_regex(value: Any, op_value: str) -> bool:
    """Check if value matches the regex pattern in op_value."""
    return bool(isinstance(value, str) and re.search(op_value, value))


# Map of operators to their handler functions
_OPERATOR_HANDLERS: Dict[str, Callable[[Any, Any], bool]] = {
    "$eq": lambda v, op_v: _op_ne(v, op_v) is False,  # Inverted to match original logic
    "$ne": lambda v, op_v: _op_eq(v, op_v) is False,  # Inverted to match original logic
    "$gt": _op_gt,
    "$gte": _op_gte,
    "$lt": _op_lt,
    "$lte": _op_lte,
    "$in": _op_in,
    "$nin": lambda v, op_v: _op_in(v, op_v) is False,  # Inverted to match original logic
    "$exists": _op_exists,
    "$regex": _op_regex,
}


def apply_operator_filter(value: Any, operators: Dict[str, Any]) -> bool:
    """Applies MongoDB-style operators to filter a value."""
    for op, op_value in operators.items():
        handler = _OPERATOR_HANDLERS.get(op)
        if handler:
            if not handler(value, op_value):
                return False
        # Silently ignore unknown operators to maintain backward compatibility

    return True


# Function apply_sorting moved to data_store_sorting.py


def apply_pagination(data: List[Dict[str, Any]], page: int, page_size: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Applies pagination to a list of data."""
    total_count = len(data)
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1

    # Ensure page is within valid range
    page = max(1, min(page, total_pages))

    # Calculate slice indices
    start = (page - 1) * page_size
    end = min(start + page_size, total_count)

    # Create pagination metadata
    pagination = {"page": page, "page_size": page_size, "total_count": total_count, "total_pages": total_pages}

    return data[start:end], pagination


def apply_field_selection(data: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
    """Selects only the specified fields from a list of dictionaries."""
    return [{k: v for k, v in item.items() if k in fields} for item in data]


def validate_item(data_store: "DataStore", collection: str, item: Dict[str, Any], add_to_constraints: bool = True) -> None:
    """Validates an item against defined validation rules, unique constraints,"""
    errors: Dict[str, List[str]] = {}  # Added type annotation

    # Apply validation rules defined in DataStore
    for rule in data_store.validation_rules:
        if rule.collection is None or rule.collection == collection:
            if rule.field in item:
                value_to_validate = item.get(rule.field)
                # Allow validation of None if the rule is designed for it
                is_valid, error_message = rule.validate(value_to_validate)
                if not is_valid and error_message:  # Ensure error_message is not None
                    if rule.field not in errors:
                        errors[rule.field] = []
                    errors[rule.field].append(error_message)

    # Apply unique constraints defined in DataStore
    for constraint in data_store.unique_constraints:
        if constraint.collection is None or constraint.collection == collection:
            # Temporarily add the value to check for uniqueness
            is_valid, error_message = constraint.validate(item)
            if not is_valid and error_message:  # Ensure error_message is not None
                # If validation failed, immediately remove the value we tried to add
                constraint.remove_value(item)

                # Add the error
                field_name = ", ".join(constraint.fields)
                if field_name not in errors:
                    errors[field_name] = []
                # Avoid duplicate messages if multiple fields involved
                if error_message not in errors[field_name]:
                    errors[field_name].append(error_message)
            elif not add_to_constraints:
                # If we are just validating (e.g., during update before committing),
                # remove the value again so the constraint state isn't permanently changed yet.
                constraint.remove_value(item)

    # Apply referential integrity checks (Foreign Key constraints)
    for relationship in data_store.relationships:
        # Check if the current collection is the 'target' side holding the FK
        if relationship.target_collection == collection:
            fk_field = relationship.target_key
            fk_value = item.get(fk_field)

            # Only check if the FK field exists and has a non-null value
            if fk_field in item and fk_value is not None:
                source_collection_name = relationship.source_collection
                source_key_field = relationship.source_key

                # Check if the referenced item exists in the source collection
                source_collection_data = data_store.collections.get(source_collection_name, [])
                exists = any(
                    source_item.get(source_key_field) == fk_value and not source_item.get(data_store.deleted_field, False)
                    for source_item in source_collection_data
                )

                if not exists:
                    error_message = f"Referenced item with {source_key_field}={fk_value} not found in {source_collection_name}."
                    if fk_field not in errors:
                        errors[fk_field] = []
                    errors[fk_field].append(error_message)

        # Add check for ONE_TO_ONE where FK might be on the source side if defined that way
        # (Less common, but possible)
        # elif relationship.source_collection == collection and relationship.relationship_type == RelationshipType.ONE_TO_ONE:
        #    # Similar logic if FK is defined on the source side
        #    pass # Add if needed based on specific relationship definitions

    # If there are errors, raise an exception
    if errors:
        # Import ValidationException at the top level if needed by other functions
        from .data_store_definitions import ValidationException

        raise ValidationException("Validation failed", errors)


# cascade_delete function moved to data_store_relationships.py


# Functions include_related_data and include_related_item moved to data_store_relationships.py
# Import them if needed elsewhere, or adjust calls in data_store_crud.py etc.
# (Note: They are already used in data_store_crud.py, which imports them directly)
# cascade_delete is now also imported in data_store_crud.py from data_store_relationships.py
