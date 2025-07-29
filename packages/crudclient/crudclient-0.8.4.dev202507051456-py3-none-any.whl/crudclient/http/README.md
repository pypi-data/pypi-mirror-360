# crudclient.http Module

This module encapsulates the HTTP communication layer for the `crudclient` library. It provides the necessary components for making HTTP requests, handling responses, managing sessions, implementing retry logic, handling errors, and logging the request/response lifecycle.

## Core Components

### `HttpClient`
The central class responsible for executing HTTP requests (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`). It orchestrates the request lifecycle by utilizing several helper components:
*   `SessionManager`: Manages the underlying `requests.Session`.
*   `RequestFormatter`: Prepares the outgoing request (URL, headers, body).
*   `ResponseHandler`: Parses successful responses.
*   `ErrorHandler`: Handles HTTP error responses by mapping them to specific exceptions.
*   `RetryHandler`: Manages the logic for retrying failed requests.
*   `HttpLifecycleLogger`: Provides detailed logging for requests and responses.

It takes a `ClientConfig` object for configuration and allows customization by optionally providing instances of the helper components. It exposes standard HTTP methods and a `request_raw` method to get the raw `requests.Response` object.

### `SessionManager`
Manages a `requests.Session` instance. It configures the session based on `ClientConfig`, setting up:
*   Authentication (using `AuthStrategy` from `ClientConfig` or fallback methods).
*   Default headers.
*   Basic retry settings via `requests.adapters.HTTPAdapter`.
*   Request timeouts.
It provides methods to update headers, refresh authentication, and close the session.

### `RequestFormatter`
Responsible for preparing the details of an outgoing HTTP request before it's sent:
*   **URL Construction:** Builds the final request URL using the `base_url` from `ClientConfig` and the provided endpoint, or uses a fully qualified URL if given.
*   **Authentication Parameters:** Integrates authentication details into request parameters if the configured `AuthStrategy` supports `prepare_request_params`.
*   **Body Formatting:** Prepares the request body based on provided `data`, `json`, or `files` arguments, setting the appropriate `Content-Type` header (e.g., `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data`).

### `ResponseHandler`
Handles successful HTTP responses (`response.ok` is True).
*   Parses the response body based on the `Content-Type` header (JSON, binary/octet-stream, or plain text).
*   Returns `None` for `204 No Content` responses.
*   Raises a `ResponseParsingError` if JSON decoding fails for a response declared as `application/json`.

### `ErrorHandler`
Handles HTTP error responses (`response.ok` is False).
*   Maps specific HTTP error status codes (e.g., 400, 401, 404, 500, 503) to corresponding `CrudClientError` subclasses (e.g., `BadRequestError`, `ClientAuthenticationError`, `NotFoundError`, `InternalServerError`, `ServiceUnavailableError`).
*   Attempts to parse the error response body (JSON or text).
*   Raises the mapped exception, falling back to `APIError` for unmapped codes or if the response is missing.
*   Allows registration of custom status code-to-exception mappings.

### Retry Mechanism
Provides robust handling for transient network issues or specific server errors.
*   **`RetryHandler`:** Orchestrates the retry process. It executes the request function, checks if a retry is needed based on the outcome (response status or exception), calculates the delay using a `RetryStrategy`, and performs the retry up to a configured maximum number of attempts. It can also trigger an authentication refresh (`setup_auth_func`) before retrying on a 401 status.
*   **`RetryCondition`:** Defines *whether* a retry should be attempted. Conditions can be based on:
    *   Specific HTTP status codes (e.g., 500, 503).
    *   Specific exception types (e.g., `requests.exceptions.Timeout`, `requests.exceptions.ConnectionError`).
    *   Predefined `RetryEvent` enums (e.g., `SERVER_ERROR`, `TIMEOUT`).
    *   Custom callback functions.
    The default condition retries on common server errors (500, 502, 503, 504) and network issues (Timeout, ConnectionError).
*   **`RetryStrategy`:** Defines *how long* to wait between retries.
    *   `ExponentialBackoffStrategy` (Default): Increases the delay exponentially with each attempt, optionally adding jitter.
    *   `FixedRetryStrategy`: Uses a constant delay.

### `HttpLifecycleLogger`
Provides detailed logging throughout the HTTP request and response lifecycle, configured via `ClientConfig`.
*   Logs request details (method, URL, parameters, headers).
*   Logs response details (status code, reason, headers).
*   Optionally logs request and response bodies (truncating long bodies).
*   Redacts sensitive information (e.g., passwords, tokens, API keys) from logged headers and JSON bodies using helpers from `crudclient.http.utils`.
*   Logs the final outcome (success or failure), attempt count, and total duration of the request.

### Utilities (`utils.py`)
Contains helper functions primarily used for logging:
*   `redact_sensitive_headers`: Redacts known sensitive headers (e.g., `Authorization`, `Cookie`) and prefixes (e.g., `X-API-Key`).
*   `redact_json_body`: Recursively redacts known sensitive keys (e.g., `password`, `token`, `api_key`) within JSON-like dictionary/list structures.

## Key Exports

The following components are exposed by this module:

*   `HttpClient`
*   `SessionManager`
*   `RequestFormatter`
*   `ResponseHandler`
*   `ErrorHandler`
*   `RetryHandler`
*   `RetryStrategy` (ABC)
*   `FixedRetryStrategy`
*   `ExponentialBackoffStrategy`
*   `RetryCondition`
*   `RetryEvent` (Enum)