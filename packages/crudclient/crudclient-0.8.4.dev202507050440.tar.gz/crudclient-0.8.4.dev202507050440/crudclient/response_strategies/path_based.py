"""
Module `response_strategies.path_based`
=====================================

This module defines the path-based response model strategy for handling API responses.

Classes:
    - PathBasedResponseModelStrategy: Strategy for extracting data using path expressions.
"""

import logging
from typing import Any, List, Optional, Type, Union

from pydantic import ValidationError as PydanticValidationError

from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse
from .base import ResponseModelStrategy, T
from .types import ApiResponseType, ResponseTransformer

# Get a logger for this module
logger = logging.getLogger(__name__)


class PathBasedResponseModelStrategy(ResponseModelStrategy[T]):
    """
    A response model strategy that extracts data using path expressions.

    This strategy allows for extracting data from nested structures using dot notation
    path expressions (e.g., "data.items" to access data["data"]["items"]).
    """

    datamodel: Optional[Type[T]]
    api_response_model: Optional[ApiResponseType]
    single_item_path: Optional[str]
    list_item_path: Optional[str]
    pre_transform: Optional[ResponseTransformer]

    def __init__(
        self,
        datamodel: Optional[Type[T]] = None,
        api_response_model: Optional[ApiResponseType] = None,
        single_item_path: Optional[str] = None,
        list_item_path: Optional[str] = None,
        pre_transform: Optional[ResponseTransformer] = None,
    ):
        self.datamodel = datamodel
        self.api_response_model = api_response_model
        self.single_item_path = single_item_path
        self.list_item_path = list_item_path
        self.pre_transform = pre_transform

    def _extract_by_path(self, data: Any, path: Optional[str]) -> Any:
        if not path:
            return data

        current: Any = data
        for part in path.split("."):
            if isinstance(current, list):
                try:
                    index = int(part)
                except ValueError:
                    raise ValueError(f"Expected integer index in path '{path}', got '{part}'")
                try:
                    current = current[index]
                except IndexError:
                    raise ValueError(f"Index {index} out of range in path '{path}'")
            elif isinstance(current, dict):
                if part not in current:
                    raise ValueError(f"Could not find '{part}' in path '{path}' in response data")
                current = current[part]
            else:
                raise ValueError(f"Unable to traverse into '{part}' from type {type(current)} while processing path '{path}'")

        return current

    def _prepare_single_data(self, data: RawResponse) -> Union[JSONDict, JSONList]:
        """Handles initial data type checks and parsing for single item conversion."""
        if data is None:
            raise ValueError("Response data is None")

        # Handle string data
        if isinstance(data, str):
            str_data = data
            try:
                import json

                parsed_data: Any = json.loads(str_data)
                if not isinstance(parsed_data, (dict, list)):
                    raise ValueError(f"Parsed JSON is not a dictionary or list, got {type(parsed_data)}")
                return parsed_data
            except json.JSONDecodeError:
                raise ValueError(f"Could not parse string as JSON: {str_data[:100]}...")
        # Handle bytes data
        elif isinstance(data, bytes):
            try:
                decoded = data.decode("utf-8")
                # Recursive call
                return self._prepare_single_data(decoded)
            except UnicodeDecodeError:
                raise ValueError("Could not decode binary data as UTF-8")
        # Handle dict/list data
        elif isinstance(data, (dict, list)):
            return data
        else:
            raise ValueError(f"Unexpected initial data type: {type(data)}")

    # Refactored convert_single
    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]:
        processed_data = self._prepare_single_data(data)

        # Apply pre-transform if provided
        if self.pre_transform:
            # Assuming pre_transform handles dict/list and returns dict/list
            processed_data = self.pre_transform(processed_data)

        # Extract data using path if provided
        extracted_data: Any = processed_data
        if self.single_item_path:
            try:
                # _extract_by_path expects dict/list, processed_data should be that now
                if not isinstance(processed_data, (dict, list)):
                    raise ValueError(f"Data is not a dictionary or list before path extraction: {type(processed_data)}")
                extracted_data = self._extract_by_path(processed_data, self.single_item_path)
            except ValueError as e:
                raise ValueError(f"Failed to extract single item data: {e}")

        # Validate final data is a dictionary
        if not isinstance(extracted_data, dict):
            path_info = f" (path: {self.single_item_path})" if self.single_item_path else ""
            raise ValueError(f"Expected dictionary data{path_info}, got {type(extracted_data)}")

        # Apply datamodel
        final_data: JSONDict = extracted_data
        if self.datamodel:
            try:
                return self.datamodel(**final_data)
            except PydanticValidationError as e:
                model_name = self.datamodel.__name__ if self.datamodel else "Unknown"
                path_info = f" (path: {self.single_item_path})" if self.single_item_path else ""
                error_msg = f"Response data validation failed for model {model_name}{path_info}"
                logger.error(f"{error_msg}: errors={e.errors()}")
                raise
        else:
            # Return the dictionary if no datamodel
            return final_data

    def _prepare_data_for_conversion(self, data: RawResponse) -> Union[JSONDict, JSONList]:
        """Handles initial data type checks and parsing (None, str, bytes)."""
        if data is None:
            raise ValueError("Response data is None")

        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                if isinstance(parsed_data, (dict, list)):
                    return parsed_data
                else:
                    # Handle cases where JSON is valid but not dict/list (e.g., "null", "true", 123)
                    raise ValueError(f"Parsed JSON is not a dictionary or list, got {type(parsed_data)}")
            except json.JSONDecodeError:
                # Ensure data is str before using it in the error message for mypy
                assert isinstance(data, str)
                raise ValueError(f"Could not parse string as JSON: {data[:100]}...")

        if isinstance(data, bytes):
            try:
                decoded = data.decode("utf-8")
                # Recursively call to handle the decoded string (which might be JSON)
                return self._prepare_data_for_conversion(decoded)
            except UnicodeDecodeError:
                raise ValueError("Could not decode binary data as UTF-8")

        # If it's already a dict or list, return as is for further processing
        if isinstance(data, (dict, list)):
            return data

        # If it's none of the above, raise an error
        raise ValueError(f"Unsupported data type for conversion: {type(data)}")

    def _apply_api_response_model(self, data: JSONDict) -> Optional[ApiResponse[Any]]:
        """Applies the api_response_model if configured and data is a dict."""
        if self.api_response_model:
            try:
                return self.api_response_model(**data)
            except PydanticValidationError as e:
                model_name = self.api_response_model.__name__ if self.api_response_model else "Unknown"
                error_msg = f"Response data validation failed for API response model {model_name}"
                logger.error(f"{error_msg}: errors={e.errors()}")
                raise
        return None

    def _extract_and_validate_list(self, data: Union[JSONDict, JSONList]) -> JSONList:
        """Extracts list data using list_item_path and validates it's a list."""
        list_data = data
        if self.list_item_path:
            try:
                # Ensure data is dict before path extraction if path is present
                if not isinstance(data, dict):
                    raise ValueError(f"Expected dictionary data for path extraction, got {type(data)}")
                list_data = self._extract_by_path(data, self.list_item_path)
            except ValueError as e:
                raise ValueError(f"Failed to extract list data using path '{self.list_item_path}': {e}")

        if not isinstance(list_data, list):
            path_info = f" (path: {self.list_item_path})" if self.list_item_path else ""
            raise ValueError(f"Expected list data{path_info}, got {type(list_data)}")

        return list_data

    def _convert_items_to_datamodel(self, list_data: JSONList) -> List[T]:
        """Converts items in the list to the specified datamodel."""
        if not self.datamodel:
            # Should not happen if called correctly, but safeguard
            raise TypeError("Datamodel is not set, cannot convert list items.")
        try:
            return [self.datamodel(**item) for item in list_data]
        except PydanticValidationError as e:
            model_name = self.datamodel.__name__ if self.datamodel else "Unknown"
            path_info = f" (path: {self.list_item_path})" if self.list_item_path else ""
            error_msg = f"Response list item validation failed for model {model_name}{path_info}"
            logger.error(f"{error_msg}: errors={e.errors()}")
            raise

    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]:
        prepared_data = self._prepare_data_for_conversion(data)

        # Apply pre-transform if provided
        if self.pre_transform:
            prepared_data = self.pre_transform(prepared_data)

        # Handle API response model if applicable (must be dict)
        if isinstance(prepared_data, dict):
            api_response = self._apply_api_response_model(prepared_data)
            if api_response:
                return api_response  # Return early if API model processed it

        # Extract the list data (potentially using path)
        list_data = self._extract_and_validate_list(prepared_data)

        # Convert items if datamodel is specified, otherwise return raw list
        if self.datamodel:
            return self._convert_items_to_datamodel(list_data)
        else:
            return list_data
