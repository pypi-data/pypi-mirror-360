"""
Module `endpoint.py`.

This module provides functions for building and manipulating API endpoints.
It handles the construction of resource paths, including nested resources,
and ensures proper formatting of URL paths.
"""

import logging
from typing import TYPE_CHECKING, List, Optional, Tuple, Union, cast

if TYPE_CHECKING:
    from .base import Crud

# Get a logger for this module
logger = logging.getLogger(__name__)

# Type alias for path arguments
PathArgs = Optional[Union[str, int]]

__all__ = [
    "_endpoint_prefix",
    "_validate_path_segments",
    "_get_parent_path",
    "_build_resource_path",
    "_get_prefix_segments",
    "_join_path_segments",
    "_get_endpoint",
]


def _endpoint_prefix(self: "Crud") -> Union[Tuple[Optional[str], Optional[str]], List[Optional[str]]]:
    """
    Construct the endpoint prefix.

    This method can be overridden in subclasses to provide a custom endpoint prefix.

    Returns
    -------
    Union[Tuple[Optional[str], Optional[str]], List[Optional[str]]]
        The endpoint prefix segments.
    """
    if self.parent:
        return (self.parent._resource_path, None)
    return []


def _validate_path_segments(self: "Crud", *args: PathArgs) -> None:
    """
    Validate the types of path segments.

    Parameters
    ----------
    *args : PathArgs
        Variable number of path segments (e.g., resource IDs, actions).

    Raises
    ------
    TypeError
        If any arg is not None, str, or int.
    """
    for arg in args:
        if arg is not None and not isinstance(arg, (str, int)):
            raise TypeError(f"Path segment must be a string, integer, or None, got {type(arg).__name__}")


def _get_parent_path(self: "Crud", parent_args: Optional[tuple] = None) -> str:
    """
    Get the parent path if a parent exists.

    Parameters
    ----------
    parent_args : Optional[tuple], optional
        Optional tuple containing path segments for the parent resource.

    Returns
    -------
    str
        The parent path or empty string if no parent exists.
    """
    if not self.parent:
        return ""

    if parent_args:
        return cast(str, self.parent._get_endpoint(*parent_args))
    return cast(str, self.parent._get_endpoint())


def _build_resource_path(self: "Crud", *args: PathArgs) -> List[str]:
    """
    Build the current resource path segments.

    Parameters
    ----------
    *args : PathArgs
        Variable number of path segments (e.g., resource IDs, actions).

    Returns
    -------
    List[str]
        The resource path segments.
    """
    segments = []
    for arg in args:
        if arg is not None:
            segments.append(str(arg))
    return segments


def _get_prefix_segments(self: "Crud") -> List[str]:
    """
    Get the prefix segments for the endpoint.

    Returns
    -------
    List[str]
        The prefix segments.
    """
    prefix = self._endpoint_prefix()
    if isinstance(prefix, tuple):
        return cast(List[str], self._build_resource_path(*prefix))
    return cast(List[str], self._build_resource_path(*prefix))


def _join_path_segments(self: "Crud", segments: List[str]) -> str:
    """
    Join path segments into a URL.

    Parameters
    ----------
    segments : List[str]
        List of path segments.

    Returns
    -------
    str
        The joined URL path.
    """
    if not segments:
        return ""

    path = "/".join(segment.strip("/") for segment in segments if segment)
    return path


def _get_endpoint(self: "Crud", *args: Optional[Union[str, int]], parent_args: Optional[tuple] = None) -> str:
    """
    Construct the endpoint path.

    Parameters
    ----------
    *args : Optional[Union[str, int]]
        Variable number of path segments (e.g., resource IDs, actions).
    parent_args : Optional[tuple], optional
        Optional tuple containing path segments for the parent resource.

    Returns
    -------
    str
        The constructed endpoint path.

    Raises
    ------
    TypeError
        If arg in args or parent_args is not None, str, or int.
    """
    self._validate_path_segments(*args)

    parent_path = self._get_parent_path(parent_args)

    prefix_segments = self._get_prefix_segments()

    resource_segments = [self._resource_path]
    resource_segments.extend(self._build_resource_path(*args))

    all_segments = []
    if parent_path:
        all_segments.append(parent_path)

    elif prefix_segments:
        all_segments.append(self._join_path_segments(prefix_segments))

    all_segments.append(self._join_path_segments(resource_segments))

    endpoint = "/".join(segment.strip("/") for segment in all_segments if segment)

    logger.debug(f"Built endpoint: {endpoint}")
    return endpoint
