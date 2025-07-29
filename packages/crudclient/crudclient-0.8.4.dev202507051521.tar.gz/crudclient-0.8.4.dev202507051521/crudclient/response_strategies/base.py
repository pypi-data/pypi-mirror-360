"""
Module `response_strategies.base`
================================

This module defines the base classes and protocols for response model strategies.

Classes:
    - ResponseModelStrategy: Abstract base class for response model conversion strategies.
    - ModelDumpable: Protocol for objects that can be dumped to a model.

Type Variables:
    - T: The type of the data model used for the resource.
"""

import logging
from abc import ABC, abstractmethod
from typing import Generic, List, Protocol, TypeVar, Union

from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse

# Get a logger for this module
logger = logging.getLogger(__name__)


class ModelDumpable(Protocol):
    def model_dump(self) -> dict: ...  # noqa: E704


T = TypeVar("T", bound=ModelDumpable)


class ResponseModelStrategy(ABC, Generic[T]):
    """
    Abstract base class for response model conversion strategies.

    This class defines the interface for converting API responses to model instances.
    Concrete implementations should provide specific conversion logic for different
    response formats.
    """

    @abstractmethod
    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]:
        pass

    @abstractmethod
    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]:
        pass
