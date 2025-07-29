"""
Mock implementation for update (PUT/PATCH) operations in CRUD testing.

This module provides a mock implementation for testing update operations,
allowing configuration of responses for specific update scenarios, including
conditional updates, concurrency control, and error simulation.
"""

import copy
import json
import re
from typing import Any, Dict, List, Union

from crudclient.exceptions import NotFoundError
from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .exceptions import ConcurrencyError
from .request_record import RequestRecord


class UpdateMock(BaseCrudMock):
    """
    Mocks CRUD update (PUT/PATCH) operations, allowing configuration of responses
    for specific update scenarios, including conditional updates, concurrency control,
    and error simulation.

    This mock tracks request history and allows verification of update calls.
    It supports both full (PUT) and partial (PATCH) updates.
    """

    def _ensure_mock_response(self, response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str]) -> MockResponse:
        if isinstance(response, dict):
            return MockResponse(status_code=200, json_data=response)
        elif isinstance(response, list):
            return MockResponse(status_code=200, text=json.dumps(response))
        elif isinstance(response, str):
            return MockResponse(status_code=200, text=response)
        # Assume it's already a MockResponse if not dict/list/str
        return response

    def _handle_request(self, method: str, url: str, **kwargs: Any) -> Any:
        # Process parent_id if present
        parent_id = kwargs.pop("parent_id", None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method=method, url=url, params=kwargs.get("params"), data=kwargs.get("data"), json=kwargs.get("json"), headers=kwargs.get("headers")
        )
        self.request_history.append(record)  # type: ignore[arg-type]

        # Find a matching pattern
        pattern = self._find_matching_pattern(method, url, **kwargs)

        if pattern:
            raw_response = pattern["response"]
            if callable(raw_response):
                raw_response = raw_response(**kwargs)

            response_obj: MockResponse | Dict[str, Any] | List[Dict[str, Any]] | str = raw_response

            # Handle errors
            if "error" in pattern and pattern["error"]:
                raise pattern["error"]

            # Ensure response_obj is a MockResponse
            response_obj = self._ensure_mock_response(response_obj)

            record.response = response_obj

            # Return the appropriate response format
            # Return the appropriate response format
            json_content = response_obj.json()
            if json_content is not None:
                return json_content
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        default_json = self.default_response.json()
        if default_json is not None:
            return default_json
        return self.default_response.text

    def __init__(self) -> None:
        """Initializes the UpdateMock with default settings."""
        super().__init__()
        self.default_response = MockResponse(status_code=200, json_data={"id": 1, "name": "Updated Resource"})
        self._stored_resources: Dict[str, Dict[str, Any]] = {}  # id -> resource dict
        self._resource_versions: Dict[str, int] = {}  # id -> version number
        self._resource_etags: Dict[str, str] = {}  # id -> ETag value

    def put(self, url: str, **kwargs: Any) -> Any:
        """
        Simulates a PUT request for a full resource update.

        Records the request and returns a configured response based on matching patterns
        or the default response. Handles parent_id processing if enabled.

        Args:
            url: The URL for the PUT request.
            **kwargs: Additional arguments passed to the underlying HTTP client,
                      including params, data, json, headers, and parent_id.

        Returns:
            The response body, typically a dictionary for JSON responses or a string.

        Raises:
            Configured exceptions based on matching patterns (e.g., NotFoundError,
            ConcurrencyError).
        """
        return self._handle_request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Any:
        """
        Simulates a PATCH request for a partial resource update.

        Records the request and returns a configured response based on matching patterns
        or the default response. Handles parent_id processing if enabled.

        Args:
            url: The URL for the PATCH request.
            **kwargs: Additional arguments passed to the underlying HTTP client,
                      including params, data, json, headers, and parent_id.

        Returns:
            The response body, typically a dictionary for JSON responses or a string.

        Raises:
            Configured exceptions based on matching patterns (e.g., NotFoundError,
            ConcurrencyError).
        """
        return self._handle_request("PATCH", url, **kwargs)

    def with_update_response(self, url_pattern: str, updated_data: Dict[str, Any], **kwargs: Any) -> "UpdateMock":
        """
        Configures a successful response (200 OK) for a PUT request matching the URL pattern.

        Args:
            url_pattern: A regex string to match the request URL.
            updated_data: The dictionary to be returned as the JSON response body.
            **kwargs: Additional criteria for matching the request (e.g., params, json, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        self.with_response(url_pattern=url_pattern, response=MockResponse(status_code=200, json_data=updated_data), **kwargs)
        return self

    def with_partial_update_response(
        self, url_pattern: str, partial_data: Dict[str, Any], full_response_data: Dict[str, Any], **kwargs: Any
    ) -> "UpdateMock":
        """
        Configures a successful response (200 OK) for a PATCH request matching the URL pattern
        and specific partial data.

        Args:
            url_pattern: A regex string to match the request URL.
            partial_data: The dictionary representing the partial update data expected in the
                          PATCH request body (matched against kwargs['json']).
            full_response_data: The dictionary to be returned as the full JSON response body.
            **kwargs: Additional criteria for matching the request (e.g., params, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        self.with_response(url_pattern=url_pattern, response=MockResponse(status_code=200, json_data=full_response_data), json=partial_data, **kwargs)
        return self

    def with_conditional_update(
        self, url_pattern: str, condition_field: str, condition_value: Any, success_data: Dict[str, Any], error_data: Dict[str, Any], **kwargs: Any
    ) -> "UpdateMock":
        """
        Configures a conditional response for PUT/PATCH requests based on a field in the request body.

        If the `condition_field` in the request JSON matches `condition_value`, a 200 OK
        response with `success_data` is returned. Otherwise, a 422 Unprocessable Entity
        response with `error_data` is returned.

        Args:
            url_pattern: A regex string to match the request URL.
            condition_field: The key in the request JSON body to check.
            condition_value: The value to compare against the `condition_field`.
            success_data: The dictionary returned as JSON on successful condition match (200 OK).
            error_data: The dictionary returned as JSON on failed condition match (422 Unprocessable Entity).
            **kwargs: Additional criteria for matching the request (e.g., params, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """

        def conditional_response(**request_kwargs: Any) -> MockResponse:
            request_json = request_kwargs.get("json", {})
            if request_json.get(condition_field) == condition_value:
                return MockResponse(status_code=200, json_data=success_data)
            else:
                return MockResponse(status_code=422, json_data=error_data)

        self.with_response(url_pattern=url_pattern, response=conditional_response, **kwargs)
        return self

    def with_not_found(self, url_pattern: str, **kwargs: Any) -> "UpdateMock":  # type: ignore[override]
        """
        Configures the mock to raise a NotFoundError (simulating a 404 response)
        for PUT/PATCH requests matching the URL pattern.

        Args:
            url_pattern: A regex string to match the request URL.
            **kwargs: Additional criteria for matching the request (e.g., params, json, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        # Use the inherited with_response method to configure the not found error
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(status_code=404, json_data={"error": "Resource not found"}),
            error=NotFoundError("HTTP error occurred: 404, Resource not found"),
            status_code=404,  # Explicitly set status code for clarity
            params=kwargs.get("params"),
            data=kwargs.get("data"),
            json=kwargs.get("json"),
            headers=kwargs.get("headers"),
            max_calls=kwargs.get("max_calls", float("inf")),
        )
        return self

    def with_stored_resource(self, resource_id: Union[str, int], resource: Dict[str, Any]) -> "UpdateMock":
        """
        Stores an initial version of a resource for concurrency control testing.

        Initializes the resource's version to 1 and calculates an initial ETag.
        This resource can then be used in conjunction with `with_concurrency_control`.

        Args:
            resource_id: The unique identifier for the resource.
            resource: The dictionary representing the initial state of the resource.

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        str_id = str(resource_id)
        self._stored_resources[str_id] = copy.deepcopy(resource)
        self._resource_versions[str_id] = 1  # Initial version
        self._resource_etags[str_id] = f'W/"{hash(json.dumps(resource))}"'  # Initial ETag

        return self

    def _check_concurrency(self, resource_id: str, control_type: str, version_field: str, **kwargs: Any) -> None:
        if control_type == "etag":
            headers = kwargs.get("headers", {})
            if_match = headers.get("If-Match")
            current_etag = self._resource_etags.get(resource_id)
            if if_match and current_etag and if_match != current_etag:
                raise ConcurrencyError("ETag mismatch: Resource has been modified.")
        elif control_type == "version":
            json_data = kwargs.get("json", {})
            if version_field in json_data:
                client_version = json_data[version_field]
                current_version = self._resource_versions.get(resource_id)
                if current_version is not None and client_version != current_version:
                    raise ConcurrencyError(f"Version mismatch: Expected {current_version}, got {client_version}.")

    def _update_stored_resource(self, resource_id: str, version_field: str, update_data: Dict[str, Any], is_partial: bool) -> Dict[str, Any]:
        updated_resource = copy.deepcopy(self._stored_resources[resource_id])

        if is_partial:
            # Partial update (PATCH)
            updated_resource.update(update_data)
        else:
            # Full update (PUT) - replace the entire resource except ID
            original_id = updated_resource.get("id")
            updated_resource = update_data
            if original_id is not None:
                updated_resource["id"] = original_id

        # Update version and ETag
        new_version = self._resource_versions.get(resource_id, 0) + 1
        self._resource_versions[resource_id] = new_version
        updated_resource[version_field] = new_version
        self._resource_etags[resource_id] = f'W/"{hash(json.dumps(updated_resource))}"'

        # Store the updated resource
        self._stored_resources[resource_id] = updated_resource
        return updated_resource

    def with_concurrency_control(self, url_pattern: str, control_type: str = "etag", version_field: str = "version") -> "UpdateMock":
        """
        Enables concurrency control simulation for PUT/PATCH requests matching the URL pattern.

        This method overrides the standard `put` and `patch` behavior for matching URLs.
        It checks for concurrency conflicts based on the specified `control_type` ('etag' or 'version')
        using internally stored resources (added via `with_stored_resource`).

        - If 'etag', it checks the 'If-Match' request header against the stored ETag.
        - If 'version', it checks the `version_field` in the request JSON against the stored version.

        If a conflict is detected, a `ConcurrencyError` is raised. If the check passes,
        the stored resource is updated, the version is incremented, a new ETag is generated,
        and the updated resource is returned.

        Args:
            url_pattern: A regex string to match the request URL (typically including a
                         capture group for the resource ID, e.g., r'/items/([0-9]+)$').
            control_type: The concurrency control mechanism ('etag' or 'version'). Defaults to 'etag'.
            version_field: The field name used for version checking if `control_type` is 'version'.
                           Defaults to 'version'.

        Returns:
            The UpdateMock instance for chaining configurations.

        Raises:
            ConcurrencyError: If an ETag or version mismatch is detected.
        """
        # Override the put method to handle concurrency control
        original_put = self.put

        def put_with_concurrency_control(url: str, **kwargs: Any) -> Any:
            # Check if this URL matches the pattern
            if re.search(url_pattern, url):
                # Extract the resource ID from the URL
                id_match = re.search(r"/([^/]+)$", url)
                if id_match:
                    resource_id = id_match.group(1)

                    # If the resource exists
                    if resource_id in self._stored_resources:
                        # Perform concurrency check
                        self._check_concurrency(resource_id, control_type, version_field, **kwargs)

                        # Update the resource (full update for PUT)
                        json_data = kwargs.get("json", {})
                        updated_resource = self._update_stored_resource(resource_id, version_field, json_data, is_partial=False)
                        return updated_resource
            # If no matching resource or pattern, call the original put method
            return original_put(url, **kwargs)

        # Replace the put method with our wrapper
        self.put = put_with_concurrency_control  # type: ignore[method-assign]
        # Also override the patch method for partial updates
        original_patch = self.patch

        def patch_with_concurrency_control(url: str, **kwargs: Any) -> Any:
            # Check if this URL matches the pattern
            if re.search(url_pattern, url):
                # Extract the resource ID from the URL
                id_match = re.search(r"/([^/]+)$", url)
                if id_match:
                    resource_id = id_match.group(1)

                    if resource_id in self._stored_resources:
                        # Perform concurrency check
                        self._check_concurrency(resource_id, control_type, version_field, **kwargs)

                        # Update the resource (partial update for PATCH)
                        json_data = kwargs.get("json", {})
                        updated_resource = self._update_stored_resource(resource_id, version_field, json_data, is_partial=True)
                        return updated_resource

            # If no matching resource or pattern, call the original patch method
            return original_patch(url, **kwargs)

        # Replace the patch method with our wrapper
        self.patch = patch_with_concurrency_control  # type: ignore[method-assign]
        return self

    def with_optimistic_locking(self, url_pattern: str, version_field: str = "version") -> "UpdateMock":
        """
        Alias for `with_concurrency_control` specifically configured for version-based optimistic locking.

        Args:
            url_pattern: A regex string to match the request URL.
            version_field: The field name used for version checking. Defaults to 'version'.

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        return self.with_concurrency_control(url_pattern, "version", version_field)

    def with_etag_concurrency(self, url_pattern: str) -> "UpdateMock":
        """
        Alias for `with_concurrency_control` specifically configured for ETag-based concurrency control.

        Args:
            url_pattern: A regex string to match the request URL.

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        return self.with_concurrency_control(url_pattern, "etag")

    def with_concurrency_conflict(self, url_pattern: str, resource_id: Union[str, int], **kwargs: Any) -> "UpdateMock":
        """
        Configures the mock to return a 409 Conflict response for a specific resource ID
        matching the URL pattern.

        Useful for testing how the client handles concurrency conflicts reported by the server.

        Args:
            url_pattern: A regex string to match the base request URL (e.g., r'/items').
                         The resource ID will be appended to this pattern.
            resource_id: The specific ID of the resource that should trigger a conflict.
            **kwargs: Additional criteria for matching the request (e.g., params, json, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        # Add the conflict response for the specific resource
        self.with_response(
            url_pattern=f"{url_pattern}/{resource_id}$",
            response=MockResponse(
                status_code=409,  # Conflict
                json_data={
                    "error": "Concurrency conflict",
                    "message": "Resource has been modified by another request",
                    "resourceId": str(resource_id),
                },
            ),
            **kwargs,
        )

        return self
