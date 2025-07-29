"""
Module `response_strategies.types`
================================

This module defines type aliases used by response model strategies.

Type Aliases:
    - ApiResponseInstance: Type alias for ApiResponse[Any]
    - ApiResponseType: Type alias for Type[ApiResponseInstance]
    - ResponseTransformer: Type alias for Callable[[Any], Any]
"""

from typing import Any, Callable, Type

from typing_extensions import TypeAlias

from ..models import ApiResponse

# Type aliases
ApiResponseInstance: TypeAlias = "ApiResponse[Any]"
ApiResponseType: TypeAlias = Type[ApiResponseInstance]
ResponseTransformer: TypeAlias = Callable[[Any], Any]
