from typing import Any, List, Optional

from .basic import BasicResponseBuilder
from .response import MockResponse


class PaginationResponseBuilder:
    """
    Builder for creating paginated API responses.

    This class provides utilities for creating mock responses that simulate
    paginated API endpoints, including pagination metadata and navigation links.
    """

    @staticmethod
    def create_paginated_response(
        items: List[Any],
        page: int = 1,
        per_page: int = 10,
        total_items: Optional[int] = None,
        total_pages: Optional[int] = None,
        base_url: str = "/api/items",
        include_links: bool = True,
    ) -> MockResponse:
        """
        Create a mock response with pagination support.

        This method creates a standardized paginated response with the requested
        page of items, pagination metadata, and navigation links following
        common REST API pagination patterns.

        Args:
            items: The complete list of items to paginate
            page: The current page number (1-based)
            per_page: Number of items per page
            total_items: Override for the calculated total number of items
            total_pages: Override for the calculated total number of pages
            base_url: Base URL for generating pagination links
            include_links: Whether to include HATEOAS navigation links

        Returns:
            A MockResponse instance with paginated data, metadata, and links

        Examples:
            ```python
            # Create a paginated response with 100 items, showing page 2 with 10 items per page
            items = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]
            response = PaginationResponseBuilder.create_paginated_response(
                items=items,
                page=2,
                per_page=10,
                base_url="/api/products"
            )

            # The response will contain:
            # - 10 items (items 11-20)
            # - Pagination metadata (page=2, per_page=10, total_items=100, total_pages=10)
            # - Navigation links (self, first, prev, next, last)
            ```
        """
        # Calculate totals if not provided
        _total_items = total_items if total_items is not None else len(items)
        _total_pages = total_pages if total_pages is not None else max(1, (_total_items + per_page - 1) // per_page)

        # Get items for the current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, _total_items)

        # If we have actual items, paginate them
        page_items = []
        if items and start_idx < len(items):
            page_items = items[start_idx : min(end_idx, len(items))]

        # Create metadata
        metadata = {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": _total_items,
                "total_pages": _total_pages,
            }
        }

        # Create links
        links = None
        if include_links:
            links = {
                "self": f"{base_url}?page={page}&per_page={per_page}",
                "first": f"{base_url}?page=1&per_page={per_page}",
                "last": f"{base_url}?page={_total_pages}&per_page={per_page}",
            }

            if page > 1:
                links["prev"] = f"{base_url}?page={page - 1}&per_page={per_page}"

            if page < _total_pages:
                links["next"] = f"{base_url}?page={page + 1}&per_page={per_page}"

        return BasicResponseBuilder.create_response(status_code=200, data=page_items, metadata=metadata, links=links)
