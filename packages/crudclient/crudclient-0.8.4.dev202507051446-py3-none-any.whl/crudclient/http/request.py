"""Module `request.py`.

This module defines the RequestFormatter class, which is responsible for handling request
preparation and content-type setting. It provides methods for formatting different types of
requests (JSON, form data, multipart) and setting the appropriate content-type headers.

Class `RequestFormatter`
------------------------
The `RequestFormatter` class provides a flexible way to prepare request data based on the
content type. It includes methods for different content types (JSON, form data, multipart)
and handles the appropriate content-type header setting.

To use the RequestFormatter:
    1. Create a RequestFormatter instance.
    2. Use the appropriate method to prepare the request data.
    3. Apply the returned headers and data to your request.

Example
-------
>>> formatter = RequestFormatter()
>>> prepared_data, headers = formatter.prepare_json({"name": "example"})
>>> # Use prepared_data and headers in your request

Classes
-------
- RequestFormatter: Main class for request preparation and formatting.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from ..exceptions import CrudClientError  # Import base exception

# Set up logging
if TYPE_CHECKING:
    from ..auth import AuthStrategy  # Use the correct class name
    from ..config import ClientConfig  # Type hint for config
logger = logging.getLogger(__name__)


class RequestFormatter:
    """Handles request preparation and content-type setting.

    This class is responsible for formatting request data based on the content type
    and providing the appropriate content-type headers. It supports JSON, form data,
    and multipart requests.

    Methods
    -------
    prepare_data
        Prepares request data based on the provided parameters.
    prepare_json
        Prepares JSON request data.
    prepare_form_data
        Prepares form data request.
    prepare_multipart
        Prepares multipart form data request.
    get_content_type_header
        Returns the content-type header for a given content type.
    """

    def __init__(self, config: Optional["ClientConfig"] = None) -> None:
        """Initialize the RequestFormatter.

        Parameters
        ----------
        config : Optional[ClientConfig]
            The client configuration, used for accessing base_url and authentication strategy if needed.
        """
        # Store config if provided, needed for base_url and auth_strategy
        self._config = config

    def validate_request_params(self, method: str, endpoint: Optional[str], url: Optional[str]) -> None:
        """Validate the core parameters for making a request.

        Ensures that method, endpoint, and url have the correct types and that
        either endpoint or url is provided.

        Parameters
        ----------
        method : str
            The HTTP method (e.g., 'GET', 'POST').
        endpoint : Optional[str]
            The API endpoint path relative to the base URL.
        url : Optional[str]
            The full URL for the request.

        Raises
        ------
        TypeError
            If any parameter has an invalid type.
        ValueError
            If both endpoint and url are None.
        """
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")
        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")
        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")
        if url is None and endpoint is None:
            raise ValueError("Either 'endpoint' or 'url' must be provided.")

    def build_request_url(self, endpoint: Optional[str], url: Optional[str]) -> str:
        """Construct the final URL for the request.

        Uses the provided url directly if available. Otherwise, constructs the URL
        by combining the base_url from the config with the endpoint.

        Parameters
        ----------
        endpoint : Optional[str]
            The API endpoint path.
        url : Optional[str]
            The full URL.

        Returns
        -------
        str
            The final URL for the request.

        Raises
        ------
        CrudClientError
            If url is None and the config or base_url is missing.
        TypeError
            If endpoint or url have incorrect types (checked by validate_request_params).
        """
        if url is not None:
            return url
        # Endpoint is guaranteed non-None by validate_request_params if url is None
        if self._config is None or self._config.base_url is None:
            raise CrudClientError("Cannot build URL: RequestFormatter requires ClientConfig with base_url.")

        # Normalize base_url to avoid duplicate slashes when concatenating
        base_url = self._config.base_url.rstrip("/")

        # Ensure endpoint is treated as str after validation
        endpoint_str = endpoint if endpoint is not None else ""
        return f"{base_url}/{endpoint_str.lstrip('/')}"

    def prepare_auth_params(self, kwargs: Dict[str, Any]) -> None:
        """Inject authentication parameters into the request kwargs if applicable.

        Checks the configured AuthStrategy (if any) for a `prepare_request_params`
        method and merges the returned parameters into `kwargs['params']`.

        Parameters
        ----------
        kwargs : Dict[str, Any]
            The request keyword arguments, potentially modified in-place.

        Raises
        ------
        TypeError
            If the auth strategy returns non-dict params.
        """
        if self._config is None or self._config.auth_strategy is None:
            return  # No auth strategy configured

        auth_strategy: "AuthStrategy" = self._config.auth_strategy
        if not hasattr(auth_strategy, "prepare_request_params"):
            return  # Strategy doesn't support param preparation

        auth_params = auth_strategy.prepare_request_params()
        if not isinstance(auth_params, dict):
            raise TypeError(f"Auth strategy's prepare_request_params must return a dictionary, " f"got {type(auth_params).__name__}")

        if not auth_params:
            return

        # Ensure kwargs['params'] exists and is a dictionary for merging.
        # Handle cases where 'params' is missing, None, or not a dict.
        params = kwargs.get("params")
        if not isinstance(params, dict):
            if params is not None:
                logger.warning(f"Request 'params' has unexpected type: {type(params).__name__}. Overwriting with auth params.")
            params = {}  # Initialize as empty dict if None or not a dict
            kwargs["params"] = params

        # Merge auth params, logging potential overwrites
        for key, value in auth_params.items():
            if key in params:
                logger.debug(f"Auth param '{key}' overwrites existing request param.")
            params[key] = value
        logger.debug("Merged auth params into request params: %s", params)

    def prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Prepare request data based on the provided parameters.

        This method determines the appropriate content type based on the provided data
        and returns the prepared data along with the necessary headers.

        Parameters
        ----------
        data : Optional[Dict[str, Any]]
            Form data to include in the request.
        json : Optional[Any]
            JSON data to include in the request.
        files : Optional[Dict[str, Any]]
            Files to include in the request.

        Returns
        -------
        Tuple[Dict[str, Any], Dict[str, str]]
            A tuple containing:
            - The prepared request data as a dictionary.
            - The headers dictionary with the appropriate content-type.

        Raises
        ------
        TypeError
            If the parameters are of incorrect types.
        """
        # Runtime type checks for critical parameters
        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        if json is not None:
            return self.prepare_json(json)
        elif files is not None:
            return self.prepare_multipart(files, data)
        elif data is not None:
            return self.prepare_form_data(data)
        return {}, {}

    def prepare_json(self, json_data: Any) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Prepare JSON request data.

        Parameters
        ----------
        json_data : Any
            The JSON data to include in the request.

        Returns
        -------
        Tuple[Dict[str, Any], Dict[str, str]]
            A tuple containing:
            - A dictionary with the 'json' key set to the provided JSON data.
            - The headers dictionary with the content-type set to 'application/json'.
        """
        headers = self.get_content_type_header("application/json")
        return {"json": json_data}, headers

    def prepare_form_data(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Prepare form data request.

        Parameters
        ----------
        data : Dict[str, Any]
            The form data to include in the request.

        Returns
        -------
        Tuple[Dict[str, Any], Dict[str, str]]
            A tuple containing:
            - A dictionary with the 'data' key set to the provided form data.
            - The headers dictionary with the content-type set to 'application/x-www-form-urlencoded'.

        Raises
        ------
        TypeError
            If data is not a dictionary.
        """
        # Runtime type check
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary, got {type(data).__name__}")
        headers = self.get_content_type_header("application/x-www-form-urlencoded")
        return {"data": data}, headers

    def prepare_multipart(self, files: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Prepare multipart form data request.

        Parameters
        ----------
        files : Dict[str, Any]
            The files to include in the request.
        data : Optional[Dict[str, Any]]
            Additional form data to include in the request.

        Returns
        -------
        Tuple[Dict[str, Any], Dict[str, str]]
            A tuple containing:
            - A dictionary with 'files' and optionally 'data' keys.
            - The headers dictionary with the content-type set to 'multipart/form-data'.

        Raises
        ------
        TypeError
            If files is not a dictionary or data is not a dictionary or None.
        """
        # Runtime type checks
        if not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary, got {type(files).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")
        headers = self.get_content_type_header("multipart/form-data")
        result = {"files": files}
        if data is not None:
            result["data"] = data
        return result, headers

    def get_content_type_header(self, content_type: str) -> Dict[str, str]:
        """Get the content-type header for a given content type.

        Parameters
        ----------
        content_type : str
            The content type to set in the header.

        Returns
        -------
        Dict[str, str]
            A dictionary with the 'Content-Type' key set to the provided content type.

        Raises
        ------
        TypeError
            If content_type is not a string.
        """
        # Runtime type check
        if not isinstance(content_type, str):
            raise TypeError(f"content_type must be a string, got {type(content_type).__name__}")
        return {"Content-Type": content_type}

    def format_request(self, method: str, endpoint: Optional[str], url: Optional[str], **kwargs: Any) -> Tuple[str, Dict[str, Any]]:
        """Format the entire request, including URL, auth params, and body/headers.

        Parameters
        ----------
        method : str
            HTTP method (e.g., 'GET', 'POST').
        endpoint : Optional[str]
            API endpoint path.
        url : Optional[str]
            Full request URL.
        **kwargs
            Additional request parameters (headers, params, data, json, files).

        Returns
        -------
        Tuple[str, Dict[str, Any]]
            A tuple containing:
            - The final request URL.
            - The prepared keyword arguments for the request function,
              including merged headers, auth params, and formatted body ('data', 'json', 'files').

        Raises
        ------
        TypeError
            If input parameters have incorrect types.
        ValueError
            If both endpoint and url are None.
        CrudClientError
            If URL construction fails due to missing config.
        """
        self.validate_request_params(method, endpoint, url)
        final_url = self.build_request_url(endpoint, url)
        self.prepare_auth_params(kwargs)  # Modifies kwargs in-place

        # Prepare data/json/files payload using existing methods
        data_kwargs, headers = self.prepare_data(data=kwargs.pop("data", None), json=kwargs.pop("json", None), files=kwargs.pop("files", None))
        kwargs.update(data_kwargs)  # Add 'json', 'data', or 'files' back to kwargs

        # Merge content-type headers if any were generated
        if headers:
            existing_headers = kwargs.setdefault("headers", {})
            if not isinstance(existing_headers, dict):
                logger.warning("Overwriting non-dict 'headers' with Content-Type header.")
                existing_headers = {}
            existing_headers.update(headers)
            kwargs["headers"] = existing_headers

        return final_url, kwargs
