"""
Client module for making API requests.

This module provides the Client class for making API requests to RESTful services.
It handles request preparation, authentication, response handling, and error handling.
"""

import logging
from typing import Any, Dict, Literal, Optional, Tuple, Type, Union, cast, overload

import requests

from .config import ClientConfig
from .exceptions import ConfigurationError, ForbiddenError
from .http.client import HttpClient
from .types import RawResponseSimple

log = logging.getLogger(__name__)


class Client:
    """
    Client class for making API requests.

    Attributes
    ----------
    config : ClientConfig
        Configuration object for the client.
    http_client : HttpClient
        The HTTP client used for making requests.
    base_url : str
        The base URL for the API.

    This class delegates HTTP operations to the HttpClient class, which handles
    request preparation, authentication, response handling, and error handling.
    It can be used as a context manager to ensure the session is closed
    automatically:

    ```python
    config = ClientConfig(hostname="https://api.example.com")
    with Client(config) as client:
        data = client.get("/users")
    ```
    """

    config: ClientConfig
    http_client: HttpClient
    base_url: str

    def __init__(self, config: Union[ClientConfig, Dict[str, Any]]) -> None:
        """
        Initialize the Client.

        Parameters
        ----------
        config : Union[ClientConfig, Dict[str, Any]]
            Configuration for the client. Can be a ClientConfig object or a dictionary
            containing parameters like `base_url`, `auth_strategy`, `timeout`, and logging settings
            (`log_request_body`, `log_response_body`).

        Raises
        ------
        ConfigurationError
            If the provided config is invalid (wrong type, missing fields, invalid values).

        Logging behavior (e.g., request/response body logging) can be controlled
        via the `logging` section of the configuration. By default, logging is
        disabled using a `NullHandler`. See `docs/logging.md` for details.
        """
        log.info("Initializing Client and processing configuration...")

        # Use a helper function to process the config
        # This avoids mypy unreachable code warnings
        self.config = self._process_config(config)

        try:
            self.base_url = str(self.config.base_url)  # Ensure it's a string after validation
        except ValueError as e:
            log.error("Configuration validation failed for base_url: %s", e, exc_info=True)
            raise ConfigurationError(f"Invalid base_url configuration: {e}") from e

        self.http_client = HttpClient(self.config)
        log.info(
            "Client configuration processed successfully. Base URL: %s, Log Request Body: %s, Log Response Body: %s",
            self.base_url,
            self.config.log_request_body,
            self.config.log_response_body,
        )

        self._session = self.http_client.session_manager.session

    def _setup_auth(self) -> None:
        """
        Set up authentication for the session.

        This method is provided for backward compatibility with existing tests.
        It delegates to the HttpClient's session_manager.
        """
        self.http_client.session_manager.refresh_auth()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        """
        Make a GET request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to request.
        params : Optional[Dict[str, Any]], optional
            Query parameters to include in the request. Defaults to None.

        Returns
        -------
        RawResponseSimple
            The processed response data.

        Raises
        ------
        TypeError
            If the parameters are of incorrect types.
        """
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")

        try:
            raw_response = self.http_client.request_raw("GET", endpoint, params=params)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            kwargs = {"params": params} if params else {}
            assert e.response is not None  # Ensure response exists for retry logic
            # Attempt retry. If it doesn't happen or fails, _maybe_retry_after_403 returns the original response.
            raw_response = self._maybe_retry_after_403("GET", url, kwargs, cast(requests.Response, e.response))
            # If the status code is still 403 after attempting retry, re-raise the original error.
            if raw_response.status_code == 403:
                raise e
            # Otherwise, the retry was successful (or wasn't needed), proceed with the response

        return self._handle_response(raw_response)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Make a POST request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to request.
        data : Optional[Dict[str, Any]], optional
            Form data to include in the request. Defaults to None.
        json : Optional[Any], optional
            JSON data to include in the request. Defaults to None.
        files : Optional[Dict[str, Any]], optional
            Files to include in the request. Defaults to None.
        params : Optional[Dict[str, Any]], optional
            Query parameters to include in the request. Defaults to None.

        Returns
        -------
        RawResponseSimple
            The processed response data.

        Raises
        ------
        TypeError
            If the parameters are of incorrect types.
        """
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")

        try:
            raw_response = self.http_client.request_raw("POST", endpoint, data=data, json=json, files=files, params=params)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            kwargs = {}
            if data:
                kwargs["data"] = data
            if json:
                kwargs["json"] = json
            if files:
                kwargs["files"] = files
            if params:
                kwargs["params"] = params
            assert e.response is not None  # Ensure response exists for retry logic
            raw_response = self._maybe_retry_after_403("POST", url, kwargs, cast(requests.Response, e.response))
            if raw_response.status_code == 403:
                raise e

        return self._handle_response(raw_response)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Make a PUT request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to request.
        data : Optional[Dict[str, Any]], optional
            Form data to include in the request. Defaults to None.
        json : Optional[Any], optional
            JSON data to include in the request. Defaults to None.
        files : Optional[Dict[str, Any]], optional
            Files to include in the request. Defaults to None.
        params : Optional[Dict[str, Any]], optional
            Query parameters to include in the request. Defaults to None.

        Returns
        -------
        RawResponseSimple
            The processed response data.

        Raises
        ------
        TypeError
            If the parameters are of incorrect types.
        """
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")

        try:
            raw_response = self.http_client.request_raw("PUT", endpoint, data=data, json=json, files=files, params=params)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            kwargs = {}
            if data:
                kwargs["data"] = data
            if json:
                kwargs["json"] = json
            if files:
                kwargs["files"] = files
            if params:
                kwargs["params"] = params
            assert e.response is not None  # Ensure response exists for retry logic
            raw_response = self._maybe_retry_after_403("PUT", url, kwargs, cast(requests.Response, e.response))
            if raw_response.status_code == 403:
                raise e

        return self._handle_response(raw_response)

    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> RawResponseSimple:
        """
        Make a DELETE request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to request.
        params : Optional[Dict[str, Any]], optional
            Query parameters to include in the request. Defaults to None.
        **kwargs : Any
            Additional keyword arguments to pass to the request.

        Returns
        -------
        RawResponseSimple
            The processed response data.

        Raises
        ------
        TypeError
            If the parameters are of incorrect types.
        """
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")

        try:
            # Capture original kwargs for potential retry
            request_kwargs = kwargs.copy()
            if params is not None:
                request_kwargs["params"] = params
            raw_response = self.http_client.request_raw("DELETE", endpoint, **request_kwargs)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            # Use the captured kwargs for the retry call
            assert e.response is not None  # Ensure response exists for retry logic
            raw_response = self._maybe_retry_after_403("DELETE", url, request_kwargs, cast(requests.Response, e.response))
            if raw_response.status_code == 403:
                raise e

        return self._handle_response(raw_response)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Make a PATCH request to the specified endpoint.

        Parameters
        ----------
        endpoint : str
            The API endpoint to request.
        data : Optional[Dict[str, Any]], optional
            Form data to include in the request. Defaults to None.
        json : Optional[Any], optional
            JSON data to include in the request. Defaults to None.
        files : Optional[Dict[str, Any]], optional
            Files to include in the request. Defaults to None.
        params : Optional[Dict[str, Any]], optional
            Query parameters to include in the request. Defaults to None.

        Returns
        -------
        RawResponseSimple
            The processed response data.

        Raises
        ------
        TypeError
            If the parameters are of incorrect types.
        """
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")

        try:
            raw_response = self.http_client.request_raw("PATCH", endpoint, data=data, json=json, files=files, params=params)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            kwargs = {}
            if data:
                kwargs["data"] = data
            if json:
                kwargs["json"] = json
            if files:
                kwargs["files"] = files
            if params:
                kwargs["params"] = params
            assert e.response is not None  # Ensure response exists for retry logic
            raw_response = self._maybe_retry_after_403("PATCH", url, kwargs, cast(requests.Response, e.response))
            if raw_response.status_code == 403:
                raise e

        return self._handle_response(raw_response)

    @overload
    def _request(
        self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: Literal[True] = True, **kwargs: Any
    ) -> RawResponseSimple:
        pass

    @overload
    def _request(
        self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: Literal[False] = False, **kwargs: Any
    ) -> requests.Response:
        pass

    def _request(
        self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: bool = True, **kwargs: Any
    ) -> Union[RawResponseSimple, requests.Response]:
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")

        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")

        if not isinstance(handle_response, bool):
            raise TypeError(f"handle_response must be a boolean, got {type(handle_response).__name__}")
        # Use the correct return type based on handle_response
        if handle_response:
            return self.http_client._request(method, endpoint, url, True, **kwargs)
        else:
            return self.http_client._request(method, endpoint, url, False, **kwargs)

    def close(self) -> None:
        """
        Close the HTTP client and clean up resources.

        This method should be called when the client is no longer needed
        to ensure proper cleanup of resources.
        """
        self.http_client.close()
        # Ensure the session exposes the `is_closed` attribute even if it
        # wasn't accessed prior to calling ``close``. Accessing the
        # ``session`` property attaches a dynamic ``is_closed`` property
        # to the underlying ``requests.Session`` instance that proxies the
        # value from ``SessionManager``.
        _ = self.session
        log.debug("Client closed.")

    def __enter__(self) -> "Client":
        """Enter the runtime context and return the client instance."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        """Exit the runtime context and close the client."""
        self.close()

    @property
    def session(self) -> requests.Session:
        """
        Get the HTTP session.

        Returns
        -------
        requests.Session
            The HTTP session.
        """
        if not hasattr(self._session, "is_closed"):
            setattr(self._session.__class__, "is_closed", property(lambda s: getattr(self.http_client.session_manager, "is_closed", False)))
        return self._session

    def _prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """
        Prepare request data based on the provided parameters.

        Parameters
        ----------
        data : Optional[Dict[str, Any]], optional
            Form data to include in the request.
        json : Optional[Any], optional
            JSON data to include in the request.
        files : Optional[Dict[str, Any]], optional
            Files to include in the request.

        Returns
        -------
        Tuple[Dict[str, str], Dict[str, Any]]
            A tuple containing:
                - Headers dictionary with the appropriate content-type.
                - A dictionary containing the prepared request data.
        """
        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        headers = {}
        request_kwargs = {}

        if json is not None:
            headers["Content-Type"] = "application/json"
            request_kwargs["json"] = json
        elif files is not None:
            headers["Content-Type"] = "multipart/form-data"
            request_kwargs["files"] = files
            if data is not None:
                request_kwargs["data"] = data
        elif data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            request_kwargs["data"] = data

        return headers, request_kwargs

    def _maybe_retry_after_403(self, method: str, url: str, kwargs: Dict[str, Any], response: requests.Response) -> requests.Response:
        """
        Retry a request after receiving a 403 Forbidden response.

        Parameters
        ----------
        method : str
            The HTTP method for the request.
        url : str
            The URL for the request.
        kwargs : Dict[str, Any]
            Additional keyword arguments for the request.
        response : requests.Response
            The response from the original request.

        Returns
        -------
        requests.Response
            The response from the retry or the original response if no retry.
        """
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if not isinstance(url, str):
            raise TypeError(f"url must be a string, got {type(url).__name__}")

        if not isinstance(kwargs, dict):
            raise TypeError(f"kwargs must be a dictionary, got {type(kwargs).__name__}")

        # Simplified type checking for response
        is_response = isinstance(response, requests.Response)
        is_mock = hasattr(response, "_mock_spec") and requests.Response in getattr(response, "_mock_spec", [])

        if not (is_response or is_mock):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        if response.status_code != 403:
            return response

        if not self.config.should_retry_on_403():
            return response

        log.debug("403 Forbidden received. Attempting retry via config handler.")
        self.config.handle_403_retry(self)
        self._setup_auth()
        retry_response = self._session.request(method, url, **kwargs)
        return retry_response

    def _handle_response(self, response: requests.Response) -> RawResponseSimple:
        """
        Handle the response from the API based on the content type.

        Parameters
        ----------
        response : requests.Response
            The response object from the API.

        Returns
        -------
        RawResponseSimple
            The parsed response content.
        """
        # Simplified type checking for response
        is_response = isinstance(response, requests.Response)
        is_mock = hasattr(response, "_mock_spec") and requests.Response in getattr(response, "_mock_spec", [])

        if not (is_response or is_mock):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")

        try:
            return self.http_client.response_handler.handle_response(response)
        except requests.HTTPError:
            self._handle_error_response(response)
            return None  # Should not be reached, but satisfies type checker

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.

        Parameters
        ----------
        response : requests.Response
            The response object from the API.

        Raises
        ------
        AuthenticationError
            If the status code is 401 (Unauthorized).
        NotFoundError
            If the status code is 404 (Not Found).
        CrudClientError
            For other error status codes.
        """
        # Simplified type checking for response
        is_response = isinstance(response, requests.Response)
        is_mock = hasattr(response, "_mock_spec") and requests.Response in getattr(response, "_mock_spec", [])

        if not (is_response or is_mock):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        self.http_client.error_handler.handle_error_response(response)

    def _process_config(self, config: Union[ClientConfig, Dict[str, Any]]) -> ClientConfig:
        """
        Process and validate the configuration.

        Parameters
        ----------
        config : Union[ClientConfig, Dict[str, Any]]
            The configuration object or dictionary.

        Returns
        -------
        ClientConfig
            The processed configuration object.

        Raises
        ------
        ConfigurationError
            If the configuration is invalid.
        """
        # Simple implementation that handles all cases
        if isinstance(config, ClientConfig):
            return config

        # Using a separate variable to help mypy understand the control flow
        is_dict = isinstance(config, dict)

        if is_dict:
            try:
                return ClientConfig(**config)
            except (TypeError, ValueError) as e:
                log.error("Configuration validation failed when creating ClientConfig from dict: %s", e, exc_info=True)
                raise ConfigurationError(f"Invalid configuration dictionary provided: {e}") from e

        # This will only be reached if config is neither ClientConfig nor dict
        message = f"Invalid config type provided: expected ClientConfig or dict, got {type(config).__name__}."
        log.error(message)
        raise ConfigurationError(message)
