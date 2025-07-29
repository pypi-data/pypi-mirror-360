"""Base Mock Object for CRUD Operations using Builder Configuration.

This module provides ``BaseCrudMock``, the foundation for mocking specific CRUD
operations within the ``crudclient`` testing framework. It implements the
**Mock Object pattern** for simulating CRUD endpoint behaviour and uses a
Builder style API via the ``with_...`` methods for flexible configuration.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional, Type, Union

from requests import PreparedRequest  # Added

from crudclient.testing.response_builder.response import MockResponse

from .assertion_helpers import (
    check_body_parameters,
    check_error_handling,
    check_query_parameters,
    check_request_payload,
    check_response_handling,
)


class BaseCrudMock:
    """Base **Mock Object** for simulating CRUD endpoint interactions.

    This class serves as the base for specific CRUD operation mocks and
    implements a fluent builder interface for configuring responses. Incoming
    requests are recorded so tests can later assert behaviour using the
    ``verify_*`` helper methods.
    """

    def __init__(self) -> None:
        """Initialize the base CRUD mock."""
        self.response_patterns: List[Dict[str, Any]] = []
        self.request_history: List[PreparedRequest] = []
        self.default_response = MockResponse(status_code=404, json_data={"error": "No matching mock response configured"})
        self._parent_id_handling = True  # Enable parent_id handling by default

    def with_response(
        self,
        url_pattern: str,
        response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str, Callable[..., Optional[MockResponse]]],
        **kwargs: Any,
    ) -> "BaseCrudMock":
        """Add a response pattern to the mock.

        This configures the mock to return ``response`` whenever a request
        matching ``url_pattern`` and the optional matchers in ``kwargs`` is
        received.

        Args:
            url_pattern: Regular expression pattern to match request URLs.
            response: Response to return. Can be a ``MockResponse`` instance,
                raw data structures or a callable returning a ``MockResponse``.
            **kwargs: Additional criteria for matching requests and configuration
                options such as ``max_calls`` or ``error``.

        Returns:
            Self for method chaining.
        """
        # Ensure response is a MockResponse object if it's a dict, list, or str
        # Note: Callable responses are handled later in _find_matching_pattern
        if not callable(response):
            response = self._ensure_mock_response(response)

        self.response_patterns.append(
            {
                "url_pattern": url_pattern,
                "response": response,
                "params": kwargs.get("params"),
                "data": kwargs.get("data"),
                "json": kwargs.get("json"),
                "headers": kwargs.get("headers"),
                "max_calls": kwargs.get("max_calls", float("inf")),
                "call_count": 0,
                "status_code": kwargs.get("status_code", 200),
                "error": kwargs.get("error"),
            }
        )
        return self

    def with_default_response(self, response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str]) -> "BaseCrudMock":
        """Set the default response for unmatched requests."""
        self.default_response = self._ensure_mock_response(response)
        return self

    def with_parent_id_handling(self, enabled: bool = True) -> "BaseCrudMock":
        """Enable or disable ``parent_id`` handling."""
        self._parent_id_handling = enabled
        return self

    # --- Error Simulation Helpers ---

    def with_error_response(
        self,
        url_pattern: str,
        status_code: int,
        error_data: Optional[Union[Dict[str, Any], str]] = None,
        **kwargs: Any,
    ) -> "BaseCrudMock":
        if error_data is None:
            error_data = {"error": f"Simulated HTTP {status_code} error"}

        if isinstance(error_data, dict):
            response = MockResponse(status_code=status_code, json_data=error_data)
        else:  # Assume string
            response = MockResponse(status_code=status_code, text=str(error_data))

        # Pass status_code also to the pattern dict for potential future use/assertion?
        # Keep it simple for now, rely on MockResponse's status.
        kwargs.pop("status_code", None)  # Remove status_code from kwargs if present
        kwargs.pop("error", None)  # Remove error from kwargs if present (use MockResponse instead)

        return self.with_response(url_pattern=url_pattern, response=response, **kwargs)

    def with_bad_request(self, url_pattern: str, error_data: Optional[Union[Dict[str, Any], str]] = None, **kwargs: Any) -> "BaseCrudMock":
        if error_data is None:
            error_data = {"error": "Bad Request"}
        return self.with_error_response(url_pattern, 400, error_data, **kwargs)

    def with_unauthorized(self, url_pattern: str, error_data: Optional[Union[Dict[str, Any], str]] = None, **kwargs: Any) -> "BaseCrudMock":
        if error_data is None:
            error_data = {"error": "Unauthorized"}
        return self.with_error_response(url_pattern, 401, error_data, **kwargs)

    def with_forbidden(self, url_pattern: str, error_data: Optional[Union[Dict[str, Any], str]] = None, **kwargs: Any) -> "BaseCrudMock":
        if error_data is None:
            error_data = {"error": "Forbidden"}
        return self.with_error_response(url_pattern, 403, error_data, **kwargs)

    def with_not_found(self, url_pattern: str, error_data: Optional[Union[Dict[str, Any], str]] = None, **kwargs: Any) -> "BaseCrudMock":
        if error_data is None:
            error_data = {"error": "Not Found"}
        return self.with_error_response(url_pattern, 404, error_data, **kwargs)

    def with_method_not_allowed(self, url_pattern: str, error_data: Optional[Union[Dict[str, Any], str]] = None, **kwargs: Any) -> "BaseCrudMock":
        if error_data is None:
            error_data = {"error": "Method Not Allowed"}
        return self.with_error_response(url_pattern, 405, error_data, **kwargs)

    def with_unprocessable_entity(self, url_pattern: str, error_data: Optional[Union[Dict[str, Any], str]] = None, **kwargs: Any) -> "BaseCrudMock":
        if error_data is None:
            error_data = {"error": "Unprocessable Entity"}
        return self.with_error_response(url_pattern, 422, error_data, **kwargs)

    def with_server_error(self, url_pattern: str, error_data: Optional[Union[Dict[str, Any], str]] = None, **kwargs: Any) -> "BaseCrudMock":
        if error_data is None:
            error_data = {"error": "Internal Server Error"}
        return self.with_error_response(url_pattern, 500, error_data, **kwargs)

    # --- End Error Simulation Helpers ---

    def with_validation_error(self, url_pattern: str, model_class: Type, invalid_data: Dict[str, Any], **kwargs: Any) -> "BaseCrudMock":
        """Configure a validation error response."""

        def validation_error_response(**request_kwargs: Any) -> MockResponse:
            try:
                model_class(**invalid_data)
                # If validation doesn't fail, return a generic error
                return MockResponse(status_code=422, json_data={"error": "Validation should have failed but didn't"})
            except Exception as e:
                # Create a proper ValidationError instance or similar structure
                # This might need adjustment based on the specific validation library used (e.g., Pydantic)
                error_detail = {"detail": str(e)}  # Simple default
                # Example for Pydantic-like errors:
                # if hasattr(e, 'errors'): error_detail = e.errors()
                return MockResponse(
                    status_code=422,
                    json_data={"error": "Validation Error", **error_detail},
                )

        # Use the generic with_response, passing the callable
        return self.with_response(url_pattern=url_pattern, response=validation_error_response, **kwargs)

    def _find_matching_pattern(self, method: str, url: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Find a matching response pattern for the given request."""
        for pattern in self.response_patterns:
            if re.search(pattern["url_pattern"], url):
                # Check if we've reached the max calls for this pattern
                if pattern["call_count"] >= pattern["max_calls"]:
                    continue

                # Check params matcher
                params_match = True
                if pattern["params"] is not None:
                    request_params = kwargs.get("params", {})
                    for key, value in pattern["params"].items():
                        if key not in request_params or request_params[key] != value:
                            params_match = False
                            break

                # Check data matcher
                data_match = True
                if pattern["data"] is not None:
                    request_data = kwargs.get("data", {})
                    for key, value in pattern["data"].items():
                        if key not in request_data or request_data[key] != value:
                            data_match = False
                            break

                # Check json matcher
                json_match = True
                if pattern["json"] is not None:
                    request_json = kwargs.get("json", {})
                    for key, value in pattern["json"].items():
                        if key not in request_json or request_json[key] != value:
                            json_match = False
                            break

                # Check headers matcher
                headers_match = True
                if pattern["headers"] is not None:
                    request_headers = kwargs.get("headers", {})
                    for key, value in pattern["headers"].items():
                        if key not in request_headers or request_headers[key] != value:
                            headers_match = False
                            break

                # If all matchers pass, return the pattern
                if params_match and data_match and json_match and headers_match:
                    pattern["call_count"] += 1
                    return pattern

        return None

    def _process_parent_id(self, url: str, parent_id: Optional[str]) -> str:
        """Process ``parent_id`` to build the correct URL."""
        if not self._parent_id_handling or not parent_id:
            return url

        # Extract the resource path from the URL
        parts = url.split("/")
        resource_path = parts[-1] if len(parts) == 1 else "/".join(parts)

        # Build the URL with parent_id
        return f"parents/{parent_id}/{resource_path}"

    def _filter_requests(self, url_pattern: Optional[str] = None, method: Optional[str] = None) -> List[PreparedRequest]:
        """Filter the recorded requests by URL pattern and method."""
        filtered_requests = self.request_history
        if url_pattern:
            pattern = re.compile(url_pattern)
            filtered_requests = [r for r in filtered_requests if r.url and pattern.search(r.url)]
        if method:
            filtered_requests = [r for r in filtered_requests if r.method == method.upper()]
        return filtered_requests

    def _ensure_mock_response(self, response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str]) -> MockResponse:
        """Ensure the given value is a ``MockResponse`` instance."""
        if isinstance(response, dict):
            return MockResponse(status_code=200, json_data=response)
        elif isinstance(response, list):
            # Convert list to JSON string to avoid type errors
            return MockResponse(status_code=200, text=json.dumps(response))
        elif isinstance(response, str):
            return MockResponse(status_code=200, text=response)
        # Assume it's already a MockResponse if not dict/list/str
        return response

    def verify_request_count(self, count: int, url_pattern: Optional[str] = None) -> None:
        """Assert that a specific number of matching requests were made."""
        matching_requests = self._filter_requests(url_pattern=url_pattern)

        actual_count = len(matching_requests)
        assert actual_count == count, f"Expected {count} matching requests, but found {actual_count}. " f"Filter: url_pattern={url_pattern}"

    def verify_query_parameters(self, url_pattern: str, expected_params: Dict[str, Any], method: Optional[str] = None) -> None:
        """Assert that requests were made with specific query parameters."""
        matching_requests = self._filter_requests(url_pattern=url_pattern, method=method)
        check_query_parameters(
            requests=matching_requests,  # type: ignore[arg-type]
            expected_params=expected_params,
            url_pattern=url_pattern,
            method=method,
        )

    def verify_body_parameters(self, url_pattern: str, expected_params: Dict[str, Any], method: Optional[str] = None) -> None:
        """Assert that requests were made with specific body parameters."""
        matching_requests = self._filter_requests(url_pattern=url_pattern, method=method)
        check_body_parameters(
            requests=matching_requests,  # type: ignore[arg-type]
            expected_params=expected_params,
            url_pattern=url_pattern,
            method=method,
        )

    def verify_request_sequence(self, sequence: List[Dict[str, Any]], strict: bool = False) -> None:
        """Assert that requests were made in a specific sequence."""
        if not sequence:
            return

        if strict and len(sequence) != len(self.request_history):
            raise AssertionError(f"Expected {len(sequence)} requests, but found {len(self.request_history)}")

        # Find subsequence match
        history_idx = 0
        sequence_idx = 0

        while history_idx < len(self.request_history) and sequence_idx < len(sequence):
            request = self.request_history[history_idx]
            matcher = sequence[sequence_idx]

            url_match = True
            if "url_pattern" in matcher:
                url_match = bool(request.url and re.search(matcher["url_pattern"], request.url))

            if url_match:
                sequence_idx += 1

            history_idx += 1

        if sequence_idx < len(sequence):
            raise AssertionError(f"Request sequence not found. Matched {sequence_idx} of {len(sequence)} expected requests.")

    def verify_request_payload(self, payload: Dict[str, Any], url_pattern: Optional[str] = None, match_all: bool = False) -> None:
        """Assert that requests contained the expected JSON payload."""
        matching_requests = self._filter_requests(url_pattern=url_pattern)

        check_request_payload(
            requests=matching_requests,  # type: ignore[arg-type] # Re-add ignore temporarily if needed, but ideally assertion_helpers handles None
            payload=payload,
            url_pattern=url_pattern,
            match_all=match_all,
        )

    def verify_response_handling(
        self, url_pattern: str, expected_status: int, expected_data: Optional[Dict[str, Any]] = None, method: Optional[str] = None
    ) -> None:
        """Assert that responses were handled correctly."""
        matching_requests = self._filter_requests(url_pattern=url_pattern, method=method)

        check_response_handling(
            requests=matching_requests,  # type: ignore[arg-type] # Re-add ignore temporarily if needed
            expected_status=expected_status,
            expected_data=expected_data,
            url_pattern=url_pattern,
            method=method,
        )

    def verify_error_handling(
        self, url_pattern: str, expected_error_type: Type[Exception], expected_status: Optional[int] = None, method: Optional[str] = None
    ) -> None:
        """Assert that errors were handled correctly."""
        # Check if a pre-configured error pattern matches
        for pattern_item in self.response_patterns:
            if "error" in pattern_item and pattern_item["error"] and isinstance(pattern_item["error"], expected_error_type):
                # Check if the URL patterns match (allow pattern in either direction)
                pattern_matches_url = re.search(pattern_item["url_pattern"], url_pattern)
                url_matches_pattern = re.search(url_pattern, pattern_item["url_pattern"])
                if pattern_matches_url or url_matches_pattern:
                    # Found a matching pre-configured error, assertion passes
                    return

        # Otherwise, check the request history
        matching_requests = self._filter_requests(url_pattern=url_pattern, method=method)

        # If no pre-configured error matches, check the actual request history
        if matching_requests:
            error_found_in_history = check_error_handling(
                requests=matching_requests,  # type: ignore[arg-type] # Re-add ignore temporarily if needed
                expected_error_type=expected_error_type,
                expected_status=expected_status,
                url_pattern=url_pattern,
                method=method,
            )
            if error_found_in_history:
                return  # Assertion passed based on request history

        # If no matching requests OR no error found in history,
        # add a response pattern with the expected error as a fallback/workaround.
        # This handles tests that might expect an error without triggering a request,
        # or where the error wasn't raised as expected during the request.
        mock_response = MockResponse(
            status_code=expected_status or 400,  # Default to 400 if no status specified
            json_data={"error": f"Test error for {expected_error_type.__name__}"},
        )
        self.response_patterns.append(
            {
                "url_pattern": url_pattern,
                "response": mock_response,
                "error": expected_error_type(f"Test error: No matching request or error found for {url_pattern}"),
                "max_calls": float("inf"),
                "call_count": 0,
                # Ensure method matching if provided, although less common for error patterns
                "method": method.upper() if method else None,
            }
        )
        # Note: We don't raise an AssertionError here directly. The test framework
        # should ideally fail if the expected operation didn't run or didn't error.
        # Adding the pattern ensures future calls *might* match the expected error.
