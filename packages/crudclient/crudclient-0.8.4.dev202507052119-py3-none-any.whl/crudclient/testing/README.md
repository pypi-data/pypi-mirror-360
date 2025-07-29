# crudclient.testing

This package provides a comprehensive suite of tools for testing applications that utilize the `crudclient` library. It offers various utilities for mocking client behavior, verifying interactions, and simulating different API scenarios.

All utilities now provide inline type hints directly in the source files, and the previous `.pyi` stub files have been removed.

## Overview

The `crudclient.testing` module aims to facilitate robust testing by providing:

*   **Mock Clients:** Implementations like `MockClient` (via `MockClientFactory`) allow simulating the behavior of the actual `crudclient` without making real network requests.
*   **Factories:** The `MockClientFactory` provides convenient ways to create and configure mock client instances with specific responses, authentication methods, and error conditions. Helper functions in `factory_helpers.py` support this configuration.
*   **Verification:** The `Verifier` class enables assertions on interactions with mock objects or spies, ensuring methods were called as expected.
*   **Custom Exceptions:** A hierarchy of testing-specific exceptions (e.g., `TestingError`, `MockConfigurationError`, `VerificationError`) defined in `exceptions.py` helps pinpoint issues during tests.
*   **Shared Types:** Common type aliases (e.g., `Headers`, `StatusCode`, `ResponseData`) are defined in `types.py` for consistency.

## Submodules

The testing utilities are organized into the following submodules:

*   **[auth](./auth/README.md):** Contains mocks and helpers for testing various authentication strategies (API Key, Basic, Bearer, Custom, OAuth).
*   **[core](./core/README.md):** Provides the core mock client implementations (`MockClient`, `MockHTTPClient`).
*   **[crud](./crud/README.md):** Includes utilities specifically designed for testing CRUD operations defined via `crudclient.crud`.
*   **[doubles](./doubles/README.md):** Offers test doubles like `FakeAPI` and `DataStore` for simulating external systems or data storage.
*   **[helpers](./helpers/README.md):** Contains general-purpose helper functions and utilities useful across different testing scenarios.
*   **[response_builder](./response_builder/README.md):** Provides tools (`ResponseBuilder`, `APIPatternBuilder`, `MockResponse`) for constructing and configuring mock API responses.
*   **[spy](./spy/README.md):** Includes utilities (`SpyBase`, `MethodCall`) for spying on method calls to track interactions.

Refer to the `README.md` file within each subdirectory for detailed information about its specific components and usage.