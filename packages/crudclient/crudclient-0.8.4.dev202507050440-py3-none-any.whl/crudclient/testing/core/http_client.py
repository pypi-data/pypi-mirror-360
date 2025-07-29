"""Mock HTTP client implementation.

This module provides a mock implementation of the ``crudclient.http.Client``
class that can be used in tests to simulate HTTP requests and responses without
making actual network calls.
"""

import json
import re
import time  # Added
from typing import (  # Added List, Pattern, Union
    Any,
    Dict,
    List,
    Optional,
    Pattern,
    Tuple,
    Union,
)
from urllib.parse import urljoin

import requests
from requests import Response

from ..exceptions import RequestNotConfiguredError

# Import EnhancedSpyBase
from ..spy.enhanced import EnhancedSpyBase
from ..types import (
    Headers,
    HttpMethod,
    QueryParams,
    RequestBody,
    ResponseBody,
    StatusCode,
)


# Inherit from EnhancedSpyBase to add spying capabilities
class MockHTTPClient(EnhancedSpyBase):
    """Mock implementation of the crudclient.http.Client class.

    This class simulates HTTP requests and responses without making actual
    network calls. It allows configuring expected requests and their responses
    for testing purposes, including exact path matches and regex pattern
    matching. It also supports simulating basic network conditions like latency.
    """

    def __init__(self, base_url: str = "https://api.example.com") -> None:
        """Initialize a new MockHTTPClient.

        Args:
            base_url: The base URL for the mock client.
        """

        # Initialize SpyBase first
        EnhancedSpyBase.__init__(self)

        self.base_url = base_url
        # Store exact path matches
        self._configured_responses: Dict[Tuple[HttpMethod, str], Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]] = {}
        # Store path patterns (regex) - LIFO (last added pattern checked first)
        self._configured_patterns: List[Tuple[HttpMethod, Pattern, Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]]] = []
        # Network conditions
        self._latency_ms: float = 0.0

    def reset(self) -> None:
        """Reset the mock HTTP client to its initial state, clearing all configurations."""

        # Reset spy calls along with mock configuration
        EnhancedSpyBase.reset(self)
        self._configured_responses = {}
        self._configured_patterns = []
        self._latency_ms = 0.0

    def configure_response(
        self,
        method: HttpMethod,
        path: str,
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        """Configure a response for a specific request with an exact path match.

        This configuration takes precedence over patterns defined with
        :meth:`with_response_pattern`.

        Args:
            method: The HTTP method of the request (e.g., 'GET', 'POST').
            path: The exact path of the request (e.g., '/users/1').
            status_code: The HTTP status code to return (default: 200).
            data: The data to return in the response body (default: None).
            headers: The headers to return in the response (default: None).
            error: An exception to raise instead of returning a response (default: None).
        """

        # Normalize the method to uppercase
        method = method.upper()

        # Normalize the path to remove leading slash if present
        path = path.lstrip("/")

        # Store the configured response
        self._configured_responses[(method, path)] = (status_code, data if error is None else (data or {}), headers or {}, error)

    def with_response_pattern(
        self,
        method: HttpMethod,
        path_pattern: Union[str, Pattern],
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        """Configure a response for requests matching a path pattern (regex).

        Patterns are checked in reverse order of addition (LIFO). The first
        matching pattern for the given method and path will be used. Exact
        matches configured with :meth:`configure_response` take precedence.

        Args:
            method: The HTTP method of the request (e.g., 'GET', 'POST').
            path_pattern: A regex string or compiled pattern to match against the request path.
            status_code: The HTTP status code to return (default: 200).
            data: The data to return in the response body (default: None).
            headers: The headers to return in the response (default: None).
            error: An exception to raise instead of returning a response (default: None).
        """

        # Normalize the method to uppercase
        method = method.upper()

        # Compile pattern if it's a string
        if isinstance(path_pattern, str):
            # Ensure pattern doesn't start with / for consistency with path normalization
            if path_pattern.startswith("/"):
                # Simple adjustment, might need refinement based on usage
                path_pattern = path_pattern.lstrip("/")
            pattern = re.compile(path_pattern)
        else:
            pattern = path_pattern

        # Store the configured pattern and response
        self._configured_patterns.append((method, pattern, (status_code, data or {}, headers or {}, error)))

    def with_network_condition(
        self,
        latency_ms: float = 0.0,
        # Future: packet_loss_rate: float = 0.0
    ) -> None:
        """Configure simulated network conditions for the mock client.

        Delegates to the underlying HTTP client's network condition configuration.
        Currently supports simulating latency.

        Args:
            latency_ms: The delay in milliseconds to add before processing each request (default: 0.0).

        Raises:
            ValueError: If latency_ms is negative.
        """

        if latency_ms < 0:
            raise ValueError("Latency cannot be negative.")
        self._latency_ms = latency_ms
        # self._packet_loss_rate = packet_loss_rate

    def _get_configured_response(self, method: HttpMethod, path: str) -> Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]:
        """Find a configured response, checking exact matches first, then patterns (LIFO).

        Args:
            method: The HTTP method of the request.
            path: The path of the request.

        Returns:
            A tuple of ``(status_code, response_body, headers, error)``.

        Raises:
            RequestNotConfiguredError: If no response is configured for the request
                (neither exact match nor pattern match).
        """

        # Normalize the method to uppercase
        method = method.upper()

        # Normalize the path to remove leading slash if present
        path = path.lstrip("/")

        # 1. Check for exact match
        exact_key = (method, path)
        if exact_key in self._configured_responses:
            return self._configured_responses[exact_key]

        # 2. Check for pattern match (LIFO - iterate in reverse)
        for pattern_method, pattern, response_config in reversed(self._configured_patterns):
            if pattern_method == method and pattern.search(path):
                return response_config

        # 3. No match found
        raise RequestNotConfiguredError(method, path)

    def request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any,
    ) -> Response:
        """Make a mock HTTP request, applying configured responses and network conditions.

        Args:
            method: The HTTP method of the request.
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments (ignored by mock, but captured).

        Returns:
            A :class:`requests.Response` object with the configured response.

        Raises:
            RequestNotConfiguredError: If no response is configured for the request.
            Exception: If an error is configured for the request.
            ValueError: If network conditions are invalid (e.g., negative latency).
        """

        start_request_time = time.time()
        response: Optional[Response] = None
        recorded_exception: Optional[Exception] = None
        try:
            # Simulate latency if configured
            if self._latency_ms > 0:
                time.sleep(self._latency_ms / 1000.0)

            # Find the configured response (checks exact then patterns)
            status_code, response_body, response_headers, error = self._get_configured_response(method=method, path=path)

            # If an error is configured, capture and raise it
            if error is not None:
                recorded_exception = error
                raise error

            # Create a Response object
            url = urljoin(self.base_url, path)
            response = requests.Response()
            response.status_code = status_code
            response.headers.update(response_headers or {})

            # Handle response body
            if response_body is None:
                response._content = None
            elif isinstance(response_body, bytes):
                response._content = response_body
            elif isinstance(response_body, str):
                response._content = response_body.encode("utf-8")
            else:
                try:
                    response._content = json.dumps(response_body).encode("utf-8")
                    if "content-type" not in (h.lower() for h in response.headers):
                        response.headers["Content-Type"] = "application/json"
                except TypeError:
                    response._content = str(response_body).encode("utf-8")

            response.url = url
            response.request = requests.Request(method=method.upper(), url=url, headers=headers, data=data, params=params).prepare()

            return response  # Return the successfully created response

        except Exception as e:
            # Capture any exception raised during the process
            if recorded_exception is None:  # Avoid overwriting configured error
                recorded_exception = e
            raise  # Re-raise the exception

        finally:
            # Record the call regardless of outcome
            duration = time.time() - start_request_time
            call_args = (method, path)
            call_kwargs = {"headers": headers, "params": params, "data": data, **kwargs}
            # 'response' might not be assigned if an exception occurred early
            call_result = response if "response" in locals() and recorded_exception is None else None
            self._record_call(
                method_name="request", args=call_args, kwargs=call_kwargs, result=call_result, exception=recorded_exception, duration=duration
            )

    # Convenience methods for common HTTP methods

    def get(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Response:
        """Make a mock GET request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A :class:`requests.Response` object with the configured response.
        """

        return self.request(method="GET", path=path, headers=headers, params=params, **kwargs)

    def post(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        """Make a mock POST request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A :class:`requests.Response` object with the configured response.
        """

        return self.request(method="POST", path=path, headers=headers, params=params, data=data, **kwargs)

    def put(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        """Make a mock PUT request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A :class:`requests.Response` object with the configured response.
        """

        return self.request(method="PUT", path=path, headers=headers, params=params, data=data, **kwargs)

    def delete(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Response:
        """Make a mock DELETE request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A :class:`requests.Response` object with the configured response.
        """

        return self.request(method="DELETE", path=path, headers=headers, params=params, **kwargs)

    def patch(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        """Make a mock PATCH request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A :class:`requests.Response` object with the configured response.
        """

        return self.request(method="PATCH", path=path, headers=headers, params=params, data=data, **kwargs)
