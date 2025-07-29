"""Mock implementation for create (POST) operations in CRUD testing.

This module provides helpers for configuring mock create operations with
validation and unique constraints as well as auto-incrementing IDs.
"""

import copy
import json
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .exceptions import ValidationFailedError
from .request_record import RequestRecord


class CreateMock(BaseCrudMock):
    """Mock implementation for create (POST) operations."""

    def __init__(self) -> None:
        """Initialize the create mock with default behaviour."""
        super().__init__()
        self.default_response: MockResponse = MockResponse(status_code=201, json_data={"id": 1, "name": "Created Resource"})
        self._unique_constraints: Dict[str, Set[Any]] = {}
        self._validation_constraints: Dict[str, Tuple[Callable[[Any], bool], str]] = {}
        self._stored_resources: List[Dict[str, Any]] = []
        self._auto_increment_id: int = 1

    def with_unique_constraint(self, field_name: str, error_message: Optional[str] = None) -> "CreateMock":
        """Configure a unique constraint for ``field_name``."""
        if field_name not in self._unique_constraints:
            self._unique_constraints[field_name] = set()

        if error_message is None:
            error_message = f"Value for '{field_name}' must be unique"

        # Override the post method to handle unique constraint violations
        original_post = self.post

        def post_with_unique_constraint(url: str, **kwargs: Any) -> Any:
            json_data = kwargs.get("json", {})

            # Check for unique constraint violation
            if field_name in json_data:
                value = json_data[field_name]
                if value in self._unique_constraints[field_name]:
                    raise ValidationFailedError(f"Unique constraint violation: {error_message}")

                # Add the value to the set of used values
                self._unique_constraints[field_name].add(value)

            # Call the original post method
            return original_post(url, **kwargs)

        # Replace the post method with our wrapper
        self.post = post_with_unique_constraint  # type: ignore[method-assign]

        return self

    def with_validation_constraint(self, field_name: str, validator: Callable[[Any], bool], error_message: str) -> "CreateMock":
        """Configure a custom validation constraint for ``field_name``."""
        self._validation_constraints[field_name] = (validator, error_message)

        # Override the post method to handle validation constraint violations
        original_post = self.post

        def post_with_validation_constraint(url: str, **kwargs: Any) -> Any:
            json_data = kwargs.get("json", {})
            if field_name in json_data:
                value = json_data[field_name]
                validator_func, msg = self._validation_constraints[field_name]
                if not validator_func(value):
                    raise ValidationFailedError(f"Validation failed: {msg}")

            # If no constraint violation, call the original post method
            return original_post(url, **kwargs)

        # Replace the post method with our wrapper
        self.post = post_with_validation_constraint  # type: ignore[method-assign]

        return self

    def with_auto_increment_id(self, id_field: str = "id") -> "CreateMock":
        """Auto increment ``id_field`` if it is not provided in the request."""
        # Override the post method to handle auto-increment IDs

        def post_with_auto_increment(url: str, **kwargs: Any) -> Any:
            json_data = kwargs.get("json", {})

            # Find a matching pattern first
            pattern = self._find_matching_pattern("POST", url, **kwargs)
            if pattern:
                response_obj = pattern["response"]

                # Handle callable responses
                if callable(response_obj):
                    response_obj = response_obj(**kwargs)

                # If there's a configured response, use it
                if isinstance(response_obj, MockResponse):
                    return response_obj.json()  # Use json() method

            # If no pattern matched or no JSON data in response, create a response
            # Create a response with the same data as the request
            response_data = copy.deepcopy(json_data)

            # If ID is explicitly provided, respect it
            if id_field in json_data:
                # Store the provided ID value
                provided_id = json_data[id_field]
                response_data[id_field] = provided_id

                # Store the resource
                self._stored_resources.append(response_data)

                # Return the response with the provided ID
                return response_data

            # Otherwise, auto-increment
            response_data[id_field] = self._auto_increment_id
            self._auto_increment_id += 1

            # Store the resource
            self._stored_resources.append(response_data)

            # Return the response with the auto-incremented ID
            return response_data

        # Replace the post method with our wrapper
        self.post = post_with_auto_increment  # type: ignore[method-assign]

        return self

    def post(self, url: str, **kwargs: Any) -> Any:
        """Handle a POST request to create a resource."""
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop("parent_id", None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="POST", url=url, params=kwargs.get("params"), data=kwargs.get("data"), json=kwargs.get("json"), headers=kwargs.get("headers")
        )
        self.request_history.append(record)  # type: ignore

        # Find a matching pattern
        pattern = self._find_matching_pattern("POST", url, **kwargs)

        if pattern:
            response_obj = pattern["response"]

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if "error" in pattern and pattern["error"]:
                raise pattern["error"]

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(status_code=201, json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(status_code=201, text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(status_code=201, text=response_obj)
                else:
                    response_obj = MockResponse(status_code=201, text=str(response_obj))

            record.response = response_obj

            # Return the appropriate response format
            # Return the appropriate response format
            json_content = response_obj.json()
            if json_content is not None:
                return json_content
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        # No pattern matched, use default response
        record.response = self.default_response

        default_json = self.default_response.json()
        if default_json is not None:
            return default_json
        return self.default_response.text

    def with_success_response(self, url_pattern: str, response_data: Dict[str, Any], status_code: int = 201, **kwargs: Any) -> "CreateMock":
        """Configure a successful response for ``url_pattern``."""
        # Store the response data directly in the mock
        # This ensures we return exactly what was configured
        if "id" in response_data:
            # Set the auto-increment ID to the response ID + 1
            # This ensures the next auto-generated ID will be higher
            self._auto_increment_id = response_data["id"] + 1

        # Create a function that returns the exact response data
        def exact_response(**request_kwargs: Any) -> MockResponse:
            return MockResponse(status_code=status_code, json_data=response_data)

        # Use the inherited with_response method
        self.with_response(
            url_pattern=url_pattern,
            response=exact_response,  # Pass the callable directly
            status_code=status_code,  # Pass status_code
            params=kwargs.get("params"),
            data=kwargs.get("data"),
            json=kwargs.get("json"),
            headers=kwargs.get("headers"),
            max_calls=kwargs.get("max_calls", 1),  # Keep the default of 1 call for this specific method
        )

        return self

    def _add_request_preprocessor(self, processor: Callable[..., Optional[MockResponse]]) -> None:
        """Add a preprocessor function that may short-circuit requests."""
        # Wrap the original post method to apply preprocessors
        original_post = self.post

        def wrapped_post(url: str, **kwargs: Any) -> Any:
            # Apply the preprocessor
            response = processor(**kwargs)
            if response is not None:
                # If the preprocessor returned a response, use it
                # Record the request
                record = RequestRecord(
                    method="POST",
                    url=url,
                    params=kwargs.get("params"),
                    data=kwargs.get("data"),
                    json=kwargs.get("json"),
                    headers=kwargs.get("headers"),
                    response=response,
                )
                self.request_history.append(record)  # type: ignore

                # Return the appropriate response format
                # Return the appropriate response format
                response_json = response.json()
                if response_json is not None:
                    return response_json
                return response.text

            # Otherwise, proceed with the original post method
            return original_post(url, **kwargs)

        # Replace the post method with the wrapped version
        self.post = wrapped_post  # type: ignore[method-assign]

    def with_validation_failure(
        self, url_pattern: str, validation_errors: Dict[str, List[str]], status_code: int = 422, **kwargs: Any
    ) -> "CreateMock":
        """Configure a validation failure response for ``url_pattern``."""
        self.with_response(url_pattern=url_pattern, response=MockResponse(status_code=status_code, json_data={"errors": validation_errors}), **kwargs)
        return self
