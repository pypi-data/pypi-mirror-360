"""Module `models.py`.

This module defines various models used throughout the crudclient library.
These models provide structured data representations for API responses and other data.

Classes
-------
- RoleBasedModel: A model that validates fields based on the current role.
- Link: A model representing a hyperlink.
- PaginationLinks: A model representing pagination links.
- ApiResponse: A generic model for API responses with pagination.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class RoleBasedModel(BaseModel):
    """
    A model that validates fields based on the current role.

    This model allows for role-based field validation, where certain fields may be
    required or disallowed based on the current role. The role is specified using
    the `_role` field in the input data.

    Note: This model is currently not used in the core library but is kept here
    as it's intended to be the foundation for future enhancements to the library's
    validation capabilities. Future plans include expanding this to support more
    complex validation scenarios and integrating it with the CRUD operations.

    Attributes
    ----------
    _current_role : Optional[str]
        The current role for validation.
    """

    _current_role: Optional[str]

    @classmethod
    def check_fields_based_on_role(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fields based on the current role.

        Parameters
        ----------
        values : Dict[str, Any]
            The input values to validate.

        Returns
        -------
        Dict[str, Any]
            The validated values.

        Raises
        ------
        ValueError
            If a required field is missing or a disallowed field is present.
        """
        # Implementation placeholder - real validation logic should be implemented here
        return values


class Link(BaseModel):
    """
    A model representing a hyperlink.

    Attributes
    ----------
    href : Optional[HttpUrl]
        The URL of the link.
    """

    href: Optional[HttpUrl] = None

    @field_validator("href")
    @classmethod
    def validate_href(cls, v: Optional[HttpUrl]) -> Optional[HttpUrl]:
        """Validate the href URL if present."""
        if v is None:
            return v
        # Additional validation could be added here if needed
        return v


class PaginationLinks(BaseModel):
    """
    A model representing pagination links.

    Attributes
    ----------
    next : Optional[Link]
        Link to the next page, if available.
    previous : Optional[Link]
        Link to the previous page, if available.
    self : Link
        Link to the current page.
    """

    next: Optional[Link] = None
    previous: Optional[Link] = None
    self: Link = Field(..., description="Link to the current page")

    @field_validator("self")
    @classmethod
    def validate_self_link(cls, v: Link) -> Link:
        """Validate that the self link is present and properly formatted."""
        if v.href is None:
            raise ValueError("Self link must have a valid href")
        return v


class IdRef(BaseModel):
    """
    A simple model representing a reference to another object by its ID.

    Attributes
    ----------
    id : int
        The unique identifier of the referenced object.
    """

    id: int

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IdUrl(BaseModel):
    """
    A simple model representing an object with an ID and a URL.

    Attributes
    ----------
    id : int
        The unique identifier of the object.
    url : Optional[HttpUrl]
        The URL pointing to the object resource.
    """

    id: int
    url: Optional[HttpUrl] = None


class ListResponseWrapper(BaseModel, Generic[T_co]):
    """
    A generic model for API list responses with pagination.

    This model represents a standard API response format for lists with pagination links,
    a count of total items, and the actual data. This is the base class for API-specific
    response wrappers.

    Attributes
    ----------
    links : Optional[PaginationLinks]
        Pagination links.
    count : int
        Total number of items.
    data : List[T_co]
        The actual data items (can be populated from 'values' alias).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    links: Optional[PaginationLinks] = Field(default=None, alias="_links", description="Pagination links")
    count: int = Field(..., ge=0, description="Total number of items")
    data: List[T_co] = Field(..., validation_alias=AliasChoices("data", "values"), description="The actual data items")

    @field_validator("count")
    @classmethod
    def validate_count(cls, v: int) -> int:
        """Validate that count is non-negative."""
        if v < 0:
            raise ValueError("Count cannot be negative")
        return v


# Backward compatibility alias
ApiResponse = ListResponseWrapper
