"""
Module `client.py`.

This module defines the HttpClient class, which is responsible for making HTTP requests.
It provides a clean interface for making requests while delegating specialized concerns
to other components.
"""

import logging
import time
from collections.abc import Callable
from typing import Any, Dict, Literal, Optional, Tuple, Union, cast, overload

import requests
from requests.exceptions import HTTPError

from ..config import ClientConfig
from ..exceptions import (
    APIError,
    BadRequestError,
    ClientAuthenticationError,
    ConflictError,
    CrudClientError,
    ForbiddenError,
    InternalServerError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)
from ..ratelimit import get_rate_limiter
from ..types import RawResponseSimple
from .errors import ErrorHandler
from .logging import HttpLifecycleLogger
from .request import RequestFormatter
from .response import ResponseHandler
from .retry import RetryHandler
from .session import SessionManager

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Makes HTTP requests and delegates specialized concerns to other components.

    This class is responsible for making HTTP requests while delegating session management,
    request preparation, response handling, error handling, and retry logic to specialized
    components.

    Detailed logging of the HTTP request/response lifecycle (including potential
    redaction of sensitive data) can be configured via the `ClientConfig`.
    See `docs/logging.md` for more details.

    Attributes
    ----------
    config : ClientConfig
        Configuration object for the client.
    session_manager : SessionManager
        Manages the HTTP session.
    request_formatter : RequestFormatter
        Formats request data.
    response_handler : ResponseHandler
        Processes HTTP responses.
    error_handler : ErrorHandler
        Handles error responses.
    retry_handler : RetryHandler
        Manages retry policies.
    http_logger : HttpLifecycleLogger
        Logger for HTTP request/response lifecycle.
    rate_limiter : Optional[Any]
        RateLimiter instance if enabled.
    """

    config: ClientConfig
    session_manager: SessionManager
    request_formatter: RequestFormatter
    response_handler: ResponseHandler
    error_handler: ErrorHandler
    retry_handler: RetryHandler
    http_logger: HttpLifecycleLogger
    rate_limiter: Optional[Any]

    def __init__(
        self,
        config: ClientConfig,
        session_manager: Optional[SessionManager] = None,
        request_formatter: Optional[RequestFormatter] = None,
        response_handler: Optional[ResponseHandler] = None,
        error_handler: Optional[ErrorHandler] = None,
        retry_handler: Optional[RetryHandler] = None,
    ) -> None:
        """
        Initialize the HttpClient with a configuration and optional components.

        Parameters
        ----------
        config : ClientConfig
            Configuration for the client.
        session_manager : Optional[SessionManager], optional
            Session manager component. If not provided, a new one will be created.
        request_formatter : Optional[RequestFormatter], optional
            Request formatter component. If not provided, a new one will be created.
        response_handler : Optional[ResponseHandler], optional
            Response handler component. If not provided, a new one will be created.
        error_handler : Optional[ErrorHandler], optional
            Error handler component. If not provided, a new one will be created.
        retry_handler : Optional[RetryHandler], optional
            Retry handler component. If not provided, a new one will be created.

        Raises
        ------
        TypeError
            If the provided config is not a ClientConfig object.
        """
        if not isinstance(config, ClientConfig):
            raise TypeError("config must be a ClientConfig object")

        self.config = config
        self.session_manager = session_manager or SessionManager(config)
        self.request_formatter = request_formatter or RequestFormatter(config=self.config)
        self.response_handler = response_handler or ResponseHandler()
        self.error_handler = error_handler or ErrorHandler()
        self.retry_handler = retry_handler or RetryHandler(max_retries=config.retries or 0)
        self.http_logger = HttpLifecycleLogger(config=config, logger=logger)

        self.rate_limiter = get_rate_limiter(config)

    def _handle_request_response(self, response: requests.Response, handle_response: bool) -> Any:
        """
        Handle the successful response or error during response processing.

        Parameters
        ----------
        response : requests.Response
            The raw HTTP response.
        handle_response : bool
            Whether to process the response using ResponseHandler.

        Returns
        -------
        Any
            The processed response data or the raw response object.
        """
        response.raise_for_status()

        if not handle_response:
            return response
        return self.response_handler.handle_response(response)

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
    ) -> Any:  # noqa: C901
        """
        Internal method to make an HTTP request with validation, auth, retry, and error handling.

        Parameters
        ----------
        method : str
            HTTP method (e.g., 'GET', 'POST').
        endpoint : Optional[str], optional
            API endpoint path (relative to base_url).
        url : Optional[str], optional
            Full URL (overrides endpoint if provided).
        handle_response : bool, optional
            Whether to process the response using ResponseHandler. Defaults to True.
        **kwargs : Any
            Additional arguments passed to requests.request.

        Returns
        -------
        Any
            Processed response data (RawResponseSimple) if handle_response is True,
            otherwise the raw requests.Response object.

        Raises
        ------
        TypeError
            If input parameters have incorrect types.
        ValueError
            If neither endpoint nor url is provided.
        requests.HTTPError
            If the request fails and is not handled by ErrorHandler.
        Various exceptions from AuthStrategy or ResponseHandler/ErrorHandler.
        """
        if not isinstance(handle_response, bool):
            raise TypeError(f"handle_response must be a boolean, got {type(handle_response).__name__}")

        final_url, prepared_kwargs = self.request_formatter.format_request(method, endpoint, url, **kwargs)

        logger.debug(f"Preparing {method} request to {final_url} with final params: {prepared_kwargs.get('params')}")

        def make_request() -> requests.Response:
            if self.rate_limiter:
                self.rate_limiter.check_and_wait()

            self.http_logger.log_request_details(method, final_url, prepared_kwargs)
            response = self.session_manager.session.request(method, final_url, timeout=self.session_manager.timeout, **prepared_kwargs)

            if self.rate_limiter and response.headers:
                self.rate_limiter.update_from_headers(response.headers)

            return response

        start_time = time.monotonic()
        attempt_count: int = 0
        final_outcome: Union[requests.Response, Exception, None] = None

        try:
            final_outcome, attempt_count = self._execute_request_with_retry(method, final_url, make_request, handle_response)
            return final_outcome

        except HTTPError as e:
            final_outcome = e.response if e.response is not None else e
            self.http_logger.log_http_error(e, method=method, url=final_url)
            self._handle_http_error(e)

        except NetworkError as e:
            final_outcome = e
            raise e

        except Exception as e:
            final_outcome = e
            logger.exception("An unexpected error occurred during the request to %s: %s", final_url, e)
            if not isinstance(e, CrudClientError):
                raise CrudClientError(f"An unexpected error occurred: {e}") from e
            else:
                raise e
        finally:
            self.http_logger.log_request_completion(start_time, method, final_url, attempt_count, final_outcome)

    def _execute_request_with_retry(
        self, method: str, url: str, make_request_func: Callable[[], requests.Response], handle_response: bool
    ) -> Tuple[Any, int]:
        """
        Execute the HTTP request using the session manager and retry handler.

        Parameters
        ----------
        method : str
            The HTTP method.
        url : str
            The URL for the request.
        make_request_func : Callable[[], requests.Response]
            A callable that performs the actual HTTP request.
        handle_response : bool
            Whether to process the response using ResponseHandler.

        Returns
        -------
        Tuple[Any, int]
            A tuple containing the processed response data or raw response, and the attempt count.

        Raises
        ------
        CrudClientError
            If an unexpected result type is returned from the retry handler.
        Exception
            If an exception occurred during the request.
        """
        result_tuple = self.retry_handler.execute_with_retry(
            method, url, make_request_func, self.session_manager.session, self.session_manager.refresh_auth
        )
        result, attempt_count = result_tuple

        if isinstance(result, requests.Response):
            response = result
            self.http_logger.log_response_details(method, url, response)

            processed_or_raw_response = self._handle_request_response(response, handle_response)
            return processed_or_raw_response, attempt_count

        elif isinstance(result, Exception):
            raise result
        else:
            raise CrudClientError(f"Unexpected result type from retry handler: {type(result).__name__}")

    def _handle_http_error(self, e: HTTPError) -> None:
        """
        Handle HTTP errors using the error handler.

        Parameters
        ----------
        e : HTTPError
            The HTTPError exception.

        Raises
        ------
        APIError
            A more specific API error based on the HTTP status code.
        """
        response = e.response
        request = e.request

        if response is not None:
            STATUS_CODE_TO_EXCEPTION = {
                400: BadRequestError,
                401: ClientAuthenticationError,
                403: ForbiddenError,
                404: NotFoundError,
                409: ConflictError,
                422: UnprocessableEntityError,
                429: RateLimitError,
                500: InternalServerError,
                503: ServiceUnavailableError,
            }
            exception_cls = STATUS_CODE_TO_EXCEPTION.get(response.status_code, APIError)

            raise exception_cls(
                f"HTTP error occurred: {response.status_code} {response.reason}",
                request=cast(Any, request),
                response=cast(Any, response),
            ) from e
        else:
            raise APIError(f"HTTP error occurred without a response: {e}", request=cast(Any, request), response=None) from e

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
        return self._request("GET", endpoint=endpoint, params=params)

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
        return self._request("POST", endpoint=endpoint, data=data, json=json, files=files, params=params)

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
        return self._request("PUT", endpoint=endpoint, data=data, json=json, files=files, params=params)

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
        request_kwargs = kwargs.copy()
        if params is not None:
            request_kwargs["params"] = params
        return cast(RawResponseSimple, self._request("DELETE", endpoint=endpoint, **request_kwargs))

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
        return self._request("PATCH", endpoint=endpoint, data=data, json=json, files=files, params=params)

    def _prepare_data(
        self,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Prepare request data based on the provided parameters.

        This method delegates to the request_formatter to prepare the request data
        and set the appropriate content-type headers.

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
        Dict[str, Any]
            A dictionary containing the prepared request data and headers.

        Raises
        ------
        TypeError
            If the parameters are of incorrect types.
        """
        return {"data": data, "json": json, "files": files}

    def request_raw(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, **kwargs: Any) -> requests.Response:
        """
        Make a raw HTTP request and return the Response object without processing.

        This method is useful when you need access to the raw response object
        for custom processing.

        Parameters
        ----------
        method : str
            The HTTP method to use (GET, POST, PUT, DELETE, PATCH).
        endpoint : Optional[str], optional
            The API endpoint to request. Either endpoint or url must be provided.
        url : Optional[str], optional
            The full URL to request. Either endpoint or url must be provided.
        **kwargs : Any
            Additional keyword arguments to pass to the request.

        Returns
        -------
        requests.Response
            The raw Response object.

        Raises
        ------
        ValueError
            If neither endpoint nor url is provided.
        TypeError
            If the parameters are of incorrect types.
        """
        return self._request(method, endpoint, url, handle_response=False, **kwargs)

    def close(self) -> None:
        """
        Close the HTTP session and clean up resources.

        This method should be called when the client is no longer needed
        to ensure proper cleanup of resources.
        """
        self.session_manager.close()
        logger.debug("HttpClient closed.")
