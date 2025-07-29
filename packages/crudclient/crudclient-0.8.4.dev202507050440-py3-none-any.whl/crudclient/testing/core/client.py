"""Mock Object Pattern Implementation for ``crudclient.Client``.

This module provides ``MockClient``, an implementation of the **Mock Object
pattern** for the ``crudclient.client.Client`` interface. It allows tests to
simulate client behavior, configure specific responses or errors for defined
request patterns, and verify interactions without making actual network calls.
"""

import json
import time
from typing import Any, Dict, List, Optional, Pattern, Union

from crudclient.auth import AuthStrategy
from crudclient.config import ClientConfig
from crudclient.exceptions import AuthenticationError
from crudclient.testing.spy.enhanced import EnhancedSpyBase

from ..response_builder.pagination import (
    PaginationResponseBuilder,  # Import the builder class
)
from ..response_builder.response import (
    MockResponse,  # Import MockResponse for type hint
)
from ..types import (
    Headers,
    HttpMethod,
    QueryParams,
    RequestBody,
    ResponseBody,
    StatusCode,
)


class ResponseWrapper:
    """
    A wrapper class for HTTP responses to provide convenient access to data.

    Parameters
    ----------
    response : Any
        The raw HTTP response object.
    """

    def __init__(self, response: Any) -> None:
        """
        Initialize the ResponseWrapper.

        Parameters
        ----------
        response : Any
            The raw HTTP response object.
        """
        self.response = response
        self.data = None
        if hasattr(response, "_content") and response._content is not None:
            if response.headers.get("Content-Type") == "application/json":
                self.data = json.loads(response._content.decode("utf-8"))
            else:
                self.data = response._content.decode("utf-8")
        else:
            self.data = {}

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the wrapped response object.

        Parameters
        ----------
        name : str
            The name of the attribute to access.

        Returns
        -------
        Any
            The attribute from the wrapped response.
        """
        return getattr(self.response, name)

    def __getitem__(self, key: str) -> Any:
        """
        Allow dictionary-like access to the response data if it's a dictionary.

        Parameters
        ----------
        key : str
            The key to access in the response data.

        Returns
        -------
        Any
            The value associated with the key.

        Raises
        ------
        TypeError
            If the response data is not a dictionary.
        """
        if isinstance(self.data, dict):
            return self.data[key]
        raise TypeError(f"Cannot index response data of type {type(self.data)}")

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the response data if it's a dictionary.

        Parameters
        ----------
        key : str
            The key to check for.

        Returns
        -------
        bool
            True if the key exists, False otherwise.
        """
        if isinstance(self.data, dict):
            return key in self.data
        return False

    def json(self) -> Optional[ResponseBody]:
        """
        Return the parsed JSON data from the response.

        Returns
        -------
        Optional[ResponseBody]
            The JSON data, or None if not available.
        """
        return self.data


# Import PaginationHelper


class MockClient(EnhancedSpyBase):
    """
    A mock client for testing API interactions, extending EnhancedSpyBase for call recording.

    This class simulates HTTP requests and allows for configuring predefined responses,
    network conditions, and authentication strategies for testing purposes.

    Parameters
    ----------
    http_client : Any
        The underlying mock HTTP client (e.g., MockHTTPClient) that handles
        response configuration and network conditions.
    base_url : Optional[str], optional
        The base URL for the mock client. If None, it attempts to derive it from
        `http_client` or defaults to "https://api.example.com".
    config : Optional[ClientConfig], optional
        A client configuration object. If None, a default configuration is created.
    enable_spy : bool, optional
        If True, enables call recording for this mock client. Defaults to False.
    **kwargs : Any
        Additional keyword arguments for future flexibility.
    """

    def __init__(
        self,
        http_client: Any,
        base_url: Optional[str] = None,
        config: Optional[ClientConfig] = None,
        enable_spy: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the MockClient.

        Parameters
        ----------
        http_client : Any
            The underlying mock HTTP client.
        base_url : Optional[str], optional
            The base URL for the mock client.
        config : Optional[ClientConfig], optional
            A client configuration object.
        enable_spy : bool, optional
            If True, enables call recording.
        **kwargs : Any
            Additional keyword arguments.
        """
        super().__init__()  # Initialize the EnhancedSpyBase

        self.http_client = http_client
        self.base_url = base_url or getattr(http_client, "base_url", "https://api.example.com")
        self.enable_spy = enable_spy

        self.config = config or ClientConfig(hostname=self.base_url)

        self._auth_strategy: Optional[AuthStrategy] = None

    def configure_response(
        self,
        method: HttpMethod,
        path: str,
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        """
        Configure a specific response for a given HTTP method and path.

        Parameters
        ----------
        method : HttpMethod
            The HTTP method (e.g., "GET", "POST").
        path : str
            The exact URL path to match.
        status_code : StatusCode, optional
            The HTTP status code for the response. Defaults to 200.
        data : Optional[ResponseBody], optional
            The response body data. Defaults to None.
        headers : Optional[Headers], optional
            Additional response headers. Defaults to None.
        error : Optional[Exception], optional
            An exception to raise instead of returning a response. Defaults to None.
        """
        self.http_client.configure_response(method=method, path=path, status_code=status_code, data=data, headers=headers, error=error)

    def with_response_pattern(
        self,
        method: HttpMethod,
        path_pattern: Union[str, Pattern],
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        """
        Configure a response for HTTP methods matching a regex path pattern.

        Parameters
        ----------
        method : HttpMethod
            The HTTP method (e.g., "GET", "POST").
        path_pattern : Union[str, Pattern]
            A string or regex pattern to match against the URL path.
        status_code : StatusCode, optional
            The HTTP status code for the response. Defaults to 200.
        data : Optional[ResponseBody], optional
            The response body data. Defaults to None.
        headers : Optional[Headers], optional
            Additional response headers. Defaults to None.
        error : Optional[Exception], optional
            An exception to raise instead of returning a response. Defaults to None.
        """
        self.http_client.with_response_pattern(
            method=method, path_pattern=path_pattern, status_code=status_code, data=data, headers=headers, error=error
        )

    def with_network_condition(self, latency_ms: float = 0.0) -> None:
        """
        Configure network conditions, such as introducing latency.

        Parameters
        ----------
        latency_ms : float, optional
            The simulated network latency in milliseconds. Defaults to 0.0.
        """
        self.http_client.with_network_condition(latency_ms=latency_ms)

    def with_rate_limiter(self, limit: int, window_seconds: int) -> None:
        """
        Configure a mock rate limiter.

        This method is primarily for signaling and does not enforce rate limits
        within this mock client. It can be used to simulate rate limit
        configuration for testing purposes.

        Parameters
        ----------
        limit : int
            The maximum number of requests allowed within the window.
        window_seconds : int
            The time window in seconds for the rate limit.
        """
        print(f"MockClient: Rate limiting configured (limit={limit}, window={window_seconds}s). Not enforced by this stub.")

    def set_auth_strategy(self, auth_strategy: AuthStrategy) -> None:
        """
        Set the authentication strategy for the mock client.

        Parameters
        ----------
        auth_strategy : AuthStrategy
            The authentication strategy to use.
        """
        self._auth_strategy = auth_strategy
        self.config.auth_strategy = auth_strategy

    def get_auth_strategy(self) -> Optional[AuthStrategy]:
        """
        Get the currently configured authentication strategy.

        Returns
        -------
        Optional[AuthStrategy]
            The authentication strategy, or None if not set.
        """
        return self._auth_strategy

    def _prepare_request_args(
        self,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
    ) -> Dict[str, Any]:
        """
        Prepare request arguments by applying the authentication strategy.

        Parameters
        ----------
        headers : Optional[Headers], optional
            Initial request headers. Defaults to None.
        params : Optional[QueryParams], optional
            Initial query parameters. Defaults to None.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing 'headers' and 'params' with authentication
            details applied.
        """
        final_headers = headers.copy() if headers else {}
        final_params = params.copy() if params else {}

        if self._auth_strategy:
            auth_headers = self._auth_strategy.prepare_request_headers()
            auth_params = self._auth_strategy.prepare_request_params()
            if auth_headers:
                final_headers.update(auth_headers)
            if auth_params:
                final_params.update(auth_params)

        return {"headers": final_headers, "params": final_params}

    def _execute_http_method(
        self,
        method_name: str,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a simulated HTTP method with timing and call recording.

        Parameters
        ----------
        method_name : str
            The name of the HTTP method (e.g., "GET", "POST").
        path : str
            The URL path for the request.
        headers : Optional[Headers], optional
            Request headers. Defaults to None.
        params : Optional[QueryParams], optional
            Query parameters. Defaults to None.
        data : Optional[RequestBody], optional
            Request body data for POST/PUT/PATCH requests. Defaults to None.
        **kwargs : Any
            Additional keyword arguments to pass to the underlying HTTP method.

        Returns
        -------
        Any
            The wrapped response object or a raw response for special cases.

        Raises
        ------
        AuthenticationError
            If the response status code is 401 or 403.
        Exception
            For other HTTP errors (status code >= 400).
        """
        request_args = self._prepare_request_args(headers, params)
        start_time = time.time()
        response = None
        result = None
        exception = None

        try:
            http_method = getattr(self.http_client, method_name.lower())

            if method_name.upper() in ["POST", "PUT", "PATCH"]:
                response = http_method(path, data=data, **request_args, **kwargs)
            else:
                response = http_method(path, **request_args, **kwargs)

            if hasattr(response, "__class__") and response.__class__.__name__ == "MagicMock":
                result = response
                return result

            if (
                hasattr(response, "status_code")
                and hasattr(response, "headers")
                and response.status_code == 401
                and "WWW-Authenticate" in response.headers
            ):
                auth_header = response.headers["WWW-Authenticate"]
                if "mfa_token_required" in auth_header:
                    result = response
                    return result

            if hasattr(response, "status_code") and response.status_code >= 400:
                error_message = ""
                if hasattr(response, "_content") and response._content is not None:
                    if response.headers.get("Content-Type") == "application/json":
                        error_data = json.loads(response._content.decode("utf-8"))
                        if isinstance(error_data, dict):
                            error_message = error_data.get("message", "")
                            if not error_message and "error" in error_data:
                                error_message = error_data.get("error", "")
                    else:
                        error_message = response._content.decode("utf-8")

                if response.status_code == 401 or response.status_code == 403:
                    raise AuthenticationError(f"{response.status_code} {error_message}")
                else:
                    raise Exception(f"Request failed with status code {response.status_code}: {error_message}")

            result = ResponseWrapper(response)
            return result
        except Exception as e:
            exception = e
            raise
        finally:
            duration = time.time() - start_time

            call_kwargs = {"headers": request_args["headers"], "params": request_args["params"]}
            if data is not None:
                call_kwargs["data"] = data
            call_kwargs.update(kwargs)

            self._record_call(
                method_name=method_name.upper(), args=(path,), kwargs=call_kwargs, result=result, exception=exception, duration=duration
            )

    def get(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Any:
        """
        Simulate an HTTP GET request.

        Parameters
        ----------
        path : str
            The URL path for the GET request.
        headers : Optional[Headers], optional
            Request headers. Defaults to None.
        params : Optional[QueryParams], optional
            Query parameters. Defaults to None.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        Any
            The wrapped response object.
        """
        return self._execute_http_method("GET", path, headers, params, **kwargs)

    def post(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        """
        Simulate an HTTP POST request.

        Parameters
        ----------
        path : str
            The URL path for the POST request.
        headers : Optional[Headers], optional
            Request headers. Defaults to None.
        params : Optional[QueryParams], optional
            Query parameters. Defaults to None.
        data : Optional[RequestBody], optional
            Request body data. Defaults to None.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        Any
            The wrapped response object.
        """
        return self._execute_http_method("POST", path, headers, params, data, **kwargs)

    def put(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        """
        Simulate an HTTP PUT request.

        Parameters
        ----------
        path : str
            The URL path for the PUT request.
        headers : Optional[Headers], optional
            Request headers. Defaults to None.
        params : Optional[QueryParams], optional
            Query parameters. Defaults to None.
        data : Optional[RequestBody], optional
            Request body data. Defaults to None.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        Any
            The wrapped response object.
        """
        return self._execute_http_method("PUT", path, headers, params, data, **kwargs)

    def delete(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Any:
        """
        Simulate an HTTP DELETE request.

        Parameters
        ----------
        path : str
            The URL path for the DELETE request.
        headers : Optional[Headers], optional
            Request headers. Defaults to None.
        params : Optional[QueryParams], optional
            Query parameters. Defaults to None.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        Any
            The wrapped response object.
        """
        return self._execute_http_method("DELETE", path, headers, params, **kwargs)

    def patch(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        """
        Simulate an HTTP PATCH request.

        Parameters
        ----------
        path : str
            The URL path for the PATCH request.
        headers : Optional[Headers], optional
            Request headers. Defaults to None.
        params : Optional[QueryParams], optional
            Query parameters. Defaults to None.
        data : Optional[RequestBody], optional
            Request body data. Defaults to None.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        Any
            The wrapped response object.
        """
        return self._execute_http_method("PATCH", path, headers, params, data, **kwargs)

    def create_paginated_response(
        self,
        items: List[Any],
        per_page: int,
        base_url: str,
        page: int = 1,
    ) -> MockResponse:
        """
        Create a mock paginated response.

        Parameters
        ----------
        items : List[Any]
            A list of items to paginate.
        per_page : int
            The number of items per page.
        base_url : str
            The base URL for generating pagination links.
        page : int, optional
            The current page number. Defaults to 1.

        Returns
        -------
        MockResponse
            A mock response object representing a paginated API response.
        """
        return PaginationResponseBuilder.create_paginated_response(items=items, page=page, per_page=per_page, base_url=base_url)

    def reset(self) -> None:
        """
        Reset the mock client's state, including call history and HTTP client.
        """
        super().reset()
        if hasattr(self.http_client, "reset"):
            self.http_client.reset()
