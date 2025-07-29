"""
Module `base.py`.

This module defines the Crud class, which is the base class for all CRUD operations.
It provides a generic implementation of CRUD (Create, Read, Update, Delete) operations
for API resources. It supports both top-level and nested resources, and can be easily
extended for specific API endpoints.
"""

import logging
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
)

from typing_extensions import TypeAlias

from ..client import Client

# DataValidationError is used in imported methods
from ..models import ListResponseWrapper
from ..response_strategies import (
    DefaultResponseModelStrategy,
    ModelDumpable,
    PathBasedResponseModelStrategy,
    ResponseModelStrategy,
)
from ..types import JSONDict, JSONList

# Get a logger for this module
logger = logging.getLogger(__name__)


# Type alias for path arguments used in endpoint methods
PathArgs = Optional[Union[str, int]]

T = TypeVar("T", bound=ModelDumpable)
HttpMethodString: TypeAlias = Literal["get", "post", "put", "patch", "delete", "head", "options", "trace"]
CrudInstance: TypeAlias = "Crud[Any]"
CrudType: TypeAlias = Type[CrudInstance]


class Crud(Generic[T]):
    """
    Base class for CRUD operations on API resources, supporting both top-level and nested resources.

    This class provides a generic implementation of common CRUD operations and can be
    easily extended for specific API endpoints.

    Attributes
    ----------
    _resource_path : str
        The base path for the resource in the API.
    _datamodel : Optional[Type[T]]
        The data model class for the resource.
    _api_response_model : Optional[Type[ApiResponse]]
        Custom API response model, if any.
    _create_model : Optional[Type[T]]
        The data model class for creating resources.
    _update_model : Optional[Type[T]]
        The data model class for updating resources.
    _response_strategy : Optional[ResponseModelStrategy[T]]
        The strategy to use for converting responses.
    _list_return_keys : List[str]
        Possible keys for list data in API responses.
    _update_mode : str
        Default update mode: "standard" or "no_resource_id".
    allowed_actions : List[str]
        List of allowed methods for this resource.
    client : Client
        An instance of the API client.
    parent : Optional[Crud]
        Optional parent Crud instance for nested resources.
    """

    _resource_path: str = ""
    _datamodel: Optional[Type[T]] = None

    if TYPE_CHECKING:
        _api_response_model: ClassVar[Optional[Type[ListResponseWrapper[ModelDumpable]]]] = None
    else:
        _api_response_model: ClassVar[Optional[Type[ListResponseWrapper[Any]]]] = None

    _create_model: ClassVar[Optional[Type[ModelDumpable]]] = None
    _update_model: ClassVar[Optional[Type[ModelDumpable]]] = None
    _response_strategy: Optional[ResponseModelStrategy[T]] = None
    _list_return_keys: List[str] = ["data", "results", "items"]
    _update_mode: str = "standard"
    allowed_actions: List[str] = ["list", "create", "read", "update", "partial_update", "destroy"]
    client: Client
    parent: Optional["Crud"]

    def __init__(self, client: Client, parent: Optional["Crud"] = None) -> None:
        """
        Initialize the CRUD resource.

        Parameters
        ----------
        client : Client
            An instance of the API client.
        parent : Optional[Crud], optional
            Optional parent Crud instance for nested resources.

        Raises
        ------
        ValueError
            If the resource path is not set.
        """
        if not self._resource_path:
            raise ValueError("Resource path must be set")

        self.client = client
        self.parent = parent

        self._init_response_strategy()

    def _init_response_strategy(self: "Crud") -> None:
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

    # Import methods from other modules
    # --- Endpoint Methods ---
    from .endpoint import _build_resource_path  # type: ignore
    from .endpoint import _endpoint_prefix  # type: ignore
    from .endpoint import _get_endpoint  # type: ignore
    from .endpoint import _get_parent_path  # type: ignore
    from .endpoint import _get_prefix_segments  # type: ignore
    from .endpoint import _join_path_segments  # type: ignore
    from .endpoint import _validate_path_segments  # type: ignore

    # --- Operations Helper Methods ---
    from .operations import _prepare_request_body_kwargs  # type: ignore

    # --- Response Conversion Methods ---
    from .response_conversion import _convert_to_list_model  # type: ignore
    from .response_conversion import _convert_to_model  # type: ignore
    from .response_conversion import _dump_data  # type: ignore
    from .response_conversion import _dump_dictionary  # type: ignore
    from .response_conversion import _dump_model_instance  # type: ignore
    from .response_conversion import _fallback_list_conversion  # type: ignore
    from .response_conversion import _validate_and_dump_full_dict  # type: ignore
    from .response_conversion import _validate_list_return  # type: ignore
    from .response_conversion import _validate_partial_dict  # type: ignore
    from .response_conversion import _validate_response  # type: ignore

    # --- Operations Methods (defined as proper methods for type checking) ---
    def list(
        self, parent_id: Optional[str] = None, params: Optional["JSONDict"] = None, **kwargs: Any
    ) -> Union["JSONList", List[T], "ListResponseWrapper[T]"]:
        """Retrieve a list of resources."""
        from .operations import list_operation

        return list_operation(self, parent_id, params, **kwargs)

    def create(
        self, data: Union["JSONDict", T], parent_id: Optional[str] = None, params: Optional["JSONDict"] = None, **kwargs: Any
    ) -> Union[T, "JSONDict"]:
        """Create a new resource."""
        from .operations import create_operation

        return create_operation(self, data, parent_id, params, **kwargs)

    def read(self, resource_id: str, parent_id: Optional[str] = None, params: Optional["JSONDict"] = None, **kwargs: Any) -> Union[T, "JSONDict"]:
        """Retrieve a single resource."""
        from .operations import read_operation

        return read_operation(self, resource_id, parent_id, **kwargs)

    def update(
        self,
        resource_id: Optional[str] = None,
        data: Optional[Union["JSONDict", T]] = None,
        parent_id: Optional[str] = None,
        update_mode: Optional[str] = None,
        params: Optional["JSONDict"] = None,
        **kwargs: Any,
    ) -> Union[T, "JSONDict"]:
        """Update an existing resource."""
        from .operations import update_operation

        return update_operation(self, resource_id, data, parent_id, update_mode, params, **kwargs)

    def partial_update(
        self, resource_id: str, data: Union["JSONDict", T], parent_id: Optional[str] = None, params: Optional["JSONDict"] = None, **kwargs: Any
    ) -> Union[T, "JSONDict"]:
        """Partially update an existing resource."""
        from .operations import partial_update_operation

        return partial_update_operation(self, resource_id, data, parent_id, params, **kwargs)

    def destroy(self, resource_id: str, parent_id: Optional[str] = None, params: Optional["JSONDict"] = None, **kwargs: Any) -> None:
        """Delete a resource."""
        from .operations import destroy_operation

        return destroy_operation(self, resource_id, parent_id, params, **kwargs)

    def custom_action(
        self,
        action: str,
        method: str = "post",
        resource_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        data: Optional[Union["JSONDict", T]] = None,
        params: Optional["JSONDict"] = None,
        files: Optional["JSONDict"] = None,
        content_type: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[T, "JSONDict", List["JSONDict"], "ListResponseWrapper[T]"]:
        """Perform a custom action on the resource."""
        from .operations import custom_action_operation

        return custom_action_operation(self, action, method, resource_id, parent_id, data, params, files, content_type, **kwargs)


# Alias for backward compatibility
CrudBase = Crud
