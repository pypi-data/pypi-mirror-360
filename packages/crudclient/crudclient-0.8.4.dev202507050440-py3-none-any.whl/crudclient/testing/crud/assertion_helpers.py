"""Helper functions for asserting conditions on CRUD mock requests."""

from typing import Any, Dict, List, Optional, Type

from crudclient.testing.response_builder.response import (
    MockResponse,  # Assuming Request object structure
)

# Placeholder for the actual Request object type used in request_history
# Replace with the actual import if available


class Request:
    """Represents a request made to a mock API."""

    url: str
    method: str
    params: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]
    json: Optional[Dict[str, Any]]
    response: MockResponse


def check_request_payload(
    requests: List[Request],
    payload: Dict[str, Any],
    url_pattern: Optional[str],
    match_all: bool,
) -> None:
    """Check that requests were made with a specific payload."""
    if not requests:
        raise AssertionError(f"No matching requests found. Filter: url_pattern={url_pattern}")

    if match_all:
        for i, request in enumerate(requests):
            request_json = request.json or {}
            for key, value in payload.items():
                if key not in request_json:
                    raise AssertionError(f"Request {i} missing payload key '{key}'. " f"URL: {request.url}")
                if callable(value):
                    if not value(request_json[key]):
                        raise AssertionError(f"Request {i} payload key '{key}' failed validation. " f"URL: {request.url}")
                elif request_json[key] != value:
                    raise AssertionError(
                        f"Request {i} payload key '{key}' has value '{request_json[key]}', " f"expected '{value}'. URL: {request.url}"
                    )
    else:
        # At least one request must match all payload
        found_match = False
        for request in requests:
            all_match = True
            request_json = request.json or {}
            for key, value in payload.items():
                if key not in request_json:
                    all_match = False
                    break
                if callable(value):
                    if not value(request_json[key]):
                        all_match = False
                        break
                elif request_json[key] != value:
                    all_match = False
                    break

            if all_match:
                found_match = True
                break

        if not found_match:
            raise AssertionError(f"No request matched all payload {payload}. " f"Filter: url_pattern={url_pattern}")


def check_query_parameters(
    requests: List[Request],
    expected_params: Dict[str, Any],
    url_pattern: str,
    method: Optional[str],
) -> None:
    """Checks if at least one matching request contains the expected query parameters."""
    assert requests, f"No matching requests found for URL pattern: {url_pattern}, method: {method}"

    found_matching_request = False
    mismatch_details = []

    for i, request in enumerate(requests):
        all_params_match = True
        current_request_mismatches = []
        request_params = request.params or {}

        for key, expected_value in expected_params.items():
            if key not in request_params:
                all_params_match = False
                current_request_mismatches.append(f"missing key '{key}'")
                break  # Move to next request if a key is missing

            actual_value = request_params[key]
            # Allow callable for value checking
            if callable(expected_value):
                if not expected_value(actual_value):
                    all_params_match = False
                    current_request_mismatches.append(f"key '{key}' failed validation (value: '{actual_value}')")
            elif actual_value != expected_value:
                all_params_match = False
                current_request_mismatches.append(f"key '{key}' has value '{actual_value}', expected '{expected_value}'")

        if all_params_match:
            found_matching_request = True
            break
        elif current_request_mismatches:
            mismatch_details.append(f"Request {i}: {'; '.join(current_request_mismatches)}")

    if not found_matching_request:
        error_message = f"No request matched all expected query parameters: {expected_params}. " f"URL pattern: {url_pattern}, method: {method}."
        if mismatch_details:
            error_message += "\nMismatches found:\n" + "\n".join(mismatch_details)
        raise AssertionError(error_message)


def check_body_parameters(
    requests: List[Request],
    expected_params: Dict[str, Any],
    url_pattern: str,
    method: Optional[str],
) -> None:
    """Checks if at least one matching request contains the expected body parameters."""
    assert requests, f"No matching requests found for URL pattern: {url_pattern}, method: {method}"

    found_matching_request = False
    mismatch_details = []

    for i, request in enumerate(requests):
        all_params_match = True
        current_request_mismatches = []
        # Combine data and json, preferring json if both exist (common case)
        request_body = request.json if request.json is not None else request.data or {}

        for key, expected_value in expected_params.items():
            if key not in request_body:
                all_params_match = False
                current_request_mismatches.append(f"missing key '{key}'")
                break  # Move to next request if a key is missing

            actual_value = request_body[key]
            # Allow callable for value checking
            if callable(expected_value):
                if not expected_value(actual_value):
                    all_params_match = False
                    current_request_mismatches.append(f"key '{key}' failed validation (value: '{actual_value}')")
            elif actual_value != expected_value:
                all_params_match = False
                current_request_mismatches.append(f"key '{key}' has value '{actual_value}', expected '{expected_value}'")

        if all_params_match:
            found_matching_request = True
            break
        elif current_request_mismatches:
            mismatch_details.append(f"Request {i}: {'; '.join(current_request_mismatches)}")

    if not found_matching_request:
        error_message = f"No request matched all expected body parameters: {expected_params}. " f"URL pattern: {url_pattern}, method: {method}."
        if mismatch_details:
            error_message += "\nMismatches found:\n" + "\n".join(mismatch_details)
        raise AssertionError(error_message)


def check_response_handling(
    requests: List[Request],
    expected_status: int,
    expected_data: Optional[Dict[str, Any]],
    url_pattern: str,
    method: Optional[str],
) -> None:
    """Check that responses had the expected status and data."""
    assert requests, f"No matching requests found for URL pattern: {url_pattern}, method: {method}"

    for i, request in enumerate(requests):
        # Check status code
        assert request.response.status_code == expected_status, (
            f"Request {i} response status code is {request.response.status_code}, " f"expected {expected_status}. URL: {request.url}"
        )

        # Check response data if provided
        if expected_data:
            response_json = request.response.json()  # Use the public json() method
            # Ensure response_json is a dict if expected_data is provided
            if not isinstance(response_json, dict):
                body_snippet = request.response.text or b""
                if isinstance(body_snippet, (bytes, bytearray)):
                    body_snippet = body_snippet.decode()
                raise AssertionError(
                    f"Request {i} response body is not a JSON object (or is empty), "
                    f"but expected data was provided. URL: {request.url}. Body: {(request.response.text.decode() if isinstance(request.response.text, bytes) else request.response.text or '')[:100]}"  # Show snippet
                )
            # Add assertion to help type checker confirm response_json is not None here
            assert response_json is not None

            for key, expected_value in expected_data.items():
                assert key in response_json, f"Request {i} response missing key '{key}'. URL: {request.url}"
                actual_value = response_json[key]
                # Allow callable for value checking
                if callable(expected_value):
                    assert expected_value(actual_value), (
                        f"Request {i} response key '{key}' failed validation. " f"Value: '{actual_value}'. URL: {request.url}"
                    )
                elif actual_value != expected_value:
                    raise AssertionError(
                        f"Request {i} response key '{key}' has value '{actual_value}', " f"expected '{expected_value}'. URL: {request.url}"
                    )


def check_error_handling(
    requests: List[Request],
    expected_error_type: Type[Exception],
    expected_status: Optional[int],
    url_pattern: str,
    method: Optional[str],
) -> bool:
    """Check that errors of the expected type were raised."""
    assert requests, f"No matching requests found for URL pattern: {url_pattern}, method: {method}"

    error_found_in_history = False
    for i, request in enumerate(requests):
        # Check if the response associated with the request has an error attribute
        if hasattr(request.response, "error") and request.response.error:
            error_found_in_history = True
            assert isinstance(request.response.error, expected_error_type), (
                f"Request {i} error type is {type(request.response.error)}, " f"expected {expected_error_type}. URL: {request.url}"
            )

            # Check status code if provided
            if expected_status:
                assert request.response.status_code == expected_status, (
                    f"Request {i} response status code is {request.response.status_code}, " f"expected {expected_status}. URL: {request.url}"
                )
            # If we found a matching error in history, we can stop checking history
            break

    return error_found_in_history
