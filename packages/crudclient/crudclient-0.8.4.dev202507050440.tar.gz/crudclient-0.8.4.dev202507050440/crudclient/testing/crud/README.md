# `crudclient.testing.crud`

This module provides mock objects and utilities specifically designed for testing client-side code that interacts with CRUD (Create, Read, Update, Delete) endpoints, particularly those defined or consumed using the `crudclient` library.

It allows developers to simulate various API behaviors, configure expected responses, and verify that the client under test makes the correct HTTP requests with the appropriate parameters and payloads.

## Core Components

### `BaseCrudMock` (`base.py`)

This is the foundational class for all specific CRUD mocks. It provides core functionality:

*   **Response Configuration:** Define mock responses based on URL patterns and request attributes (params, data, json, headers) using `with_response()`. Includes helper methods for common HTTP errors (`with_not_found()`, `with_bad_request()`, `with_server_error()`, etc.). A `default_response` is used if no pattern matches.
*   **Request Recording:** Automatically records details of incoming mocked requests (method, URL, params, payload, headers, timestamp) in `request_history` as `RequestRecord` objects.
*   **Verification:** Offers various `verify_...` methods (e.g., `verify_request_count`, `verify_query_parameters`, `verify_body_parameters`, `verify_request_payload`, `verify_request_sequence`, `verify_error_handling`) to assert client behavior against the recorded history. The logic for these checks resides in `assertion_helpers.py`.
*   **Parent ID Handling:** Supports optional automatic URL prefixing for parent resources (`with_parent_id_handling`).

### `RequestRecord` (`request_record.py`)

A simple class used internally by the mocks to store details about each recorded request, including the method, URL, parameters, payload, headers, timestamp, and the `MockResponse` that was returned.

### Specific Operation Mocks

These classes inherit from `BaseCrudMock` and add behavior specific to each CRUD operation:

*   **`CreateMock` (`create.py`):** Mocks `POST` requests.
    *   Simulates unique field constraints (`with_unique_constraint`).
    *   Simulates custom field validation (`with_validation_constraint`).
    *   Provides optional auto-incrementing ID generation (`with_auto_increment_id`).
    *   Can raise `ValidationFailedError` (`exceptions.py`).
*   **`ReadMock` (`read.py`):** Mocks `GET` requests.
    *   Supports basic pattern matching like `BaseCrudMock` (`with_single_resource`, `with_resource_list`).
    *   Offers dynamic response generation based on internally stored resources (`set_stored_resources`). When using stored resources, it automatically handles:
        *   Retrieval of single items by ID (`/resource/{id}`).
        *   Filtering based on query parameters.
        *   Sorting (`sort` query parameter).
        *   Pagination (`page`/`limit` or `_page`/`_limit` query parameters).
        *   Field selection (`fields` query parameter).
*   **`UpdateMock` (`update.py`):** Mocks `PUT` and `PATCH` requests.
    *   Handles both full (`PUT`) and partial (`PATCH`) updates.
    *   Simulates concurrency control via ETags (`with_etag_concurrency`, checks `If-Match` header) or version numbers (`with_optimistic_locking`, checks field in payload).
    *   Simulates conditional updates (`with_conditional_update`).
    *   Can raise `ConcurrencyError` (`exceptions.py`).
    *   Can simulate concurrency conflicts (`with_concurrency_conflict`, returns 409).
*   **`DeleteMock` (`delete.py`):** Mocks `DELETE` requests.
    *   Simulates cascading deletes based on defined dependencies (`with_dependency`, `with_cascading_delete`).
    *   Simulates soft deletes (`with_soft_delete`), moving resources to an internal `_soft_deleted_resources` store.
    *   Simulates referential integrity checks (`with_referential_integrity_check`), preventing deletion if dependencies exist (returns 409).
    *   Provides verification methods for deletion status (`verify_resource_deleted`, `verify_dependencies_deleted`).

### `CombinedCrudMock` (`combined.py`)

Acts as a facade, holding instances of `CreateMock`, `ReadMock`, `UpdateMock`, and `DeleteMock`.

*   Delegates `get`, `post`, `put`, `patch`, `delete` calls to the appropriate underlying mock.
*   Aggregates `request_history` from all contained mocks.
*   Provides unified `verify_request_count` and `verify_request_sequence` methods.
*   Adds `verify_crud_operation_sequence` to easily verify sequences like `["create", "read", "delete"]`.

### `CrudMockFactory` (`factory.py`)

A simple factory providing static methods (`create()`, `read()`, `update()`, `delete()`, `combined()`) to conveniently create instances of the respective mock classes.

## Basic Usage

```python
from crudclient.testing.crud import CrudMockFactory

# Get a combined mock instance
mock = CrudMockFactory.combined()

# Configure the read mock to return a specific user
mock.read_mock.with_single_resource(
    url_pattern=r"/api/users/123$",
    resource_data={"id": 123, "name": "Test User", "email": "test@example.com"}
)

# --- In your test ---
# client = YourApiClient(http_session=mock) # Inject the mock
# user = client.get_user(123)
# assert user.name == "Test User"
# --- End of test code ---

# Verify the GET request was made
mock.verify_request_count(1, url_pattern=r"/api/users/123$")
mock.read_mock.verify_request_count(1, url_pattern=r"/api/users/123$") # Can also verify on specific mock

# Verify the sequence of operations (if multiple calls were made)
# mock.verify_crud_operation_sequence(["read"], resource_id="123")

```

This module provides a flexible way to isolate client code from actual backend services during testing, enabling robust verification of client-side logic and error handling related to CRUD operations.