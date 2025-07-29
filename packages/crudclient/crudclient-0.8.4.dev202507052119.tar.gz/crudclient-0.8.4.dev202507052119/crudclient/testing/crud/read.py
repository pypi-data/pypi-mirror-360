"""Read operation mock for testing GET endpoints with rich query handling."""

import copy
import json
import re
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock

if TYPE_CHECKING:
    from .request_record import RequestRecord
else:
    # Import RequestRecord for runtime use
    from .request_record import RequestRecord


class ReadMock(BaseCrudMock):
    """Mock for read operations supporting filtering and pagination."""

    _parent_id_handling: bool
    request_history: List["RequestRecord"]  # type: ignore[assignment]

    def __init__(self) -> None:
        """Initialize the read mock with default data."""
        super().__init__()
        self.default_response = MockResponse(status_code=200, json_data={"id": 1, "name": "Default Read Resource"})
        self._stored_resources: List[Dict[str, Any]] = []  # List of resources for dynamic handling

    def set_stored_resources(self, resources: List[Dict[str, Any]]) -> "ReadMock":
        """Provide a list of resources for dynamic querying."""
        self._stored_resources = copy.deepcopy(resources)
        return self

    def get(self, url: str, **kwargs: Any) -> Any:
        """Handle a GET request and return the configured response."""
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop("parent_id", None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="GET", url=url, params=kwargs.get("params"), data=kwargs.get("data"), json=kwargs.get("json"), headers=kwargs.get("headers")
        )
        self.request_history.append(record)

        # Handle the request based on stored resources or pattern matching
        if self._stored_resources:
            return self._handle_stored_resources(url, kwargs, record)
        else:
            return self._handle_pattern_matching(url, kwargs, record)

    def _handle_stored_resources(self, url: str, kwargs: Dict[str, Any], record: RequestRecord) -> Any:
        params = kwargs.get("params", {})
        result_data: Any = None
        status_code = 200

        # Check if this is a request for a specific resource by ID
        resource_id_match = re.search(r"/(\d+)$", url)
        if resource_id_match:
            result_data, status_code = self._handle_single_resource_request(resource_id_match, params)
        else:
            # This is a list request
            result_data = self._handle_list_request(params)

        # Create and record the response
        response_obj = MockResponse(status_code=status_code, json_data=result_data)
        record.response = response_obj
        return response_obj.json()  # Use .json() method for consistency

    def _handle_single_resource_request(self, resource_id_match: re.Match, params: Dict[str, Any]) -> Tuple[Any, int]:
        try:
            resource_id = int(resource_id_match.group(1))
            found_resource = next((r for r in self._stored_resources if r.get("id") == resource_id), None)

            if found_resource:
                # Apply field selection if specified
                if "fields" in params:
                    result_data = self._apply_field_selection(found_resource, params["fields"])
                else:
                    result_data = found_resource
                return result_data, 200
            else:
                return {"error": f"Resource with ID {resource_id} not found"}, 404

        except ValueError:
            # Handle cases where the matched ID is not an integer (though the regex prevents this)
            return {"error": "Invalid resource ID format"}, 400

    def _handle_list_request(self, params: Dict[str, Any]) -> Any:
        # Start with a copy of all resources
        result = self._stored_resources.copy()

        # Apply filtering
        result = self._apply_filtering(result, params)

        # Apply sorting
        result = self._apply_sorting(result, params)

        total_items = len(result)

        # Apply pagination
        paginated_result = self._apply_pagination(result, params)

        # Apply field selection
        if "fields" in params:
            paginated_result = self._apply_field_selection_to_list(paginated_result, params["fields"])

        # Format the response
        return self._format_list_response(paginated_result, params, total_items)

    def _apply_filtering(self, resources: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Apply filtering (simple equality based on params, excluding reserved keys)
        filter_params = {k: v for k, v in params.items() if k not in ("sort", "fields", "page", "limit", "_page", "_limit")}

        filtered_resources = resources
        for key, value in filter_params.items():
            filtered_resources = [r for r in filtered_resources if str(r.get(key)) == str(value)]

        return filtered_resources

    def _apply_sorting(self, resources: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        sorted_resources = resources

        if "sort" in params:
            sort_fields = params["sort"].split(",")
            for field in reversed(sort_fields):
                reverse = False
                if field.startswith("-"):
                    field = field[1:]
                    reverse = True
                # Basic sort, assumes comparable types or converts to string
                sorted_resources.sort(key=lambda r: str(r.get(field, "")), reverse=reverse)

        return sorted_resources

    def _apply_pagination(self, resources: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Apply pagination (using 'page'/'limit' or '_page'/'_limit')
        page = int(params.get("page", params.get("_page", 1)))
        limit = int(params.get("limit", params.get("_limit", 10)))  # Default limit 10
        start = (page - 1) * limit
        end = start + limit
        return resources[start:end]

    def _apply_field_selection(self, resource: Dict[str, Any], fields_param: str) -> Dict[str, Any]:
        fields = fields_param.split(",")
        return {field: resource.get(field) for field in fields if field in resource}

    def _apply_field_selection_to_list(self, resources: List[Dict[str, Any]], fields_param: str) -> List[Dict[str, Any]]:
        fields = fields_param.split(",")
        return [{field: r.get(field) for field in fields if field in r} for r in resources]

    def _format_list_response(self, resources: List[Dict[str, Any]], params: Dict[str, Any], total_items: int) -> Any:
        # Format response (simple list or paginated structure)
        # Decide structure based on presence of pagination params
        if "page" in params or "limit" in params or "_page" in params or "_limit" in params:
            page = int(params.get("page", params.get("_page", 1)))
            limit = int(params.get("limit", params.get("_limit", 10)))
            return {
                "data": resources,
                "meta": {
                    "page": page,
                    "limit": limit,
                    "total": total_items,
                    "pages": (total_items + limit - 1) // limit if limit > 0 else 1,
                    "total_count": total_items,  # Common alternative naming
                    "total_pages": (total_items + limit - 1) // limit if limit > 0 else 1,  # Common alternative naming
                },
            }
        else:
            return resources  # Return plain list if no pagination params

    def _handle_pattern_matching(self, url: str, kwargs: Dict[str, Any], record: RequestRecord) -> Any:
        pattern = self._find_matching_pattern("GET", url, **kwargs)
        if pattern:
            response_obj = self._process_pattern_response(pattern, url, kwargs, record)
            record.response = response_obj
            return response_obj.json() if response_obj.json_data is not None else response_obj.text

        # No stored resources and no pattern matched, use default response
        record.response = self.default_response
        return self.default_response.json() if self.default_response.json_data is not None else self.default_response.text

    def _process_pattern_response(self, pattern: Dict[str, Any], url: str, kwargs: Dict[str, Any], record: RequestRecord) -> MockResponse:
        response_obj = pattern["response"]

        # Handle callable responses
        if callable(response_obj):
            response_obj = response_obj(url=url, **kwargs)  # Pass context to callable

        # Handle errors defined in the pattern
        if "error" in pattern and pattern["error"]:
            error = pattern["error"]
            record.response = MockResponse(
                status_code=pattern.get("status_code", 500),
                json_data={"error": str(error)},
            )
            raise error

        # Ensure response_obj is a MockResponse
        if not isinstance(response_obj, MockResponse):
            if isinstance(response_obj, dict):
                response_obj = MockResponse(status_code=200, json_data=response_obj)
            elif isinstance(response_obj, list):
                # If it's a list, serialize to JSON and use the text parameter
                response_obj = MockResponse(status_code=200, text=json.dumps(response_obj))
            elif isinstance(response_obj, str):
                # Attempt to parse as JSON, otherwise treat as text
                try:
                    json_data = json.loads(response_obj)
                    response_obj = MockResponse(status_code=200, json_data=json_data)
                except json.JSONDecodeError:
                    response_obj = MockResponse(status_code=200, text=response_obj)
            else:
                # Fallback for other types
                response_obj = MockResponse(status_code=200, text=str(response_obj))

        return response_obj

    def with_single_resource(self, url_pattern: str, resource_data: Dict[str, Any], **kwargs: Any) -> "ReadMock":
        """Return ``resource_data`` when ``url_pattern`` matches."""
        self.with_response(url_pattern=url_pattern, response=MockResponse(status_code=200, json_data=resource_data), **kwargs)
        return self

    def with_resource_list(self, url_pattern: str, resources: List[Dict[str, Any]], **kwargs: Any) -> "ReadMock":
        """Return ``resources`` list when ``url_pattern`` matches."""
        self.with_response(url_pattern=url_pattern, response=MockResponse(status_code=200, text=json.dumps(resources)), **kwargs)
        return self

    # Removed with_stored_resources, with_field_selection, with_filtering,
    # with_sorting, and with_pagination as their logic is now integrated
    # into the main get() method when _stored_resources is populated.
    # Use set_stored_resources() to populate the data for dynamic handling.
