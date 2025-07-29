"""
Module `response_conversion.py`.

This module provides functions for converting API responses to model instances.
It handles the initialization of response strategies, validation of responses,
and conversion of response data to model instances.
"""

import json
import logging
from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Union, cast

if TYPE_CHECKING:
    from .base import Crud

from pydantic import ValidationError as PydanticValidationError

from ..exceptions import CrudClientError, DataValidationError, ResponseParsingError
from ..http.utils import redact_json_body  # Import redaction utility
from ..models import ApiResponse
from ..response_strategies import (
    DefaultResponseModelStrategy,
    ModelDumpable,
    PathBasedResponseModelStrategy,
)
from ..types import JSONDict, JSONList, RawResponse

logger = logging.getLogger(__name__)

__all__ = [
    "_init_response_strategy",
    "_validate_response",
    "_convert_to_model",
    "_convert_to_list_model",
    "_validate_list_return",
    "_fallback_list_conversion",
    "_dump_model_instance",
    "_validate_partial_dict",
    "_validate_and_dump_full_dict",
    "_dump_dictionary",
    "_dump_data",
]

# Define T type variable
T = TypeVar("T", bound="ModelDumpable")


def _init_response_strategy(self: "Crud[T]") -> None:
    """
    Initialize the response model strategy.

    This method creates an instance of the appropriate response model strategy
    based on the class configuration. It uses PathBasedResponseModelStrategy if
    _single_item_path or _list_item_path are defined, otherwise it uses
    DefaultResponseModelStrategy.
    """
    if self._response_strategy is not None:
        logger.debug(f"Using provided response strategy: {self._response_strategy.__class__.__name__}")
        return

    if hasattr(self, "_single_item_path") or hasattr(self, "_list_item_path"):
        logger.debug("Using PathBasedResponseModelStrategy")
        self._response_strategy = PathBasedResponseModelStrategy(
            datamodel=self._datamodel,
            api_response_model=self._api_response_model,
            single_item_path=getattr(self, "_single_item_path", None),
            list_item_path=getattr(self, "_list_item_path", None),
        )
    else:
        logger.debug("Using DefaultResponseModelStrategy")
        self._response_strategy = DefaultResponseModelStrategy(
            datamodel=self._datamodel,
            api_response_model=self._api_response_model,
            list_return_keys=self._list_return_keys,
        )


def _validate_response(self: "Crud[T]", data: RawResponse) -> Union[JSONDict, JSONList, str]:
    """
    Validate the API response data.

    Parameters
    ----------
    data : RawResponse
        The API response data.

    Returns
    -------
    Union[JSONDict, JSONList, str]
        The validated data.

    Raises
    ------
    ValueError
        If the response is None, invalid bytes, or not a dict or list.
    ResponseParsingError
        If the response is a string that cannot be parsed as JSON.
    """
    if data is None:
        raise ValueError("Response data is None")

    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
            return cast(Union[JSONDict, JSONList], parsed_data)
        except json.JSONDecodeError as e:
            error_msg = f"Failed to decode JSON response: {e}"
            response_snippet = data[:100] + "..." if len(data) > 100 else data
            logger.error("%s - Response snippet: %s", error_msg, response_snippet, exc_info=True)
            raise ResponseParsingError(error_msg, original_exception=e, response=None) from e

    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            error_msg = f"Unable to decode binary response data: {data[:100]!r}..."
            logger.error(error_msg)
            raise ValueError(error_msg)

    if not isinstance(data, (dict, list)):
        raise ValueError(f"Expected dict or list response, got {type(data)}")

    return data


def _convert_to_model(self: "Crud[T]", data: RawResponse) -> Union[T, JSONDict]:
    """
    Convert the API response to the datamodel type.

    This method uses the configured response model strategy to convert the data.
    The strategy handles extracting data from the response and converting it to
    the appropriate model type.

    Parameters
    ----------
    data : RawResponse
        The API response data.

    Returns
    -------
    Union[T, JSONDict]
        An instance of the datamodel or a dictionary.

    Raises
    ------
    DataValidationError
        If the response data fails Pydantic validation.
    ResponseParsingError
        If the initial response data (string) cannot be parsed as JSON.
    ValueError
        If the response data is invalid (e.g., un-decodable bytes).
    """
    try:
        validated_data = self._validate_response(data)

        if isinstance(validated_data, list):
            return cast(Union[T, JSONDict], self._convert_to_list_model(cast(JSONList, validated_data)))

        if self._response_strategy:
            return self._response_strategy.convert_single(validated_data)

        return cast(Union[T, JSONDict], validated_data)

    except PydanticValidationError as e:
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response data validation failed for model {model_name}"
        safe_data = locals().get("validated_data", data)
        redacted_data = redact_json_body(safe_data) if isinstance(safe_data, (dict, list)) else safe_data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        logger.error(f"Unexpected error converting response to model: {e}", exc_info=True)
        raise


def _convert_to_list_model(self: "Crud[T]", data: JSONList) -> Union[List[T], JSONList]:
    """
    Convert the API response to a list of datamodel types.

    Parameters
    ----------
    data : JSONList
        The API response data.

    Returns
    -------
    Union[List[T], JSONList]
        A list of instances of the datamodel or the original list.

    Raises
    ------
    DataValidationError
        If list items fail Pydantic validation.
    """
    if not self._datamodel:
        return data

    try:
        return [self._datamodel(**item) for item in data]
    except PydanticValidationError as e:
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response list item validation failed for model {model_name}"
        redacted_data = redact_json_body(data) if isinstance(data, (dict, list)) else data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        logger.error(f"Unexpected error converting list response to model: {e}", exc_info=True)
        raise


def _validate_list_return(self: "Crud[T]", data: RawResponse) -> Union[JSONList, List[T], ApiResponse]:
    """
    Validate and convert the list response data.

    This method uses the configured response model strategy to validate and convert
    the list response data. It handles different response formats and extracts list
    data according to the strategy.

    Parameters
    ----------
    data : RawResponse
        The API response data.

    Returns
    -------
    Union[JSONList, List[T], ApiResponse]
        Validated and converted list data.

    Raises
    ------
    DataValidationError
        If the response data fails Pydantic validation during conversion.
    ResponseParsingError
        If the initial response data (string) cannot be parsed as JSON.
    ValueError
        If the response data is invalid (e.g., un-decodable bytes).
    """
    try:
        validated_data = self._validate_response(data)

        if self._response_strategy:
            return self._response_strategy.convert_list(validated_data)

        return cast(Union[JSONList, List[T], ApiResponse], self._fallback_list_conversion(validated_data))

    except PydanticValidationError as e:
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response list validation failed for model {model_name}"
        safe_data = locals().get("validated_data", data)
        redacted_data = redact_json_body(safe_data) if isinstance(safe_data, (dict, list)) else safe_data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        logger.error(f"Unexpected error validating list return: {e}", exc_info=True)
        raise


def _fallback_list_conversion(self: "Crud[T]", data: RawResponse) -> Union[JSONList, List[T], ApiResponse]:
    """
    Fallback conversion logic for list responses when the strategy fails.

    This method implements the original behavior for backward compatibility.

    Parameters
    ----------
    data : RawResponse
        The validated response data.

    Returns
    -------
    Union[JSONList, List[T], ApiResponse]
        Converted list data.

    Raises
    ------
    ValueError
        If the response format is unexpected or conversion fails.
    """
    if isinstance(data, list):
        return cast(Union[JSONList, List[T], ApiResponse], self._convert_to_list_model(data))

    if isinstance(data, dict):
        if self._api_response_model:
            try:
                return self._api_response_model(**data)
            except Exception as e:
                logger.warning(f"Failed to convert to API response model: {e}", exc_info=True)

        for key in self._list_return_keys:
            if key in data and isinstance(data[key], list):
                return cast(Union[JSONList, List[T], ApiResponse], self._convert_to_list_model(cast(JSONList, data[key])))

    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list):
                return cast(Union[JSONList, List[T], ApiResponse], self._convert_to_list_model(cast(JSONList, parsed_data)))
            elif isinstance(parsed_data, dict):
                for key in self._list_return_keys:
                    if key in parsed_data and isinstance(parsed_data[key], list):
                        return cast(Union[JSONList, List[T], ApiResponse], self._convert_to_list_model(cast(JSONList, parsed_data[key])))
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse string response as JSON in fallback: {e}", exc_info=True)

    logger.warning(f"Could not extract list data from response using fallback, returning empty list. Response snippet: {str(data)[:200]}")
    return []


def _dump_model_instance(self: "Crud[T]", model_instance: T, partial: bool) -> JSONDict:
    """
    Dump a Pydantic model instance to a dictionary.

    Handles both Pydantic v1 (dict()) and v2 (model_dump()).
    Falls back to __dict__ if necessary.

    Parameters
    ----------
    model_instance : T
        The model instance to dump.
    partial : bool
        Whether to exclude unset fields (for partial updates).

    Returns
    -------
    JSONDict
        The dumped dictionary representation of the model.

    Raises
    ------
    TypeError
        If the instance cannot be dumped.
    """
    if hasattr(model_instance, "model_dump") and callable(getattr(model_instance, "model_dump")):
        return cast(JSONDict, getattr(model_instance, "model_dump")(exclude_unset=partial))
    elif hasattr(model_instance, "dict") and callable(getattr(model_instance, "dict")):
        logger.warning(f"Using deprecated dict() for dumping model {type(model_instance)}.")
        return cast(JSONDict, getattr(model_instance, "dict")(exclude_unset=partial))
    elif hasattr(model_instance, "__dict__"):
        logger.warning(f"Using __dict__ for dumping model instance {type(model_instance)}.")
        return model_instance.__dict__
    else:
        raise TypeError(f"Cannot dump model instance of type {type(model_instance)}")


def _validate_partial_dict(self: "Crud[T]", data_dict: JSONDict, validation_model: Optional[Type[ModelDumpable]] = None) -> None:
    """
    Validate provided fields in a dictionary against the specified validation model for partial updates.

    Ignores 'missing' errors.

    Parameters
    ----------
    data_dict : JSONDict
        The dictionary containing partial data.
    validation_model : Optional[Type[ModelDumpable]], optional
        The model to validate against. If None, falls back to self._datamodel.

    Raises
    ------
    DataValidationError
        If validation fails for non-missing fields.
    """
    model = validation_model or self._datamodel

    if not model:
        return

    try:
        getattr(model, "model_validate")(data_dict)
    except PydanticValidationError as e:
        non_missing_errors = [err for err in e.errors() if err.get("type") != "missing"]
        if non_missing_errors:
            model_name = getattr(model, "__name__", "Unknown")
            error_msg = f"Partial update data validation failed for provided fields in model {model_name}"
            redacted_data = redact_json_body(data_dict) if isinstance(data_dict, (dict, list)) else data_dict
            logger.warning(
                "%s: %s",
                error_msg,
                json.dumps(non_missing_errors, indent=2),
            )
            raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e


def _validate_and_dump_full_dict(self: "Crud[T]", data_dict: JSONDict, validation_model: Optional[Type[ModelDumpable]] = None) -> JSONDict:
    """
    Validate a dictionary against the specified validation model and dump the result.

    Parameters
    ----------
    data_dict : JSONDict
        The dictionary to validate and dump.
    validation_model : Optional[Type[ModelDumpable]], optional
        The model to validate against. If None, falls back to self._datamodel.

    Returns
    -------
    JSONDict
        The dumped dictionary after validation.

    Raises
    ------
    DataValidationError
        If validation fails.
    """
    model = validation_model or self._datamodel

    if not model:
        return data_dict

    try:
        validated_model = getattr(model, "model_validate")(data_dict)
        return self._dump_model_instance(validated_model, partial=False)  # type: ignore[no-any-return]
    except PydanticValidationError as e:
        model_name = getattr(model, "__name__", "Unknown")
        error_msg = f"Input data validation failed for model {model_name}"
        redacted_data = redact_json_body(data_dict) if isinstance(data_dict, (dict, list)) else data_dict
        logger.warning(
            "%s: %s",
            error_msg,
            json.dumps(e.errors(), indent=2),
        )
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e


def _dump_dictionary(self: "Crud[T]", data_dict: JSONDict, partial: bool, validation_model: Optional[Type[ModelDumpable]] = None) -> JSONDict:
    """
    Validate and dump a dictionary based on the specified validation model.

    For partial updates, validates only provided fields.
    For full updates, validates against the full model and dumps the result.

    Parameters
    ----------
    data_dict : JSONDict
        The dictionary to dump.
    partial : bool
        Whether this is a partial update.
    validation_model : Optional[Type[ModelDumpable]], optional
        The model to validate against. If None, falls back to self._datamodel.

    Returns
    -------
    JSONDict
        The validated and/or dumped dictionary.

    Raises
    ------
    DataValidationError
        If validation fails.
    """
    if partial:
        self._validate_partial_dict(data_dict, validation_model)
        return data_dict
    else:
        return self._validate_and_dump_full_dict(data_dict, validation_model)  # type: ignore[no-any-return]


def _dump_data(
    self: "Crud[T]", data: Optional[Union[JSONDict, T]], validation_model: Optional[Type[ModelDumpable]] = None, partial: bool = False
) -> JSONDict:
    """
    Dump the data model to a JSON-serializable dictionary.

    Parameters
    ----------
    data : Optional[Union[JSONDict, T]]
        The data to dump.
    validation_model : Optional[Type[ModelDumpable]], optional
        Optional model to use for validation. If None, determines model based on operation type.
    partial : bool, optional
        Whether this is a partial update. Defaults to False.

    Returns
    -------
    JSONDict
        The dumped data.

    Raises
    ------
    DataValidationError
        If the data fails validation.
    TypeError
        If the input data is not a dict or model instance.
    """
    if data is None:
        return cast(JSONDict, {})

    if validation_model is None:
        if partial is False and hasattr(self, "_create_model") and self._create_model is not None:
            validation_model = self._create_model
        elif partial is True and hasattr(self, "_update_model") and self._update_model is not None:
            validation_model = self._update_model
        else:
            validation_model = self._datamodel

    try:
        if isinstance(data, dict):
            data_dict: JSONDict = data
            return cast(JSONDict, self._dump_dictionary(data_dict, partial, validation_model))
        else:
            # If not a dict, it must be a model instance of type T
            return cast(JSONDict, self._dump_model_instance(data, partial))

    except DataValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error dumping data: {e}", exc_info=True)
        raise CrudClientError(f"Unexpected error during data dumping: {e}") from e
