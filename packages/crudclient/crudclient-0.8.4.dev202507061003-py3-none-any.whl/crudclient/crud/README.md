# crudclient.crud Module

This module provides the core framework for defining and interacting with API resources using CRUD (Create, Read, Update, Delete) patterns within the `crudclient` library. It offers a base class (`Crud`) that integrates endpoint construction, standard CRUD operations, custom actions, and response handling.

## Core Components

### 1. `Crud` Base Class (`base.py`)

The central piece is the generic `Crud[T]` class. Subclasses of `Crud` represent specific API resources. Key aspects include:

*   **Resource Path:** Each subclass *must* define a `_resource_path` class attribute (e.g., `"users"`, `"posts"`).
*   **Data Model:** Optionally, a `_datamodel` class attribute can be set to a Pydantic model (`Type[T]`). If provided, the module will attempt to validate request data against this model and parse responses into instances of this model.
*   **Client Integration:** A `Crud` instance is initialized with a `Client` object, which is used for making the actual HTTP requests.
*   **Parent Resources:** Supports nesting resources by accepting an optional `parent` `Crud` instance during initialization.
*   **Allowed Actions:** Controls which standard CRUD operations are permitted via the `allowed_actions` list (defaults to `["list", "create", "read", "update", "partial_update", "destroy"]`).
*   **Response Strategy:** Automatically initializes a response strategy (`DefaultResponseModelStrategy` or `PathBasedResponseModelStrategy`) to handle parsing and conversion of API responses based on configuration (`_datamodel`, `_api_response_model`, `_list_return_keys`, `_single_item_path`, `_list_item_path`).

### 2. Endpoint Construction (`endpoint.py`)

The `_get_endpoint` method (and its helpers) dynamically constructs the API endpoint URL for each operation. It considers:

*   The `_resource_path` of the `Crud` subclass.
*   Any provided resource IDs or action names (e.g., `resource_id` for `read`, `action` for `custom_action`).
*   The path of any `parent` resource, including its ID if provided via `parent_args`.
*   Optional static prefixes defined via `_endpoint_prefix`.

### 3. Operations (`operations.py`)

Standard CRUD operations are provided as methods on the `Crud` class:

*   `list(**kwargs)`: Performs a GET request to the resource's base endpoint.
*   `create(data, **kwargs)`: Performs a POST request with the provided `data`.
*   `read(resource_id, **kwargs)`: Performs a GET request to a specific resource endpoint.
*   `update(resource_id, data, **kwargs)`: Performs a PUT request to update a specific resource.
*   `partial_update(resource_id, data, **kwargs)`: Performs a PATCH request for partial updates.
*   `destroy(resource_id, **kwargs)`: Performs a DELETE request on a specific resource.
*   `custom_action(action, method="post", resource_id=None, **kwargs)`: Performs a request for non-standard actions on a resource or collection, allowing specification of the HTTP method, action name, and optional data/params.

These methods utilize the endpoint construction logic and delegate the actual HTTP call to the associated `client` instance. They also integrate data dumping and response conversion.

### 4. Request Data Dumping & Response Conversion (`response_conversion.py`)

This part handles the flow of data to and from the API:

*   **Request Data (`_dump_data`, `_dump_model_instance`, `_dump_dictionary`)**:
    *   Converts input data (Pydantic models or dictionaries) into JSON-serializable dictionaries suitable for request bodies (`POST`, `PUT`, `PATCH`).
    *   Performs validation against the `_datamodel` before sending, if applicable (distinguishing between full and partial updates).
    *   Handles potential `DataValidationError` if input data doesn't match the model.
*   **Response Handling (`_validate_response`, `_convert_to_model`, `_convert_to_list_model`, `_validate_list_return`)**:
    *   Validates the raw HTTP response (checking for basic structure, attempting JSON parsing).
    *   Uses the configured `ResponseModelStrategy` (`_response_strategy`) to parse the validated response data.
    *   Attempts to convert the response JSON into the specified `_datamodel` (for single items or lists).
    *   Handles potential `ResponseParsingError` or `DataValidationError` during response processing.
    *   Provides fallback mechanisms for list conversion if the primary strategy fails.

## Usage Example (Conceptual)

```python
from crudclient import Client
from crudclient.crud import Crud
from pydantic import BaseModel

# Define your data model
class User(BaseModel):
    id: int
    name: str
    email: str

# Create a Crud subclass for the 'users' resource
class UserCrud(Crud[User]):
    _resource_path = "users"
    _datamodel = User

# Initialize the client and the Crud instance
client = Client(base_url="https://api.example.com")
user_crud = UserCrud(client=client)

# --- Perform Operations ---

# List users
user_response: ApiResponse[User] = user_crud.list()
all_users: list[User] = user_response.data

# ``list`` may return an ``ApiResponse`` wrapper when a response model is
# configured. Access the ``data``/``values`` attribute to get the list of
# ``User`` instances instead of overriding the method to return a raw list.

# Create a new user
new_user_data = {"name": "Jane Doe", "email": "jane.doe@example.com"}
created_user: User = user_crud.create(data=new_user_data)

# Read a specific user
user_1: User = user_crud.read(resource_id=str(created_user.id))

# Update a user
update_data = {"name": "Jane Smith", "email": "jane.smith@example.com"}
updated_user: User = user_crud.update(resource_id=str(user_1.id), data=update_data)

# Partially update a user
partial_data = {"email": "jane.s@example.com"}
patched_user: User = user_crud.partial_update(resource_id=str(user_1.id), data=partial_data)

# Delete a user
user_crud.destroy(resource_id=str(patched_user.id))
```

This module forms the foundation for defining resource interactions in a structured and reusable way, leveraging Pydantic models for data validation and conversion.