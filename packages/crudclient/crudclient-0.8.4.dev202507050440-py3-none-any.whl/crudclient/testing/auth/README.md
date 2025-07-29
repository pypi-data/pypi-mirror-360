# crudclient.testing.auth

This module provides mock implementations and utility functions specifically designed for testing various authentication strategies used with the `crudclient`. It allows simulating different authentication scenarios, including success, failure modes, token expiration, rate limiting, and more, without needing a live authentication server.

## Core Concepts

The primary component is the `AuthMockBase` abstract class, which serves as the foundation for all specific authentication mock implementations. It provides common attributes and methods for configuring mock behavior, such as:

*   Simulating authentication failures (`with_failure`, `fail_after`).
*   Simulating token expiration and refresh logic (`with_token_expiration`, `with_expired_token`, `with_refresh_token`, `refresh`).
*   Simulating Multi-Factor Authentication (MFA) requirements (`with_mfa_required`).
*   Adding custom headers or parameters (`with_custom_header`, `with_custom_param`).

Each concrete mock class inherits from `AuthMockBase` and implements the logic specific to a particular authentication strategy (e.g., Basic, Bearer, API Key).

## Mock Implementations

The following mock classes are provided:

*   **`BasicAuthMock`**: Simulates HTTP Basic Authentication.
    *   Validates username/password credentials.
    *   Supports configuring multiple valid credentials, username patterns, password complexity rules, case sensitivity, and maximum login attempts.
    *   Generates the appropriate `Authorization: Basic ...` header.
*   **`BearerAuthMock`**: Simulates Bearer Token Authentication (often used with OAuth 2.0).
    *   Manages token lifecycle: issuance, validation (including expiration), revocation.
    *   Stores token metadata (scopes, user ID, client ID).
    *   Supports token format validation (regex patterns, prefixes).
    *   Implements token refresh logic using a refresh token.
    *   Generates the appropriate `Authorization: Bearer ...` header.
*   **`ApiKeyAuthMock`**: Simulates API Key Authentication (via headers or query parameters).
    *   Uses helper classes:
        *   `ApiKeyValidator`: Manages key validity (format, expiration, revocation) and metadata (owner, permissions, tier).
        *   `ApiKeyRateLimiter`: Implements sliding window rate limiting.
        *   `ApiKeyUsageTracker`: Tracks API key usage counts (total and per-endpoint).
    *   Can be configured to send the key via a specified header (e.g., `X-API-Key`) or query parameter.
*   **`OAuthMock`**: Simulates various OAuth 2.0 flows.
    *   Uses helper classes:
        *   `OAuthTokenManager`: Manages the storage and lifecycle of access tokens, refresh tokens, authorization codes, and user credentials (for password grant).
        *   `OAuthScopeValidator`: Manages available and required scopes, validating requested scopes.
        *   `OAuthGrantHandler`: Orchestrates the logic for different grant types (Authorization Code, Client Credentials, Password, Refresh Token).
    *   Configurable client credentials, URLs, scopes, and grant types.
    *   Provides a `CustomAuth` strategy internally to generate the `Authorization: Bearer ...` header based on the managed token state.
*   **`CustomAuthMock`**: Simulates flexible or non-standard authentication schemes.
    *   Relies on user-provided callback functions (`header_callback`, `param_callback`) to dynamically generate authentication headers or parameters.
    *   Integrates spying capabilities (inherits from `EnhancedSpyBase`) to record calls to callbacks and verification methods.
    *   Allows defining expected/required headers/parameters and custom validation functions for verification during tests.

## Factory Functions

The `factory.py` module provides convenient functions (`create_basic_auth_mock`, `create_bearer_auth_mock`, etc.) to instantiate these mock classes with common configurations, simplifying test setup.

## Verification Helpers

Authentication verification utilities are provided directly by `apiconfig.testing.auth_verification`:

*   **`AuthHeaderVerification`** (from `apiconfig.testing`): Methods to verify the format and structure of `Authorization` headers (Basic, Bearer, API Key).
*   **`AuthTokenVerification`**: Methods to verify token properties, primarily for JWTs (expiration, scopes, client ID, user) and refresh behavior.
*   **`AuthErrorVerification`**: Methods to verify authentication error responses (status code, error codes) and standard rate limit headers.
*   **`AuthExtractionUtils`**: Methods to parse credentials/tokens from Basic/Bearer headers and extract payloads from JWTs.
*   **`AuthTestHelpers`**: Convenience wrappers for asserting auth headers were applied using the `apiconfig` utilities.

These helpers can be used in tests to assert that the client is sending the correct authentication information or that the mock is behaving as expected.

## Basic Usage Example

```python
# Example using BasicAuthMock (requires a mock client setup, not shown here)
from crudclient.testing.auth import create_basic_auth_mock
from crudclient.testing import create_mock_client # Assumed import

# 1. Create the auth mock
basic_auth_mock = create_basic_auth_mock(username="testuser", password="testpassword")

# 2. Create a mock client using the auth mock's strategy
mock_client = create_mock_client(base_url="http://mock.api", auth_strategy=basic_auth_mock.get_auth_strategy())

# 3. Configure mock responses (details depend on mock client implementation)
# mock_client.add_response(...)

# 4. Make a request using the client
# response = mock_client.get("/protected/resource")

# 5. Assertions (using verification helpers or mock client spies)
# For example, check if the correct header was sent (details depend on spy implementation)
# request_spy = mock_client.get_request_spy(...)
# assert request_spy.calls[0].request.headers["Authorization"] == "Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk"