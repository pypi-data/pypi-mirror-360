from typing import Any, Callable, Dict, List, Optional


class PaginationHelper:
    """
    Helper class for simulating various pagination styles in API responses.

    Supports offset-based, cursor-based, and link-based pagination with
    customizable metadata and link generation.
    """

    items: List[Any]
    page_size: int
    current_page: int
    _total_items: int
    _total_pages: int
    page_param: str
    size_param: str
    base_url: str
    pagination_style: str
    cursor_param: str
    next_cursor_generator: Callable[[int, int], str]
    prev_cursor_generator: Callable[[int, int], str]
    custom_metadata_generator: Optional[Callable[[int, int, int, int], Dict[str, Any]]]
    custom_links_generator: Optional[Callable[[int, int, int, str], Dict[str, str]]]

    def __init__(
        self,
        items: List[Any],
        page_size: int = 10,
        current_page: int = 1,
        total_pages: Optional[int] = None,
        total_items: Optional[int] = None,
        page_param: str = "page",
        size_param: str = "per_page",
        base_url: str = "",
        pagination_style: str = "offset",  # "offset", "cursor", or "link"
        cursor_param: str = "cursor",
        next_cursor_generator: Optional[Callable[[int, int], str]] = None,
        prev_cursor_generator: Optional[Callable[[int, int], str]] = None,
        custom_metadata_generator: Optional[Callable[[int, int, int, int], Dict[str, Any]]] = None,
        custom_links_generator: Optional[Callable[[int, int, int, str], Dict[str, str]]] = None,
    ) -> None:
        """
        Initialize a PaginationHelper instance.

        Args:
            items: The complete list of items to paginate
            page_size: Number of items per page
            current_page: The current page number (1-based)
            total_pages: Override for the calculated total pages
            total_items: Override for the calculated total items
            page_param: URL parameter name for page number
            size_param: URL parameter name for page size
            base_url: Base URL for generating pagination links
            pagination_style: Style of pagination ("offset", "cursor", or "link")
            cursor_param: URL parameter name for cursor-based pagination
            next_cursor_generator: Custom function to generate next page cursor
            prev_cursor_generator: Custom function to generate previous page cursor
            custom_metadata_generator: Custom function to generate pagination metadata
            custom_links_generator: Custom function to generate pagination links
        """
        self.items = items
        self.page_size = page_size
        self.current_page = current_page
        self._total_items = total_items or len(items)
        self._total_pages = total_pages or ((self._total_items + page_size - 1) // page_size)
        self.page_param = page_param
        self.size_param = size_param
        self.base_url = base_url
        self.pagination_style = pagination_style
        self.cursor_param = cursor_param
        self.next_cursor_generator = next_cursor_generator or self._default_next_cursor_generator
        self.prev_cursor_generator = prev_cursor_generator or self._default_prev_cursor_generator
        self.custom_metadata_generator = custom_metadata_generator
        self.custom_links_generator = custom_links_generator

    def get_page(self, page: Optional[int] = None, page_size: Optional[int] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a paginated response for the specified page.

        Args:
            page: The page number to retrieve (1-based)
            page_size: Override for the instance's page size
            cursor: Cursor string for cursor-based pagination

        Returns:
            A dictionary containing:
            - 'data': List of items for the requested page
            - 'metadata': Pagination metadata (varies by pagination style)
            - 'links': URLs for navigating between pages
        """
        size = page_size or self.page_size

        if self.pagination_style == "cursor" and cursor is not None:
            # For cursor-based pagination, decode the cursor to get the page
            # In a real implementation, this would be more sophisticated
            try:
                # Simple cursor implementation - in real code this would be more secure
                import base64

                decoded = base64.b64decode(cursor.encode()).decode()
                parts = decoded.split(":")
                if len(parts) >= 2:
                    page = int(parts[0])
                    size = int(parts[1])
            except Exception:
                # If cursor is invalid, default to first page
                page = 1

        # Default to first page if not specified
        page = page or 1

        start_idx = (page - 1) * size
        end_idx = min(start_idx + size, self._total_items)

        # If we're simulating pagination beyond actual items
        if start_idx >= len(self.items):
            page_items = []
        else:
            page_items = self.items[start_idx : min(end_idx, len(self.items))]

        # Generate metadata based on pagination style
        if self.custom_metadata_generator:
            metadata = self.custom_metadata_generator(page, size, self._total_items, self._total_pages)
        else:
            if self.pagination_style == "offset":
                metadata = {
                    "pagination": {
                        "currentPage": page,
                        "perPage": size,
                        "totalItems": self._total_items,
                        "totalPages": self._total_pages,
                    }
                }
            elif self.pagination_style == "cursor":
                next_cursor = self.next_cursor_generator(page, size) if page < self._total_pages else None
                prev_cursor = self.prev_cursor_generator(page, size) if page > 1 else None
                metadata = {
                    "pagination": {
                        "perPage": size,
                        "totalItems": self._total_items,
                        "nextCursor": next_cursor,
                        "prevCursor": prev_cursor,
                    }
                }
            else:  # link-based or other styles
                metadata = {
                    "pagination": {
                        "perPage": size,
                        "totalItems": self._total_items,
                    }
                }

        # Generate links based on pagination style
        if self.custom_links_generator:
            links = self.custom_links_generator(page, size, self._total_pages, self.base_url)
        else:
            if self.pagination_style == "offset":
                links = self._generate_offset_links(page, size)
            elif self.pagination_style == "cursor":
                links = self._generate_cursor_links(page, size)
            else:  # link-based or other styles
                links = self._generate_link_based_links(page, size)

        return {"data": page_items, "metadata": metadata, "links": links}

    def _generate_offset_links(self, page: int, size: int) -> Dict[str, str]:
        """
        Generate pagination links for offset-based pagination.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Dictionary of link relations to URLs
        """
        links = {
            "self": f"{self.base_url}?{self.page_param}={page}&{self.size_param}={size}",
            "first": f"{self.base_url}?{self.page_param}=1&{self.size_param}={size}",
            "last": f"{self.base_url}?{self.page_param}={self._total_pages}&{self.size_param}={size}",
        }

        if page > 1:
            links["prev"] = f"{self.base_url}?{self.page_param}={page - 1}&{self.size_param}={size}"

        if page < self._total_pages:
            links["next"] = f"{self.base_url}?{self.page_param}={page + 1}&{self.size_param}={size}"

        return links

    def _generate_cursor_links(self, page: int, size: int) -> Dict[str, str]:
        """
        Generate pagination links for cursor-based pagination.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Dictionary of link relations to URLs
        """
        links = {
            "self": f"{self.base_url}?{self.cursor_param}={self.next_cursor_generator(page - 1, size)}",
        }

        if page > 1:
            links["prev"] = f"{self.base_url}?{self.cursor_param}={self.prev_cursor_generator(page, size)}"

        if page < self._total_pages:
            links["next"] = f"{self.base_url}?{self.cursor_param}={self.next_cursor_generator(page, size)}"

        return links

    def _generate_link_based_links(self, page: int, size: int) -> Dict[str, str]:
        """
        Generate pagination links for link-based pagination.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Dictionary of link relations to URLs
        """
        base = self.base_url.rstrip("/")
        links = {
            "self": f"{base}?{self.page_param}={page}&{self.size_param}={size}",
        }

        if self._total_pages > 1:
            links["first"] = f"{base}?{self.page_param}=1&{self.size_param}={size}"
            links["last"] = f"{base}?{self.page_param}={self._total_pages}&{self.size_param}={size}"

        if page > 1:
            links["prev"] = f"{base}?{self.page_param}={page - 1}&{self.size_param}={size}"

        if page < self._total_pages:
            links["next"] = f"{base}?{self.page_param}={page + 1}&{self.size_param}={size}"

        return links

    def _default_next_cursor_generator(self, page: int, size: int) -> str:
        """
        Default generator for next page cursor.

        Creates a base64-encoded string containing page and size information.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Base64-encoded cursor string
        """
        import base64

        cursor_data = f"{page + 1}:{size}:next"
        return base64.b64encode(cursor_data.encode()).decode()

    def _default_prev_cursor_generator(self, page: int, size: int) -> str:
        """
        Default generator for previous page cursor.

        Creates a base64-encoded string containing page and size information.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Base64-encoded cursor string
        """
        import base64

        cursor_data = f"{page - 1}:{size}:prev"
        return base64.b64encode(cursor_data.encode()).decode()
