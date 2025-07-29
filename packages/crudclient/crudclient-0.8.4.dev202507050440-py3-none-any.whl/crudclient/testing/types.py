"""
Type definitions for the crudclient testing framework.

This module provides type definitions and utility classes used throughout the testing framework.
"""

from typing import Any, Dict, List, Sequence, Union

from typing_extensions import Protocol, TypeAlias

from crudclient.testing.response_builder.response import MockResponse
from crudclient.testing.spy.method_call import MethodCall

# Type aliases for HTTP components
Headers: TypeAlias = Dict[str, str]
QueryParams: TypeAlias = Dict[str, Union[str, int, float, bool, Sequence[Union[str, int, float, bool]], None]]
HttpMethod: TypeAlias = str
StatusCode: TypeAlias = int
RequestBody: TypeAlias = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseBody: TypeAlias = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseData: TypeAlias = Dict[str, Any]


# We're using MethodCall directly instead of a separate CallRecord Protocol
# since MethodCall already has the required attributes
class SpyTarget(Protocol):
    """
    Protocol defining the interface for objects that can be verified by the Verifier class.

    A SpyTarget must have a 'calls' attribute that contains call records.
    Each call record should have method_name, args, and kwargs attributes.
    """

    calls: List[MethodCall]  # Using the concrete MethodCall type to match test implementation


# Re-export MockResponse for convenience
__all__ = [
    "Headers",
    "QueryParams",
    "HttpMethod",
    "StatusCode",
    "RequestBody",
    "ResponseBody",
    "ResponseData",
    "SpyTarget",
    "MockResponse",
]
