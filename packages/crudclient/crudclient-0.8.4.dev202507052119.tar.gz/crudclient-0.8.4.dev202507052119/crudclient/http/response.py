"""
Handles HTTP response processing and validation.

This module provides functionality for processing HTTP responses based on their content type
and validating response status. It supports JSON, binary, and text responses.
"""

import logging
from typing import Any, Dict, List, Union, cast

import requests
from requests.exceptions import JSONDecodeError

from ..exceptions import ResponseParsingError
from ..types import RawResponseSimple

logger = logging.getLogger(__name__)


class ResponseHandler:
    """Handles HTTP response processing and validation.

    This class is responsible for processing HTTP responses based on their content type
    and validating response status. It supports JSON, binary, and text responses.

    Methods
    -------
    handle_response
        Processes an HTTP response and returns the parsed data.
    parse_json_response
        Parses a JSON response.
    parse_binary_response
        Parses a binary response.
    parse_text_response
        Parses a text response.
    """

    def handle_response(self, response: requests.Response) -> RawResponseSimple:
        """Process an HTTP response and return the parsed data.

        This method checks if the response is successful and then parses the response
        based on its content type. It delegates to specific parsing methods based on
        the content type.

        Parameters
        ----------
        response : requests.Response
            The HTTP response to process.

        Returns
        -------
        RawResponseSimple
            The parsed response data, which could be a JSON dictionary,
            binary content, or text.

        Raises
        ------
        requests.HTTPError
            If the response status code indicates an error.
        TypeError
            If response is not a requests.Response object.

        Note
        ----
        This method does not handle error responses. It assumes that error handling
        is done by the caller before this method is called.
        """
        self._validate_response_object(response)

        if not response.ok:
            logger.debug(f"Response not OK: {response.status_code}")
            response.raise_for_status()

        if response.status_code == 204:
            logger.debug("Received 204 No Content response, returning None")
            return None

        content_type = response.headers.get("Content-Type", "")
        logger.debug(f"Processing response with content type: {content_type}")

        if content_type.startswith("application/json"):
            return self.parse_json_response(response)
        elif content_type.startswith("application/octet-stream") or content_type.startswith("multipart/form-data"):
            return self.parse_binary_response(response)
        else:
            return self.parse_text_response(response)

    def parse_json_response(self, response: requests.Response) -> Union[Dict[str, Any], List[Any], str]:
        """Parse a JSON response.

        Parameters
        ----------
        response : requests.Response
            The HTTP response with JSON content.

        Returns
        -------
        Union[Dict[str, Any], List[Any], str]
            The parsed JSON data.

        Raises
        ------
        TypeError
            If response is not a requests.Response object.
        ResponseParsingError
            If the response cannot be parsed as JSON.
        """
        self._validate_response_object(response)

        logger.debug("Parsing JSON response")
        try:
            # Parse the JSON response
            result = response.json()

            # Return the result with appropriate type
            if isinstance(result, dict):
                return cast(Dict[str, Any], result)
            elif isinstance(result, list):
                return result  # No need for cast, mypy can infer this
            else:
                return cast(str, result)
        except JSONDecodeError as e:
            logger.error(
                "Failed to parse JSON response despite 'application/json' Content-Type. " "Status: %s, URL: %s, Error: %s",
                response.status_code,
                response.url,
                e,
                exc_info=True,
            )
            raise ResponseParsingError(
                message=f"Failed to decode JSON response from {response.url}",
                original_exception=e,
                response=response,
            ) from e

    def parse_binary_response(self, response: requests.Response) -> bytes:
        """Parse a binary response.

        Parameters
        ----------
        response : requests.Response
            The HTTP response with binary content.

        Returns
        -------
        bytes
            The binary content of the response.

        Raises
        ------
        TypeError
            If response is not a requests.Response object.
        """
        self._validate_response_object(response)

        logger.debug("Parsing binary response")
        return response.content

    def parse_text_response(self, response: requests.Response) -> str:
        """Parse a text response.

        Parameters
        ----------
        response : requests.Response
            The HTTP response with text content.

        Returns
        -------
        str
            The text content of the response.

        Raises
        ------
        TypeError
            If response is not a requests.Response object.
        """
        self._validate_response_object(response)

        logger.debug("Parsing text response")
        return response.text

    def _validate_response_object(self, response: Any) -> None:
        """Validate that the response is a valid Response object or a mock.

        Parameters
        ----------
        response
            The response object to validate.

        Raises
        ------
        TypeError
            If response is not a valid Response object or mock.
        """
        is_response = isinstance(response, requests.Response)
        is_mock = hasattr(response, "_mock_spec") and requests.Response in getattr(response, "_mock_spec", [])

        if not is_response and not is_mock:
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
