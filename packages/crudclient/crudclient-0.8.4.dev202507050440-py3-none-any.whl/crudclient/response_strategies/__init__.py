"""
Module `response_strategies`
==========================

This module defines response model strategies for handling different API response formats
when converting them to model instances. These strategies are used by the Crud class to
provide flexible handling of various API response structures.

Classes:
    - ResponseModelStrategy: Abstract base class for response model conversion strategies.
    - DefaultResponseModelStrategy: Default implementation for backward compatibility.
    - PathBasedResponseModelStrategy: Strategy for extracting data using path expressions.
    - ModelDumpable: Protocol for objects that can be dumped to a model.

Type Variables:
    - T: The type of the data model used for the resource.
"""

from .base import ModelDumpable, ResponseModelStrategy, T
from .default import DefaultResponseModelStrategy
from .path_based import PathBasedResponseModelStrategy
from .types import ApiResponseInstance, ApiResponseType, ResponseTransformer

__all__ = [
    "ResponseModelStrategy",
    "DefaultResponseModelStrategy",
    "PathBasedResponseModelStrategy",
    "ModelDumpable",
    "ResponseTransformer",
    "ApiResponseInstance",
    "ApiResponseType",
    "T",
]
