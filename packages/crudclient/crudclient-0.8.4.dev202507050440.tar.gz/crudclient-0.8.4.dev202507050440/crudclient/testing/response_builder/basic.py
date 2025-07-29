"""
Basic response builder utilities for mock client.

This module provides utilities for building basic API responses with structured data,
nested structures, and GraphQL format. These utilities help create consistent and
realistic mock responses for testing API interactions.
"""

from typing import Any, Dict, List, Optional

from .response import MockResponse


class BasicResponseBuilder:
    """
    Builder for creating basic API responses.

    This class provides static methods for creating various types of API responses
    with structured data, including responses with metadata, links, and nested
    structures. It also supports GraphQL-specific response formats.
    """

    DEFAULT_HEADERS = {"Content-Type": "application/json"}

    @classmethod
    def create_response(
        cls,
        status_code: int = 200,
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = "application/json",
    ) -> MockResponse:
        """
        Create a mock response with structured data.

        This method creates a response with a standardized structure that includes
        data, metadata, links, and errors sections, following common API design
        patterns.

        Args:
            status_code: HTTP status code for the response
            data: Primary response data
            metadata: Response metadata such as pagination info or timestamps
            links: HATEOAS links for resource navigation
            errors: Error details if the response represents an error
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse instance with the specified structure and content
        """
        final_headers = cls.DEFAULT_HEADERS.copy()
        if headers:
            final_headers.update(headers)
        if content_type:
            final_headers["Content-Type"] = content_type
        else:
            # If content_type is explicitly None, remove the default
            final_headers.pop("Content-Type", None)

        # Handle 204 No Content specifically
        if status_code == 204:
            return MockResponse(status_code=status_code, headers=final_headers)

        # Handle non-JSON responses
        if content_type != "application/json":
            if not isinstance(data, (str, bytes)) and data is not None:
                raise ValueError(f"Data must be str or bytes for content type {content_type}, got {type(data)}")
            return MockResponse(status_code=status_code, text=data, headers=final_headers)

        # Build JSON response body
        response_body: Dict[str, Any] = {}
        if data is not None:
            response_body["data"] = data
        if metadata is not None:
            response_body["metadata"] = metadata
        if links is not None:
            response_body["links"] = links
        if errors is not None:
            response_body["errors"] = errors

        # Return JSON response only if there's content or it's not a 204
        json_data = response_body if response_body else None
        return MockResponse(status_code=status_code, json_data=json_data, headers=final_headers)

    @classmethod
    def created(
        cls,
        data: Any,
        location: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        """
        Creates a 201 Created response.

        Args:
            data: Primary response data
            location: Location header value for the created resource
            metadata: Response metadata
            links: HATEOAS links for resource navigation
            headers: Additional HTTP headers

        Returns:
            A MockResponse with 201 status code and the specified data
        """
        final_headers = headers or {}
        if location:
            final_headers["Location"] = location
        return cls.create_response(
            status_code=201,
            data=data,
            metadata=metadata,
            links=links,
            headers=final_headers,
        )

    @classmethod
    def no_content(cls, headers: Optional[Dict[str, str]] = None) -> MockResponse:
        """
        Creates a 204 No Content response.

        Args:
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse with 204 status code and no content
        """
        # 204 should not have a Content-Type header typically
        final_headers = headers or {}
        return cls.create_response(status_code=204, headers=final_headers, content_type=None)

    @classmethod
    def create_nested_response(
        cls,
        structure: Dict[str, Any],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        """
        Create a response with a nested structure.

        This method allows for creating responses with arbitrary nested structures,
        which is useful for testing APIs that return complex, deeply nested JSON.

        Args:
            structure: Nested structure for the response body
            status_code: HTTP status code for the response
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse instance with the specified nested structure
        """
        final_headers = cls.DEFAULT_HEADERS.copy()
        if headers:
            final_headers.update(headers)
        return MockResponse(status_code=status_code, json_data=structure, headers=final_headers)

    @staticmethod
    def create_graphql_response(
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        extensions: Optional[Dict[str, Any]] = None,
    ) -> MockResponse:
        """Create a GraphQL response.

        This helper builds a response body that follows the GraphQL
        specification with ``data``, ``errors`` and ``extensions`` fields.

        Args:
            data: GraphQL data returned for the query.
            errors: Optional list of error objects.
            extensions: Optional extensions providing additional metadata.

        Returns:
            A ``MockResponse`` formatted according to the GraphQL spec.
        """
        body: Dict[str, Any] = {}
        if data is not None:
            body["data"] = data
        if errors is not None:
            body["errors"] = errors
        if extensions is not None:
            body["extensions"] = extensions

        return MockResponse(status_code=200, json_data=body, headers={"Content-Type": "application/json"})
