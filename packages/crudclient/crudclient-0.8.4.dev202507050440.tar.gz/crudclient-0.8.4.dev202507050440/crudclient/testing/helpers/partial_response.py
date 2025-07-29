import copy
from typing import Any, Dict, List, Optional, Set


class PartialResponseHelper:
    """
    Helper class for creating partial API responses by selecting specific fields.

    Allows clients to request only the fields they need, reducing response size
    and improving performance. Supports field selection using dot notation,
    wildcards, exclusions, and depth limiting.
    """

    full_response: Dict[str, Any]
    field_separator: str
    wildcard_char: str
    default_fields: List[str]

    def __init__(
        self, full_response: Dict[str, Any], field_separator: str = ".", wildcard_char: str = "*", default_fields: Optional[List[str]] = None
    ) -> None:
        """
        Initialize a PartialResponseHelper instance.

        Args:
            full_response: The complete response data
            field_separator: Character used to separate nested field paths (e.g., "user.address.city")
            wildcard_char: Character used for wildcard matching (e.g., "user.*.name")
            default_fields: Default fields to include if none are specified
        """
        self.full_response = full_response
        self.field_separator = field_separator
        self.wildcard_char = wildcard_char
        self.default_fields = default_fields or []

    def get_partial_response(
        self,
        fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        include_metadata: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a partial response containing only the requested fields.

        Args:
            fields: List of field paths to include (using dot notation)
            exclude_fields: List of field paths to exclude
            max_depth: Maximum depth of nested objects to include
            include_metadata: Whether to include metadata about the partial response

        Returns:
            A dictionary containing only the requested fields from the full response.
            If include_metadata is True, the result will be wrapped in a dictionary
            with 'data' and '_metadata' keys.

        Examples:
            ```python
            # Include specific fields
            helper.get_partial_response(fields=["id", "name", "address.city"])

            # Use wildcards to include all fields at a certain level
            helper.get_partial_response(fields=["user.*"])

            # Include fields but exclude some
            helper.get_partial_response(
                fields=["user.*"],
                exclude_fields=["user.password"]
            )

            # Limit depth of nested objects
            helper.get_partial_response(max_depth=2)
            ```
        """
        # Use default fields if none provided
        fields_to_use = fields or self.default_fields

        # Handle different parameter combinations
        if not fields_to_use and exclude_fields:
            # Only exclusions provided
            result = self._handle_exclusions_only(exclude_fields)
        elif not fields_to_use:
            # No fields specified and no exclusions
            result = {}
        else:
            # Process included fields
            result = self._process_included_fields(fields_to_use)

            # Apply exclusions if specified
            if exclude_fields:
                self._apply_exclusions(result, exclude_fields)

        # Apply max depth if specified
        if max_depth is not None:
            result = self._limit_depth(result, max_depth)

        # Add metadata if requested
        if include_metadata:
            result = self._add_metadata(result, fields_to_use, exclude_fields, max_depth)

        return result

    def _handle_exclusions_only(self, exclude_fields: List[str]) -> Dict[str, Any]:
        """
        Handle the case where only exclusions are provided.

        Creates a copy of the full response and removes the excluded fields.

        Args:
            exclude_fields: List of field paths to exclude

        Returns:
            A copy of the full response with excluded fields removed
        """
        result = self._deep_copy(self.full_response)
        self._apply_exclusions(result, exclude_fields)
        return result

    def _apply_exclusions(self, data: Dict[str, Any], exclude_fields: List[str]) -> None:
        """
        Apply exclusions to the data.

        Removes all fields specified in exclude_fields from the data.

        Args:
            data: The data to modify
            exclude_fields: List of field paths to exclude
        """
        for field_path in exclude_fields:
            self._remove_field(data, field_path)

    def _process_included_fields(self, fields_to_use: List[str]) -> Dict[str, Any]:
        """
        Process the included fields and build the result.

        Builds a new dictionary containing only the specified fields.

        Args:
            fields_to_use: List of field paths to include

        Returns:
            A dictionary containing only the specified fields
        """
        result: Dict[str, Any] = {}

        for field_path in fields_to_use:
            if self.wildcard_char in field_path:
                self._process_wildcard_field(result, field_path)
            else:
                self._process_single_field(result, field_path)

        return result

    def _process_single_field(self, result: Dict[str, Any], field_path: str) -> None:
        """
        Process a single field path and add it to the result if it exists.

        Navigates to the field in the full response and adds it to the result
        with the same nested structure.

        Args:
            result: The result dictionary to update
            field_path: The field path to process
        """
        parts = field_path.split(self.field_separator)
        value = self.full_response

        try:
            # Navigate to the nested value
            for part in parts[:-1]:
                if not isinstance(value, dict) or part not in value:
                    # Path doesn't exist
                    return
                value = value[part]

            # We got through all parts except the last one
            last_part = parts[-1]
            if isinstance(value, dict) and last_part in value:
                # Build the nested structure in the result
                self._build_nested_structure(result, parts, value[last_part])
        except (KeyError, TypeError):
            # Skip fields that don't exist or can't be accessed
            pass

    def _build_nested_structure(self, result: Dict[str, Any], parts: List[str], final_value: Any) -> None:
        """
        Build a nested structure in the result dictionary.

        Creates the necessary nested dictionaries in the result and sets the final value.

        Args:
            result: The result dictionary to update
            parts: The parts of the field path
            final_value: The value to set at the end of the path
        """
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = final_value

    def _process_wildcard_field(self, result: Dict[str, Any], field_path: str) -> None:
        """
        Process a field path containing wildcards and add matching fields to the result.

        Args:
            result: The result dictionary to update
            field_path: The field path with wildcards
        """
        parts = field_path.split(self.field_separator)

        # Find all matching paths
        matching_paths = self._find_matching_paths(self.full_response, parts)

        # Add each matching path to the result
        for path in matching_paths:
            path_parts = path.split(self.field_separator)
            value = self.full_response

            # Navigate to the value
            valid_path = True
            for part in path_parts:
                if not isinstance(value, dict) or part not in value:
                    valid_path = False
                    break
                value = value[part]

            if valid_path:
                # Build the nested structure in the result
                self._build_nested_structure(result, path_parts, value)

    def _find_matching_paths(self, data: Any, pattern_parts: List[str], current_path: str = "") -> Set[str]:
        """
        Find all paths in the data that match the given pattern parts.

        Args:
            data: The data to search in
            pattern_parts: The parts of the pattern to match
            current_path: The current path being built

        Returns:
            A set of field paths that match the pattern
        """
        if not isinstance(data, dict):
            return set()

        if not pattern_parts:
            return {current_path} if current_path else set()

        result = set()
        current_part = pattern_parts[0]
        remaining_parts = pattern_parts[1:]

        if current_part == self.wildcard_char:
            # Wildcard matches all keys at this level
            for key in data:
                new_path = key if not current_path else f"{current_path}{self.field_separator}{key}"
                if remaining_parts:
                    # Continue matching with remaining parts
                    if isinstance(data[key], dict):
                        result.update(self._find_matching_paths(data[key], remaining_parts, new_path))
                else:
                    # End of pattern, add this path
                    result.add(new_path)
        elif current_part in data:
            # Exact match
            new_path = current_part if not current_path else f"{current_path}{self.field_separator}{current_part}"
            if remaining_parts:
                # Continue matching with remaining parts
                if isinstance(data[current_part], dict):
                    result.update(self._find_matching_paths(data[current_part], remaining_parts, new_path))
            else:
                # End of pattern, add this path
                result.add(new_path)

        return result

    def _remove_field(self, data: Dict[str, Any], field_path: str) -> None:
        """
        Remove a field from the data by its path.

        Args:
            data: The data to modify
            field_path: The path of the field to remove
        """
        parts = field_path.split(self.field_separator)

        if len(parts) == 1:
            # Direct field at the top level
            if parts[0] in data:
                del data[parts[0]]
        else:
            # Nested field
            current = data
            for part in parts[:-1]:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    # Path doesn't exist
                    return

            # Remove the last part
            last_part = parts[-1]
            if isinstance(current, dict) and last_part in current:
                del current[last_part]

    def _limit_depth(self, data: Dict[str, Any], max_depth: int, current_depth: int = 0) -> Dict[str, Any]:
        """
        Limit the depth of nested objects in the data.

        Args:
            data: The data to limit
            max_depth: The maximum depth to allow
            current_depth: The current depth in the recursion

        Returns:
            A copy of the data with depth limited to max_depth
        """
        if not isinstance(data, dict) or current_depth >= max_depth:
            return data

        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                if current_depth < max_depth - 1:
                    result[key] = self._limit_depth(value, max_depth, current_depth + 1)
                else:
                    # At max depth, include only a summary
                    result[key] = {"_summary": f"Object with {len(value)} properties"}
            else:
                result[key] = value

        return result

    def _add_metadata(
        self, result: Dict[str, Any], included_fields: Optional[List[str]], excluded_fields: Optional[List[str]], max_depth: Optional[int]
    ) -> Dict[str, Any]:
        """
        Add metadata about the partial response.

        Args:
            result: The partial response data
            included_fields: The fields that were included
            excluded_fields: The fields that were excluded
            max_depth: The maximum depth that was applied

        Returns:
            A dictionary with 'data' and '_metadata' keys
        """
        metadata = {
            "partial_response": True,
            "total_fields_in_full_response": self._count_fields(self.full_response),
            "fields_included": len(included_fields) if included_fields else 0,
            "fields_excluded": len(excluded_fields) if excluded_fields else 0,
        }

        if max_depth is not None:
            metadata["max_depth"] = max_depth

        return {"data": result, "_metadata": metadata}

    def _count_fields(self, data: Any, prefix: str = "") -> int:
        """
        Count the total number of fields in the data.

        Args:
            data: The data to count fields in
            prefix: The prefix for the current path

        Returns:
            The total number of fields
        """
        if not isinstance(data, dict):
            return 1

        count = 0
        for key, value in data.items():
            field_name = key if not prefix else f"{prefix}{self.field_separator}{key}"
            if isinstance(value, dict):
                count += self._count_fields(value, field_name)
            else:
                count += 1

        return count

    def _deep_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deep copy of the data.

        Args:
            data: The data to copy

        Returns:
            A deep copy of the data
        """
        return copy.deepcopy(data)
