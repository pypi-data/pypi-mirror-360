# crudclient.testing.core

This module provides core components for testing applications that use the `crudclient` library. It focuses on mocking the client and its underlying HTTP interactions to enable isolated unit and integration testing without making actual network calls.

## Overview

The primary components offered by this module are:

*   **`MockClient`**: A mock implementation of the main `crudclient.Client`. It simulates the client's behavior, allowing you to configure responses for specific API calls and verify interactions during tests. It utilizes a mock HTTP client internally.
*   **`MockHTTPClient`**: A mock implementation of the HTTP layer used by the client. It allows configuring predefined responses (including status codes, data, and headers) for specific HTTP methods and URL paths (either exact matches or regex patterns). It can also simulate network latency.
*   **`NetworkCondition`**: A utility class designed to simulate various network conditions like latency, packet loss, and random errors. `MockHTTPClient` currently uses this to simulate latency.

Both `MockClient` and `MockHTTPClient` inherit from `EnhancedSpyBase`, providing capabilities to record calls made to them, allowing for detailed verification of interactions in tests.

## Key Components

### `MockClient`

(`crudclient.testing.core.client.MockClient`)

This class acts as a stand-in for the real `crudclient.Client`.

*   **Initialization**: Requires a mock HTTP client instance (like `MockHTTPClient`). Can optionally take a `base_url` and a `ClientConfig` object.
*   **Response Configuration**: Delegates response configuration to the underlying mock HTTP client via methods like `configure_response` (for exact path matches) and `with_response_pattern` (for regex path matches).
*   **Authentication**: Supports setting an `AuthStrategy` via `set_auth_strategy`, which will be used to prepare request headers/params.
*   **HTTP Methods**: Provides mock implementations of `get`, `post`, `put`, `delete`, and `patch`. These methods interact with the configured responses on the mock HTTP client, handle basic error simulation (raising exceptions for >= 400 status codes), and wrap successful responses in a `ResponseWrapper`.
*   **Call Recording**: Records details of each HTTP method call (path, headers, params, data, result/exception, duration) using its `EnhancedSpyBase` capabilities.
*   **Reset**: The `reset()` method clears configured responses on the underlying HTTP client and resets the call history.
*   **Pagination Helper**: Includes a `create_paginated_response` method to easily build mock paginated responses using `PaginationResponseBuilder`.

**Helper Class:**

*   **`ResponseWrapper`**: A simple wrapper around the mock `Response` object returned by `MockHTTPClient`. It provides dictionary-like access (`__getitem__`, `__contains__`) and a `.json()` method for convenience when the response content is JSON.

### `MockHTTPClient`

(`crudclient.testing.core.http_client.MockHTTPClient`)

This class simulates the behavior of an HTTP client (like `requests.Session`).

*   **Initialization**: Takes an optional `base_url`.
*   **Response Configuration**:
    *   `configure_response()`: Define a response for a specific HTTP method and exact URL path.
    *   `with_response_pattern()`: Define a response for a specific HTTP method and a URL path matching a regular expression. Patterns are checked in LIFO order (last added pattern is checked first).
*   **Network Simulation**:
    *   `with_network_condition()`: Currently supports configuring latency (`latency_ms`) which adds a `time.sleep()` delay before returning a response.
*   **Request Handling**: The `request()` method (and convenience methods like `get`, `post`, etc.) looks up the configured response based on the method and path (checking exact matches first, then patterns). If no response is configured, it raises `RequestNotConfiguredError`. If a response is found, it simulates latency (if configured) and returns a `requests.Response` object populated with the configured status code, headers, and body content. It also handles configured errors by raising them.
*   **Call Recording**: Records details of each call to `request` (method, path, headers, params, data, result/exception, duration) using its `EnhancedSpyBase` capabilities.
*   **Reset**: The `reset()` method clears all configured responses, patterns, network conditions, and call history.

### `NetworkCondition`

(`crudclient.testing.core.network.NetworkCondition`)

A utility to define simulated network conditions.

*   **Initialization**: Takes `latency_ms`, `packet_loss_percentage`, `error_rate_percentage`, and an optional `error_factory` (defaults to raising `requests.ConnectionError`).
*   **Methods**:
    *   `should_drop_packet()`: Returns `True` based on `packet_loss_percentage`.
    *   `should_raise_error()`: Returns `True` based on `error_rate_percentage`.
    *   `apply_latency()`: Sleeps for the configured `latency_ms`.

## Basic Usage Example

```python
import pytest
from crudclient.testing.core import MockClient, MockHTTPClient
from crudclient.testing.exceptions import RequestNotConfiguredError

# 1. Create a mock HTTP client
mock_http = MockHTTPClient(base_url="https://test.api")

# 2. Configure responses
mock_http.configure_response(
    method="GET",
    path="/users/1",
    status_code=200,
    data={"id": 1, "name": "Test User"},
    headers={"Content-Type": "application/json"}
)
mock_http.configure_response(
    method="POST",
    path="/users",
    status_code=201,
    data={"id": 2, "name": "New User"}
)
mock_http.configure_response(
    method="GET",
    path="/users/notfound",
    status_code=404,
    data={"error": "Not Found"}
)
mock_http.with_response_pattern(
    method="GET",
    path_pattern=r"/items/\d+", # Match /items/ followed by digits
    status_code=200,
    data={"item_id": "matched", "value": "some data"}
)


# 3. Create the MockClient using the mock HTTP client
mock_client = MockClient(http_client=mock_http)

# 4. Use the MockClient in your test
def test_get_user():
    response = mock_client.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Test User"}
    assert response["name"] == "Test User" # Using ResponseWrapper access

def test_create_user():
    response = mock_client.post("/users", data={"name": "New User"})
    assert response.status_code == 201
    assert response.json()["id"] == 2

def test_get_item_by_pattern():
    response = mock_client.get("/items/123")
    assert response.status_code == 200
    assert response.json()["item_id"] == "matched"

def test_not_found():
    with pytest.raises(Exception) as excinfo: # MockClient raises generic Exception for 4xx/5xx
        mock_client.get("/users/notfound")
    assert "Request failed with status code 404" in str(excinfo.value)
    # Note: The actual exception type might vary based on MockClient's error handling logic

def test_unconfigured_request():
    with pytest.raises(RequestNotConfiguredError):
        mock_client.get("/unconfigured/path")

# 5. Verify calls (using EnhancedSpyBase features)
def test_call_verification():
    mock_client.reset() # Clear previous calls
    mock_client.get("/users/1")
    mock_client.post("/users", data={"name": "Another User"})

    assert mock_client.call_count == 2

    # Verify GET call
    get_call = mock_client.calls[0]
    assert get_call.method_name == "GET"
    assert get_call.args == ("/users/1",)
    assert get_call.kwargs.get("params") is None # Check specific kwargs

    # Verify POST call
    post_call = mock_client.calls[1]
    assert post_call.method_name == "POST"
    assert post_call.args == ("/users",)
    assert post_call.kwargs.get("data") == {"name": "Another User"}

    # Assert specific call happened
    mock_client.assert_called_with("GET", "/users/1")
    mock_client.assert_called_once_with("POST", "/users", data={"name": "Another User"})