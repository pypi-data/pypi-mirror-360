# crudclient.testing.doubles

This module provides test doubles (Fakes and Stubs) to facilitate testing applications built with the `crudclient` library. Test doubles replace real dependencies, allowing for isolated, faster, and more predictable tests.

This module offers two primary types of test doubles:

1.  **Fakes (`FakeAPI`, `FakeCrud`, `DataStore`):** These provide a higher-fidelity, in-memory simulation of the actual API's behavior. They are useful for integration-style tests where you need to verify interactions and basic business logic without making real network calls.
2.  **Stubs (`StubAPI`, `StubCrud`, `StubClient`, `StubResponse`):** These return predefined, canned responses to specific calls. They are useful for unit tests where you need to control the exact data returned by a dependency or simulate specific edge cases or error conditions.

## Fake Components

Fakes simulate the behavior of the `crudclient` components using an in-memory data store.

### `DataStore`

The core of the Fake implementation. `DataStore` provides an in-memory simulation of a database or backend storage.

*   **Collections:** Manages data organized into named collections (like database tables).
*   **CRUD Operations:** Supports `create`, `get`, `list`, `update`, `delete` operations.
*   **Bulk Operations:** Supports `bulk_create`, `bulk_update`, `bulk_delete`.
*   **Features:** Includes support for filtering, sorting, pagination, relationships (one-to-one, one-to-many, many-to-many), validation rules, unique constraints, soft deletes, and automatic timestamp tracking (`_created_at`, `_updated_at`).
*   **Configuration:** Allows defining relationships, validation rules, and unique constraints programmatically.

### `FakeCrud`

Acts as a fake implementation for a single CRUD endpoint (e.g., `/users`). It interacts with a `DataStore` instance to perform operations.

*   **API Simulation:** Translates `DataStore` results and exceptions into API-like responses. For example, it raises `FakeAPIError` with appropriate status codes (404, 422, 409) instead of returning `None` or internal `DataStore` exceptions.
*   **Model Conversion:** Can automatically convert data dictionaries from the `DataStore` into specified model instances upon retrieval.

### `FakeAPI`

The main entry point for using Fakes. It acts as a container for multiple `FakeCrud` endpoints, all sharing a single underlying `DataStore`.

*   **Endpoint Registration:** Use `register_endpoint()` to define resources managed by the fake API.
*   **Shared State:** All registered `FakeCrud` instances operate on the same `DataStore`, allowing tests to verify interactions between different resources.
*   **DataStore Configuration:** Provides methods (`define_relationship`, `add_validation_rule`, `add_unique_constraint`) to configure the shared `DataStore`.

**Example Usage (FakeAPI):**

```python
from crudclient.testing.doubles import FakeAPI
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

# Create a Fake API instance
fake_api = FakeAPI()

# Register a 'users' endpoint, optionally associating it with a model
users_crud = fake_api.register_endpoint(name="users", endpoint="/users", model=User)

# Add a unique constraint on email within the 'users' collection
fake_api.add_unique_constraint(fields="email", collection="users", error_message="Email must be unique")

# Use the fake CRUD endpoint like the real one
new_user_data = {"name": "Alice", "email": "alice@example.com"}
created_user = users_crud.create(new_user_data)
# created_user will be a User instance: User(id=1, name='Alice', email='alice@example.com')

retrieved_user = users_crud.get(created_user.id)
# retrieved_user will also be a User instance

all_users = users_crud.list()
# all_users will be a list containing the User instance

# Attempting to create another user with the same email will raise FakeAPIError (422)
try:
    users_crud.create({"name": "Bob", "email": "alice@example.com"})
except FakeAPIError as e:
    print(f"Caught expected error: {e.status_code} - {e.detail}")

```

## Stub Components

Stubs provide canned responses or simple behaviors, useful for isolating components in unit tests.

### `StubResponse`

A helper class to create predefined HTTP-like response objects. You can specify the status code, content (JSON, text, bytes), and headers.

### `StubCrud`

A stub implementation for a single CRUD endpoint. It offers several ways to configure its behavior:

*   **Predefined Responses:** Use `configure_list()`, `configure_get()`, `configure_create()` to set specific return values (often `StubResponse` instances) for operations.
*   **Handler Functions:** Provide custom functions (`handler=...`) to dynamically determine the response based on input arguments.
*   **Simple Internal Store:** If no specific response or handler is configured, it falls back to a basic internal dictionary for simple CRUD simulation (less sophisticated than `DataStore`).
*   **Hooks:** Set `before_*` and `after_*` hooks to execute custom logic before or after specific operations.

### `StubAPI`

A container for `StubCrud` endpoints.

*   **Endpoint Registration:** Use `register_endpoint()` to add `StubCrud` instances.
*   **Shared Simple Store:** Manages a simple shared dictionary (`_data_store`) that can be used by the default behavior of its contained `StubCrud` instances. Provides methods like `populate_data_store` and `clear_data_store` to manage this simple state.

### `StubClient`

A stub implementation of the low-level `crudclient.Client`. It intercepts HTTP method calls (`get`, `post`, `put`, `delete`, `patch`) and returns configured responses.

*   **Response Mapping:** Use `add_response(pattern, response)` to define responses (including `StubResponse` objects or handler functions) based on URL patterns or method prefixes (e.g., `"^GET:"`).
*   **Default Response:** Set a fallback response using `set_default_response()`.
*   **Network Simulation:** Can simulate network latency (`set_latency()`) and random errors (`set_error_rate()`).
*   **Spying:** Inherits from `EnhancedSpyBase`, allowing inspection of calls made to the client (arguments, results, exceptions, duration).

**Example Usage (StubClient):**

```python
from crudclient.config import ClientConfig
from crudclient.testing.doubles import StubClient, StubResponse

# Configure the StubClient
config = ClientConfig(hostname="https://test.com")
stub_client = StubClient(config)

# Configure a specific response for GET /users/1
user_1_response = StubResponse(status_code=200, content={"id": 1, "name": "Alice"})
stub_client.add_response("^GET:/users/1$", user_1_response)

# Configure a default 404 for other GET requests
not_found_response = StubResponse(status_code=404, content={"detail": "Not Found"})
stub_client.set_default_response(not_found_response) # Or configure per method: stub_client.add_response("^GET:", not_found_response)


# Make calls using the stub client
response1 = stub_client.get("/users/1")
# response1 will be {"id": 1, "name": "Alice"}

try:
    stub_client.get("/users/2")
except requests.exceptions.HTTPError as e:
    # The default StubResponse(404) will raise an HTTPError
    print(f"Caught expected error: {e.response.status_code}")

# Inspect calls made to the stub
calls = stub_client.get_calls()
print(f"Number of calls: {len(calls)}")
print(f"First call args: {calls[0].args}")
print(f"First call result: {calls[0].result}")
```

## Choosing Between Fakes and Stubs

*   Use **Fakes** (`FakeAPI`) when:
    *   You need to test the interaction between multiple components or resources.
    *   You need a functional simulation of the backend logic (e.g., validation, relationships).
    *   You are writing integration-style tests for your service layer.
*   Use **Stubs** (`StubAPI`, `StubClient`, `StubCrud`) when:
    *   You need to provide specific, canned data for a unit test.
    *   You want to isolate the component under test from its dependencies completely.
    *   You need to simulate specific error conditions or edge cases returned by the API.
    *   You need fine-grained control over the responses returned by the HTTP client or CRUD operations.