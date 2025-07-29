# crudclient Package

This directory contains core components of the `crudclient` library. It provides the primary `Client` for HTTP interactions, the `API` base class for structuring API interfaces, `ClientConfig` for configuration, base data `models`, custom `exceptions`, shared `types`, and re-exports core `Crud` elements.

## Top-Level Components

The primary files in this directory define foundational elements of the client:

*   **`client.py`**: Contains the `Client` class. This class provides high-level methods for HTTP requests (GET, POST, PUT, DELETE, PATCH) and delegates the underlying HTTP operations (session management, authentication, retries, response/error handling) to an `HttpClient` instance (from the `http` submodule). It is configured using a `ClientConfig` object.
*   **`api.py`**: Defines the abstract base class `API`. Subclasses implement specific API interfaces by registering `Crud` resources and `ResourceGroup` instances. It manages a `Client` instance (either provided or initialized via `ClientConfig`) and handles its lifecycle, including closing connections.
*   **`config.py`**: Provides the `ClientConfig` class for configuring `Client` instances. It holds settings like base URL components (`hostname`, `version`), request `timeout`, `retries`, custom `headers`, logging flags, and the `auth_strategy` (from the `auth` submodule) used for authentication.
*   **`exceptions.py`**: Defines the base `CrudClientError` and various specific exception classes for handling errors related to configuration (`ConfigurationError`), authentication (`AuthenticationError`), network issues (`NetworkError`), API responses (e.g., `APIError`, `BadRequestError`, `NotFoundError`, `ForbiddenError`), data validation (`DataValidationError`), and response parsing (`ResponseParsingError`).
*   **`groups.py`**: Defines the `ResourceGroup` class, which inherits from `Crud` and provides a way to group related CRUD resources under a common path segment. It enables typed, hierarchical nesting of API resources, improving type hinting and code organization.
*   **`models.py`**: Contains core Pydantic models used for data representation and validation within API responses, specifically `Link` (for hyperlinks), `PaginationLinks` (for pagination), and the generic `ApiResponse` (for structured responses with data, count, and links).
*   **`types.py`**: Defines shared type aliases used across the library, including `JSONDict`, `JSONList`, and `RawResponse`/`RawResponseSimple` for representing various data structures and response formats.
*   **`crud.py`**: Re-exports core elements related to CRUD operations from the `crudclient.crud` submodule, specifically the `Crud` base class and associated types (`HttpMethodString`, `CrudInstance`, `CrudType`, `T`).
*   **`__init__.py`**: Initializes the `crudclient` package, sets up basic logging (using `NullHandler`), and explicitly exports the main public components (`Client`, `API`, `ClientConfig`, `Crud`, `ApiResponse`, key exceptions, and types) via `__all__`.
*   **`__main__.py`**: This file is currently empty and does not provide a command-line interface.

## Submodules

The `crudclient` package is organized into several submodules, each handling a specific aspect of the library's functionality:

*   **[auth.py](./auth.py)**: Re-exports authentication strategies from apiconfig library (Basic, Bearer, ApiKey, Custom auth).
*   **[crud](./crud/README.md)**: Defines the structure and implementation for CRUD (Create, Read, Update, Delete) operations against API endpoints.
*   **[http](./http/README.md)**: Contains lower-level HTTP handling logic, including the `HttpClient`, request/response objects, error handling, retry strategies, and session management.
*   **[response_strategies](./response_strategies/README.md)**: Provides different strategies for processing and interpreting API responses.
*   **[testing](./testing/README.md)**: Offers utilities and tools for testing applications that use the `crudclient` library, including mocks, factories, and verification helpers.