# crudclient.testing.spy

This module provides test spy implementations for various components of the `crudclient` library. Spies are test doubles that wrap real objects to record interactions (like method calls, arguments, return values, and exceptions) without necessarily altering the original object's behavior. This allows tests to verify that specific methods were called as expected during a test scenario.

## Key Components

The module contains two main sets of spying tools: an enhanced system and a basic system.

### Enhanced Spying System

This is the primary system for spying, offering detailed call recording and flexible assertion capabilities.

*   **`EnhancedSpyBase`**: The core base class for enhanced spies. It records interactions as `CallRecord` objects and provides methods for retrieving and inspecting these calls (`get_calls`, `get_call_count`, `was_called`, `was_called_with`, `reset`). It inherits assertion logic from `SpyAssertionsMixin`.
*   **`CallRecord`**: A data class extending `MethodCall` to store detailed information about a single method invocation, including:
    *   Method name, positional arguments (`args`), keyword arguments (`kwargs`)
    *   Result or raised exception
    *   Timestamp of the call
    *   Execution duration
    *   Stack trace and caller information
*   **`SpyAssertionsMixin`**: Provides a comprehensive suite of assertion methods (e.g., `assert_called`, `assert_not_called`, `assert_called_with`, `assert_called_once`, `assert_called_times`, `assert_call_order`, `assert_no_errors`, `assert_no_unexpected_calls`, `assert_call_max_duration`) that operate on the recorded `CallRecord`s within an `EnhancedSpyBase` instance.
*   **`ClassSpy`**: Wraps an existing object instance. It replaces specified methods (or all public methods by default) with internal `MethodSpy` instances, recording all calls made to them. It inherits from `EnhancedSpyBase`.
*   **`FunctionSpy`**: Wraps a standalone function to record calls made to it. It inherits from `EnhancedSpyBase`.
*   **`MethodSpy`**: An internal helper class used by `ClassSpy` to wrap individual methods of the target object.
*   **`EnhancedSpyFactory`**: A utility class providing static methods (`create_class_spy`, `create_function_spy`, `patch_method`) for conveniently creating spy instances.

### Specific Enhanced Spies

These classes utilize the enhanced spying system to provide tailored spies for `crudclient` components:

*   **`ApiSpy`**: Wraps a `crudclient.api.API` instance using `ClassSpy`. It specifically spies on the `register_endpoint` method and provides custom verification methods like `verify_endpoint_registered` and `verify_endpoint_registered_with_model`.
*   **`ClientSpy`**: Wraps a `crudclient.client.Client` instance using `ClassSpy`. It spies on standard HTTP methods (`get`, `post`, `put`, `delete`, `patch`) and provides custom verification methods like `verify_endpoint_called`, `verify_endpoint_called_with_method`, and `verify_json_payload_sent`.
*   **`CrudSpy`**: Wraps a `crudclient.crud.base.Crud` instance using `ClassSpy`. It spies on standard CRUD operations (`list`, `get`, `create`, `update`, `delete`, etc.) and provides custom verification methods like `verify_resource_created`, `verify_resource_updated`, and `verify_resource_deleted`.

### Basic Spying System (Legacy)

This system provides simpler spying capabilities.

*   **`SpyBase`**: A base class that records calls as `MethodCall` objects. It provides basic verification methods (`verify_called`, `verify_not_called`, `verify_called_with`, `verify_call_count`) and corresponding deprecated `assert_*` methods.
*   **`MethodCall`**: A simple data class storing the method name, arguments (`args`, `kwargs`), return value, and any exception raised for a recorded call.

## Basic Usage Example

```python
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.spy import ClientSpy

# 1. Create a real client instance (or use a mock if needed by the spy's target)
config = ClientConfig(hostname="https://api.test.com")
real_client = Client(config)

# 2. Wrap the real client with the ClientSpy
client_spy = ClientSpy(config=config) # ClientSpy creates its own target Client internally

# 3. Use the spy in your code under test
# (Code that uses the client_spy instance)
try:
    client_spy.get("/users/1")
    client_spy.post("/users", json={"name": "Test User"})
except Exception:
    pass # Handle potential exceptions from the *real* client call

# 4. Verify interactions using assertion methods
client_spy.assert_called("get")
client_spy.assert_called_with("get", "/users/1")
client_spy.assert_called_with("post", "/users", json={"name": "Test User"})
client_spy.assert_called_times("get", 1)
client_spy.assert_call_order("get", "post")

# You can also access the recorded calls directly
get_calls = client_spy.get_calls("get")
print(f"GET call details: {get_calls[0]}")
```

**Note:** Spies in this module primarily record interactions by wrapping real objects. By default, they allow the call to proceed to the wrapped object (`record_only=False`). The enhanced spies (`ClassSpy`, `FunctionSpy`) can be configured with `record_only=True` to prevent the call to the original object/function, effectively acting more like a stub in that mode while still recording the call attempt.