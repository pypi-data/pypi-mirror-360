# crudclient/testing/doubles/data_store_sorting.py
from typing import Any, Dict, List, Tuple, Union


def apply_sorting(data: List[Dict[str, Any]], sort_by: Union[str, List[str]], sort_desc: Union[bool, List[bool]]) -> List[Dict[str, Any]]:
    """Sorts a list of dictionaries based on specified fields and directions."""
    if not data:
        return data

    # --- Normalize sort parameters ---
    if isinstance(sort_by, str):
        sort_by_list = [sort_by]
        sort_desc_list = [sort_desc] if isinstance(sort_desc, bool) else [False]  # Default desc to False if single sort_by
    else:
        sort_by_list = sort_by
        if isinstance(sort_desc, bool):
            sort_desc_list = [sort_desc] * len(sort_by_list)
        elif len(sort_desc) < len(sort_by_list):
            # Pad sort_desc with False if shorter than sort_by
            sort_desc_list = sort_desc + [False] * (len(sort_by_list) - len(sort_desc))
        else:
            sort_desc_list = sort_desc[: len(sort_by_list)]  # Truncate if longer

    # --- Perform multi-level sort ---
    # Python's sort is stable, so we can sort by each key in reverse order of significance
    # However, a single sort with a multi-level key function is generally more efficient.

    # Sort using a single multi-level key
    # sorted_data = sorted(data, key=multi_level_key)  # Original single-pass approach

    # Apply reverse order where specified (needs careful handling for stability)
    # Since the primary sort handles None placement, we only need to reverse sections
    # based on the sort_desc_list flags. A simpler stable approach for multi-key reverse
    # is often to sort multiple times or use a more complex key/cmp function.
    # Let's use the multi-pass stable sort approach:

    temp_data = data[:]  # Work on a copy
    for i in range(len(sort_by_list) - 1, -1, -1):
        # Create a key function for *only* the current level
        def get_single_level_key(item: Dict[str, Any], level: int = i) -> Tuple[int, Any]:
            # Replicating part of the multi-level sort logic for a single field
            field = sort_by_list[level]
            value: Any = None
            if "." in field:
                parts = field.split(".")
                current_val: Any = item
                for part in parts:
                    if isinstance(current_val, dict) and part in current_val:
                        current_val = current_val[part]
                    else:
                        current_val = None
                        break
                value = current_val
            else:
                value = item.get(field)

            if value is None:
                return (1, None)
            else:
                return (0, value)

        temp_data.sort(key=get_single_level_key, reverse=sort_desc_list[i])

    return temp_data

    # --- Alternative (potentially less stable or more complex) reverse logic ---
    # This was the previous attempt, which might have stability issues with multiple reverse keys.
    # Keeping the multi-pass sort above as it's generally safer for stability.
    # sorted_data = sorted(data, key=multi_level_key)
    # for i, reverse in enumerate(sort_desc_list):
    #     if reverse:
    #         def key_func(item: Dict[str, Any], idx: int = i) -> Any:
    #              # Ensure this key function correctly handles the (0, value) / (1, None) tuple
    #              return multi_level_key(item)[idx]
    #
    #         # This part needs careful implementation to maintain stability across multiple reverse sorts
    #         # It involves sorting sub-groups, which is complex.
    #         # Sticking with the multi-pass sort approach above for simplicity and stability.
    #         pass # Placeholder for complex stable reverse logic
    # return sorted_data
