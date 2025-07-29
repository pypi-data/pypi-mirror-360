# crudclient/testing/doubles/data_store_definitions.py
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Moved from data_store.py


class ValidationException(Exception):
    """Exception raised for data validation errors."""

    def __init__(self, message: str, errors: Optional[Dict[str, List[str]]] = None):
        super().__init__(message)
        self.errors = errors or {}


# Moved from data_store.py
class Relationship:
    """Defines a relationship between two collections in the DataStore."""

    def __init__(
        self,
        source_collection: str,
        target_collection: str,
        relationship_type: str,
        source_key: str = "id",
        target_key: Optional[str] = None,
        cascade_delete: bool = False,
        bidirectional: bool = False,
        junction_collection: Optional[str] = None,
        source_junction_key: Optional[str] = None,
        target_junction_key: Optional[str] = None,
    ):
        self.source_collection = source_collection
        self.target_collection = target_collection
        self.relationship_type = relationship_type
        self.source_key = source_key

        # For one-to-many, target_key is the foreign key in the target collection
        # For many-to-many, target_key is the key in the target collection to join on
        self.target_key = target_key or f"{source_collection}_{source_key}"

        self.cascade_delete = cascade_delete
        self.bidirectional = bidirectional

        # For many-to-many relationships
        self.junction_collection = junction_collection
        self.source_junction_key = source_junction_key or f"{source_collection}_{source_key}"
        self.target_junction_key = target_junction_key or f"{target_collection}_{self.target_key}"


# Moved from data_store.py
class ValidationRule:
    """Defines a validation rule for a specific field in a collection."""

    def __init__(
        self,
        field: str,
        validator_func: Callable[[Any], bool],
        error_message: str,
        collection: Optional[str] = None,
    ):
        self.field = field
        self.validator_func = validator_func
        self.error_message = error_message
        self.collection = collection

    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """Validates a value using the defined function."""
        is_valid = self.validator_func(value)
        return is_valid, None if is_valid else self.error_message


# Moved from data_store.py
class UniqueConstraint:
    """Defines a unique constraint across one or more fields in a collection."""

    def __init__(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None,
    ):
        self.fields = [fields] if isinstance(fields, str) else fields
        self.error_message = error_message or f"Values for {', '.join(self.fields)} must be unique"
        self.collection = collection
        self._values: Set[str] = set()  # Stores unique value combinations

    def validate(self, item: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Checks if the item violates the unique constraint."""
        composite_key = self._get_composite_key(item)
        if composite_key is None:
            # If any required field is missing, we can't validate uniqueness yet
            return True, None

        if composite_key in self._values:
            return False, self.error_message

        # Add to tracked values
        self._values.add(composite_key)
        return True, None

    def remove_value(self, item: Dict[str, Any]) -> None:
        """Removes an item's value combination from the tracked set."""
        composite_key = self._get_composite_key(item)
        if composite_key is not None and composite_key in self._values:
            self._values.remove(composite_key)

    def _get_composite_key(self, item: Dict[str, Any]) -> Optional[str]:
        """Generates the composite key string for an item."""
        key_parts = []
        for field in self.fields:
            if field not in item:
                return None  # Cannot form key if a field is missing
            key_parts.append(str(item[field]))
        return "|".join(key_parts)
