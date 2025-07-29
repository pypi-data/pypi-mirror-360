"""
Module `response_strategies.default`
==================================

This module defines the default response model strategy for handling API responses.

Classes:
    - DefaultResponseModelStrategy: Default implementation for backward compatibility.
"""

import logging
from typing import Any, List, Optional, Type, Union

from pydantic import ValidationError as PydanticValidationError

from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse
from .base import ResponseModelStrategy, T
from .types import ApiResponseType

# Get a logger for this module
logger = logging.getLogger(__name__)


class DefaultResponseModelStrategy(ResponseModelStrategy[T]):
    """
    Default implementation of the response model strategy.

    This strategy implements the original behavior of the Crud class for backward compatibility.
    """

    datamodel: Optional[Type[T]]
    api_response_model: Optional[ApiResponseType]
    list_return_keys: List[str]

    def __init__(
        self,
        datamodel: Optional[Type[T]] = None,
        api_response_model: Optional[ApiResponseType] = None,
        list_return_keys: List[str] = ["data", "results", "items"],
    ) -> None:
        self.datamodel = datamodel
        self.api_response_model = api_response_model
        self.list_return_keys = list_return_keys

    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]:
        if data is None:
            raise ValueError("Response data is None")

        # Handle string data by trying to parse it as JSON
        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                if isinstance(parsed_data, dict):
                    return self.datamodel(**parsed_data) if self.datamodel else parsed_data
                else:
                    raise ValueError(f"Expected dictionary after JSON parsing, got {type(parsed_data)}")
            except json.JSONDecodeError:
                # If it's not valid JSON, we can't convert it to a model
                raise ValueError(f"Could not parse string as JSON: {data[:100]}...")

        if isinstance(data, bytes):
            try:
                # Try to decode and parse as JSON
                decoded = data.decode("utf-8")
                return self.convert_single(decoded)
            except UnicodeDecodeError:
                raise ValueError("Could not decode binary data as UTF-8")

        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary response, got {type(data)}")

        if self.datamodel:
            try:
                return self.datamodel(**data)
            except PydanticValidationError as e:
                model_name = self.datamodel.__name__ if self.datamodel else "Unknown"
                error_msg = f"Response data validation failed for model {model_name}"
                logger.error(f"{error_msg}: errors={e.errors()}")
                raise  # Re-raise the original validation error
        else:
            return data

    def _prepare_data_for_conversion(self, data: RawResponse) -> Union[JSONDict, JSONList]:
        """Handles initial data type checks and parsing (None, str, bytes)."""
        # Implementation moved from docstring
        if data is None:
            raise ValueError("Response data is None")

        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                # Recursively call to handle the parsed data (could be dict or list)
                # Ensure the recursive call returns a dict or list, otherwise raise
                result = self._prepare_data_for_conversion(parsed_data)
                if isinstance(result, (dict, list)):
                    return result
                else:
                    # This case might occur if JSON parses to a non-dict/list type
                    raise ValueError(f"Parsed JSON data is not a dictionary or list: {type(result)}")
            except json.JSONDecodeError:
                raise ValueError(f"Could not parse string as JSON: {data[:100]}...")

        if isinstance(data, bytes):
            try:
                decoded = data.decode("utf-8")
                # Recursively call to handle the decoded string
                return self._prepare_data_for_conversion(decoded)
            except UnicodeDecodeError:
                raise ValueError("Could not decode binary data as UTF-8")

        if isinstance(data, (dict, list)):
            return data

        raise ValueError(f"Unsupported data type for conversion: {type(data)}")

    def _convert_items_to_datamodel(self, list_data: JSONList) -> Union[List[T], JSONList]:
        """Converts items in the list to the specified datamodel, or returns raw list."""
        # Implementation moved from docstring
        if not self.datamodel:
            # Return raw list if no datamodel specified
            return list_data
        try:
            return [self.datamodel(**item) for item in list_data]
        except PydanticValidationError as e:
            model_name = self.datamodel.__name__ if self.datamodel else "Unknown"
            error_msg = f"Response list item validation failed for model {model_name}"
            logger.error(f"{error_msg}: errors={e.errors()}")
            raise

    def _handle_dict_response(self, data: JSONDict) -> Union[List[T], JSONList, ApiResponse[Any]]:
        """Handles the case where the prepared data is a dictionary."""
        # Implementation moved from docstring
        # Check for custom API response model first
        if self.api_response_model:
            # For API response models, we need to convert the list items first
            modified_data = data.copy()

            # Look for list data in known keys and convert items
            for key in self.list_return_keys:
                if key in modified_data and isinstance(modified_data[key], list):
                    # Convert the items to datamodel if available
                    if self.datamodel:
                        modified_data[key] = self._convert_items_to_datamodel(modified_data[key])
                    break

            try:
                return self.api_response_model(**modified_data)
            except PydanticValidationError as e:
                model_name = self.api_response_model.__name__ if self.api_response_model else "Unknown"
                error_msg = f"Response data validation failed for API response model {model_name}"
                logger.error(f"{error_msg}: errors={e.errors()}")
                raise

        # Look for list data in known keys
        for key in self.list_return_keys:
            if key in data:
                list_data = data[key]
                if not isinstance(list_data, list):
                    raise ValueError(f"Expected list data under key '{key}', got {type(list_data)}")
                return self._convert_items_to_datamodel(list_data)

        raise ValueError(f"Could not find list data using keys {self.list_return_keys} in response: {list(data.keys())}")

    def _handle_list_response(self, data: JSONList) -> Union[List[T], JSONList]:
        """Handles the case where the prepared data is a list."""
        # Implementation moved from docstring
        return self._convert_items_to_datamodel(data)

    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]:
        prepared_data = self._prepare_data_for_conversion(data)

        if isinstance(prepared_data, dict):
            return self._handle_dict_response(prepared_data)
        elif isinstance(prepared_data, list):
            return self._handle_list_response(prepared_data)
        else:
            # This path should theoretically not be reached due to _prepare_data_for_conversion
            # raising errors for unsupported types earlier.
            # Raise explicitly for robustness and to satisfy linters like Pylance.
            # Mypy knows it's unreachable, hence the ignore.
            logger.error(f"Internal error: Unexpected data format after preparation: {type(prepared_data)}")  # type: ignore[unreachable]
            raise ValueError(f"Unexpected data format after preparation: {type(prepared_data)}")
