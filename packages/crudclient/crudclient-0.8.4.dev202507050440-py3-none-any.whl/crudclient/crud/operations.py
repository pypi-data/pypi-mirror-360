"""
Module `operations.py`.

This module defines the CRUD operations for API resources.
It provides implementations for list, create, read, update, partial_update, destroy,
and custom_action operations.
"""

import json
import logging
from typing import TYPE_CHECKING, Any, Dict
from typing import List as TypingList  # Rename List to avoid conflict
from typing import Optional, Union

from pydantic import ValidationError as PydanticValidationError

if TYPE_CHECKING:
    from .base import Crud
    from crudclient.models import ListResponseWrapper

from ..exceptions import DataValidationError
from ..http.utils import redact_json_body
from ..types import JSONDict, JSONList
from .base import T

logger = logging.getLogger(__name__)

__all__ = [
    "list_operation",
    "create_operation",
    "read_operation",
    "update_operation",
    "partial_update_operation",
    "destroy_operation",
    "custom_action_operation",
    "_prepare_request_body_kwargs",
    "list",
    "create",
    "read",
    "update",
    "partial_update",
    "destroy",
    "custom_action",
]


def list_operation(
    self: "Crud[T]", parent_id: Optional[str] = None, params: Optional[JSONDict] = None
) -> Union[JSONList, TypingList[T], "ListResponseWrapper[T]"]:
    """Retrieve a list of resources.

    The returned value depends on the configured response strategy. When an
    ``_api_response_model`` is set (or the active strategy produces one), the
    method returns an :class:`ListResponseWrapper[T]` instance containing the list in its
    ``data``/``values`` attribute along with any metadata. Callers expecting only
    the raw list should access ``.data`` on the returned object instead of
    overriding this method.

    Parameters
    ----------
    parent_id : Optional[str], optional
        Optional ID of the parent resource for nested resources.
    params : Optional[JSONDict], optional
        Optional query parameters.

    Returns
    -------
    Union[JSONList, List[T], ListResponseWrapper[T]]
        Validated list data or the full ``ListResponseWrapper[T]`` wrapper.

    Raises
    ------
    ValueError
        If list action is not allowed for this resource.
    NotFoundError
        If the parent resource (if applicable) is not found.
    NetworkError
        If a network-related error occurs during the request.
    APIError
        For other API-related errors (e.g., 4xx/5xx responses).
    """
    if "list" not in self.allowed_actions:
        raise ValueError(f"List action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(parent_args=(parent_id,) if parent_id else None)
    response = self.client.get(endpoint, params=params)
    return self._validate_list_return(response)  # type: ignore[no-any-return]


def create_operation(
    self: "Crud[T]", data: Union[JSONDict, T], parent_id: Optional[str] = None, params: Optional[JSONDict] = None
) -> Union[T, JSONDict]:
    """
    Create a new resource.

    Parameters
    ----------
    data : Union[JSONDict, T]
        The data for the new resource.
    parent_id : Optional[str], optional
        Optional ID of the parent resource for nested resources.
    params : Optional[JSONDict], optional
        Optional query parameters.

    Returns
    -------
    Union[T, JSONDict]
        The created resource.

    Raises
    ------
    ValueError
        If create action is not allowed for this resource.
    DataValidationError
        If the input data fails validation.
    NotFoundError
        If the parent resource (if applicable) is not found.
    NetworkError
        If a network-related error occurs during the request.
    APIError
        For other API-related errors (e.g., 4xx/5xx responses).
    """
    if "create" not in self.allowed_actions:
        raise ValueError(f"Create action not allowed for {self.__class__.__name__}")

    try:
        model_for_create = getattr(self, "_create_model", None) or self._datamodel

        converted_data = self._dump_data(data, validation_model=model_for_create)

        endpoint = self._get_endpoint(parent_args=(parent_id,) if parent_id else None)
        response = self.client.post(endpoint, json=converted_data, params=params)

        return self._convert_to_model(response)  # type: ignore[no-any-return]

    except PydanticValidationError as e:
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        logger.error(
            "Request data validation failed during 'create' for resource '%s'. Errors: %s",
            getattr(model_for_create, "__name__", "Unknown") if model_for_create else "Unknown",
            json.dumps(e.errors()),
        )
        raise DataValidationError(
            f"Request data validation failed for {getattr(model_for_create, '__name__', 'Unknown') if model_for_create else 'Unknown'}",
            data=redacted_data,
            pydantic_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in create operation: {e}", exc_info=True)
        raise


def read_operation(self: "Crud[T]", resource_id: str, parent_id: Optional[str] = None) -> Union[T, JSONDict]:
    """
    Retrieve a specific resource.

    Parameters
    ----------
    resource_id : str
        The ID of the resource to retrieve.
    parent_id : Optional[str], optional
        Optional ID of the parent resource for nested resources.

    Returns
    -------
    Union[T, JSONDict]
        The retrieved resource.

    Raises
    ------
    ValueError
        If read action is not allowed for this resource.
    NotFoundError
        If the resource or parent resource (if applicable) is not found.
    NetworkError
        If a network-related error occurs during the request.
    APIError
        For other API-related errors (e.g., 4xx/5xx responses).
    """
    if "read" not in self.allowed_actions:
        raise ValueError(f"Read action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
    response = self.client.get(endpoint)
    return self._convert_to_model(response)  # type: ignore[no-any-return]


def update_operation(
    self: "Crud[T]",
    resource_id: Optional[str] = None,
    data: Optional[Union[JSONDict, T]] = None,
    parent_id: Optional[str] = None,
    update_mode: Optional[str] = None,
    params: Optional[JSONDict] = None,
) -> Union[T, JSONDict]:
    """
    Update a resource.

    Parameters
    ----------
    resource_id : Optional[str], optional
        The ID of the resource to update. Can be None for non-standard APIs.
    data : Optional[Union[JSONDict, T]], optional
        The data to update the resource with.
    parent_id : Optional[str], optional
        Optional parent ID if this is a nested resource.
    update_mode : Optional[str], optional
        The update mode to use. If None, uses the class's _update_mode.
        Supported modes:
        - "standard": Standard RESTful update (default)
        - "no_resource_id": Update without resource ID in URL (e.g., Tripletex company)
    params : Optional[JSONDict], optional
        Optional query parameters.

    Returns
    -------
    Union[T, JSONDict]
        The updated resource.

    Raises
    ------
    ValueError
        If update action is not allowed for this resource.
    DataValidationError
        If the input data fails validation.
    NotFoundError
        If the resource or parent resource (if applicable) is not found.
    NetworkError
        If a network-related error occurs during the request.
    APIError
        For other API-related errors (e.g., 4xx/5xx responses).
    """
    if "update" not in self.allowed_actions:
        raise ValueError(f"Update action not allowed for {self.__class__.__name__}")

    effective_mode = update_mode or getattr(self, "_update_mode", "standard")

    try:
        model_for_update = getattr(self, "_update_model", None) or self._datamodel

        converted_data = self._dump_data(data, validation_model=model_for_update)

        if effective_mode == "no_resource_id":
            endpoint = self._get_endpoint(parent_args=(parent_id,) if parent_id else None)
            if isinstance(data, dict):
                json_data = data
            else:
                json_data = converted_data
            response = self.client.put(endpoint, json=json_data, params=params)
        else:
            if resource_id is None:
                raise ValueError("resource_id is required for standard update mode")
            endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
            response = self.client.put(endpoint, json=converted_data, params=params)

        return self._convert_to_model(response)  # type: ignore[no-any-return]

    except PydanticValidationError as e:
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        logger.error(
            "Request data validation failed during 'update' for resource '%s'. Errors: %s",
            getattr(model_for_update, "__name__", "Unknown") if model_for_update else "Unknown",
            json.dumps(e.errors()),
        )
        raise DataValidationError(
            f"Request data validation failed for {getattr(model_for_update, '__name__', 'Unknown') if model_for_update else 'Unknown'}",
            data=redacted_data,
            pydantic_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in update operation: {e}", exc_info=True)
        raise


def partial_update_operation(
    self: "Crud[T]", resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None, params: Optional[JSONDict] = None
) -> Union[T, JSONDict]:
    """
    Partially update a specific resource.

    Parameters
    ----------
    resource_id : str
        The ID of the resource to update.
    data : Union[JSONDict, T]
        The partial updated data for the resource.
    parent_id : Optional[str], optional
        Optional ID of the parent resource for nested resources.
    params : Optional[JSONDict], optional
        Optional query parameters.

    Returns
    -------
    Union[T, JSONDict]
        The updated resource.

    Raises
    ------
    ValueError
        If partial_update action is not allowed for this resource.
    DataValidationError
        If the input data fails validation.
    NotFoundError
        If the resource or parent resource (if applicable) is not found.
    NetworkError
        If a network-related error occurs during the request.
    APIError
        For other API-related errors (e.g., 4xx/5xx responses).
    """
    if "partial_update" not in self.allowed_actions:
        raise ValueError(f"Partial update action not allowed for {self.__class__.__name__}")

    try:
        model_for_partial_update = getattr(self, "_update_model", None) or self._datamodel

        converted_data = self._dump_data(data, validation_model=model_for_partial_update, partial=True)

        endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
        response = self.client.patch(endpoint, json=converted_data, params=params)

        return self._convert_to_model(response)  # type: ignore[no-any-return]

    except PydanticValidationError as e:
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        logger.error(
            "Request data validation failed during 'partial_update' for resource '%s'. Errors: %s",
            getattr(model_for_partial_update, "__name__", "Unknown") if model_for_partial_update else "Unknown",
            json.dumps(e.errors()),
        )
        raise DataValidationError(
            f"Partial update request data validation failed for {getattr(model_for_partial_update, '__name__', 'Unknown') if model_for_partial_update else 'Unknown'}",
            data=redacted_data,
            pydantic_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in partial update operation: {e}", exc_info=True)
        raise


def destroy_operation(self: "Crud[T]", resource_id: str, parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> None:
    """
    Delete a specific resource.

    Parameters
    ----------
    resource_id : str
        The ID of the resource to delete.
    parent_id : Optional[str], optional
        Optional ID of the parent resource for nested resources.
    params : Optional[JSONDict], optional
        Optional query parameters.

    Raises
    ------
    ValueError
        If destroy action is not allowed for this resource.
    NotFoundError
        If the resource or parent resource (if applicable) is not found.
    NetworkError
        If a network-related error occurs during the request.
    APIError
        For other API-related errors (e.g., 4xx/5xx responses).
    """
    if "destroy" not in self.allowed_actions:
        raise ValueError(f"Destroy action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
    self.client.delete(endpoint, params=params)


def _prepare_request_body_kwargs(
    self: "Crud[T]",
    data: Optional[Union[JSONDict, T]],
    files: Optional[JSONDict],
    content_type: Optional[str],
) -> Dict[str, Any]:
    """
    Prepare request body keyword arguments based on content type and data.

    Parameters
    ----------
    data : Optional[Union[JSONDict, T]]
        Optional data to send with the request.
    files : Optional[JSONDict]
        Optional dictionary of files to upload (for multipart/form-data requests).
    content_type : Optional[str]
        Optional content type for the request.

    Returns
    -------
    Dict[str, Any]
        Dictionary of keyword arguments for the request body.

    Raises
    ------
    TypeError
        If the data type is incompatible with the content type.
    ValueError
        If an unsupported content type is provided.
    """
    request_body_kwargs = {}

    if files is not None:
        request_body_kwargs["files"] = files

        if data is not None:
            if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
                request_body_kwargs["data"] = getattr(data, "model_dump")()
            elif isinstance(data, dict):
                request_body_kwargs["data"] = data
            else:
                raise TypeError("For multipart/form-data with files, 'data' must be a dict or a Pydantic model")

    elif content_type == "application/x-www-form-urlencoded":
        if data is not None:
            if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
                request_body_kwargs["data"] = getattr(data, "model_dump")()
            elif isinstance(data, dict):
                request_body_kwargs["data"] = data
            else:
                raise TypeError("For application/x-www-form-urlencoded, 'data' must be a dict or a Pydantic model")

    elif files is None and (content_type is None or content_type == "application/json"):
        if data is not None:
            if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
                request_body_kwargs["json"] = getattr(data, "model_dump")()
            elif isinstance(data, dict):
                request_body_kwargs["json"] = data
            else:
                raise TypeError("For application/json, 'data' must be a dict or a Pydantic model")
        else:
            request_body_kwargs["json"] = {}

    elif data is not None and content_type is not None:
        raise ValueError(f"Unsupported content_type '{content_type}' for provided 'data'")

    return request_body_kwargs


def custom_action_operation(
    self: "Crud[T]",
    action: str,
    method: str = "post",
    resource_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    data: Optional[Union[JSONDict, T]] = None,
    params: Optional[JSONDict] = None,
    files: Optional[JSONDict] = None,
    content_type: Optional[str] = None,
) -> Union[T, JSONDict, TypingList[JSONDict], "ListResponseWrapper[T]"]:
    """
    Perform a custom action on the resource.

    Parameters
    ----------
    action : str
        The name of the custom action.
    method : str, optional
        The HTTP method to use. Defaults to "post".
    resource_id : Optional[str], optional
        Optional resource ID if the action is for a specific resource.
    parent_id : Optional[str], optional
        Optional ID of the parent resource for nested resources.
    data : Optional[Union[JSONDict, T]], optional
        Optional data to send with the request.
    params : Optional[JSONDict], optional
        Optional query parameters.
    files : Optional[JSONDict], optional
        Optional dictionary of files to upload (for multipart/form-data requests).
    content_type : Optional[str], optional
        Optional content type for the request. If not provided, defaults to
        "application/json" unless files are provided (which uses multipart/form-data).
        Supported values: "application/json", "application/x-www-form-urlencoded".

    Returns
    -------
    Union[T, JSONDict, List[JSONDict]]
        The API response.

    Raises
    ------
    TypeError
        If the parameters are of incorrect types.
    ValueError
        If the HTTP method is invalid, the action is not defined, or an unsupported content_type is provided.
    DataValidationError
        If the input data fails validation.
    NotFoundError
        If the resource or parent resource (if applicable) is not found.
    NetworkError
        If a network-related error occurs during the request.
    APIError
        For other API-related errors (e.g., 4xx/5xx responses).
    """
    if not isinstance(action, str):
        raise TypeError(f"Action must be a string, got {type(action).__name__}")

    if method not in ["get", "post", "put", "patch", "delete", "head", "options", "trace"]:
        raise ValueError(f"Invalid HTTP method: {method}")

    if resource_id is not None and not isinstance(resource_id, str):
        raise TypeError(f"Resource ID must be a string or None, got {type(resource_id).__name__}")

    if parent_id is not None and not isinstance(parent_id, str):
        raise TypeError(f"Parent ID must be a string or None, got {type(parent_id).__name__}")

    endpoint_args = [arg for arg in [resource_id, action] if arg is not None]
    endpoint = self._get_endpoint(*endpoint_args, parent_args=(parent_id,) if parent_id else None)

    final_kwargs = {}
    if params:
        final_kwargs["params"] = params

    try:
        if method.lower() in ["post", "put", "patch"]:
            request_body_kwargs = self._prepare_request_body_kwargs(data, files, content_type)
            final_kwargs.update(request_body_kwargs)

        response = getattr(self.client, method.lower())(endpoint, **final_kwargs)

        try:
            if hasattr(response, "__iter__") and not isinstance(response, (dict, str, bytes)):
                return response  # type: ignore[no-any-return]
            return self._convert_to_model(response)  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Unexpected error converting custom action response: {e}", exc_info=True)
            raise

    except PydanticValidationError as e:
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        logger.error(
            "Request data validation failed during custom action '%s'. Errors: %s",
            action,
            json.dumps(e.errors()),
        )
        raise DataValidationError(
            "Custom action request data validation failed",
            data=redacted_data,
            pydantic_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in custom_action operation: {e}", exc_info=True)
        raise


# Aliases for the Crud class methods
list = list_operation
create = create_operation
read = read_operation
update = update_operation
partial_update = partial_update_operation
destroy = destroy_operation
custom_action = custom_action_operation
