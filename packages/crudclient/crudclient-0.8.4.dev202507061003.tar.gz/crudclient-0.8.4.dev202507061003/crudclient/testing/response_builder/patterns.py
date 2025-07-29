import re
from typing import Any, Callable, Dict, List, Optional, Union

from crudclient.testing.response_builder.response import MockResponse


class ResponsePattern:
    """
    Defines a pattern for matching HTTP requests and providing appropriate mock responses.

    This class allows for sophisticated request matching based on URL patterns, HTTP methods,
    query parameters, request data, JSON payloads, headers, and custom conditions. It's used
    to create mock API endpoints that respond differently based on request attributes.
    """

    def __init__(
        self,
        method: str,
        url_pattern: str,
        response: Union[MockResponse, Callable[..., MockResponse]],
        params_matcher: Optional[Dict[str, Any]] = None,
        data_matcher: Optional[Dict[str, Any]] = None,
        json_matcher: Optional[Dict[str, Any]] = None,
        headers_matcher: Optional[Dict[str, Any]] = None,
        call_count: int = 0,
        max_calls: Optional[int] = None,
        conditions: Optional[List[Callable[[Dict[str, Any]], bool]]] = None,
    ):
        """
        Initialize a new ResponsePattern for matching requests and providing responses.

        Args:
            method: HTTP method to match (e.g., "GET", "POST")
            url_pattern: Regular expression pattern to match request URLs
            response: Either a MockResponse object or a callable that returns a MockResponse
            params_matcher: Dictionary of query parameters to match
            data_matcher: Dictionary of form data to match
            json_matcher: Dictionary of JSON payload to match
            headers_matcher: Dictionary of headers to match
            call_count: Initial call count (typically 0)
            max_calls: Maximum number of times this pattern should match
            conditions: List of additional functions that take request context and return boolean

        Examples:
            ```python
            # Create a pattern for a simple GET endpoint
            pattern = ResponsePattern(
                method="GET",
                url_pattern=r"^/api/users/\\d+$",
                response=MockResponse(
                    status_code=200,
                    json_data={"id": 1, "name": "John Doe"}
                )
            )

            # Create a pattern with a dynamic response based on the request
            def create_response(**kwargs):
                user_id = re.search(r"/users/(\\d+)", kwargs["url"]).group(1)
                return MockResponse(
                    status_code=200,
                    json_data={"id": int(user_id), "name": f"User {user_id}"}
                )

            pattern = ResponsePattern(
                method="GET",
                url_pattern=r"^/api/users/\\d+$",
                response=create_response
            )
            ```
        """
        self.method = method.upper()
        self.url_pattern = re.compile(url_pattern)
        self.response = response
        self.params_matcher = params_matcher
        self.data_matcher = data_matcher
        self.json_matcher = json_matcher
        self.headers_matcher = headers_matcher
        self.call_count = call_count
        self.max_calls = max_calls
        self.conditions = conditions or []

    def matches(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if this pattern matches the given request.

        Evaluates whether the provided request attributes match this pattern's criteria.
        All specified matchers must pass for the pattern to match.

        Args:
            method: HTTP method of the request
            url: URL of the request
            params: Query parameters of the request
            data: Form data of the request
            json: JSON payload of the request
            headers: Headers of the request

        Returns:
            True if the request matches this pattern, False otherwise

        Note:
            If max_calls is set and call_count has reached it, this will return False
            even if all other criteria match.
        """
        if self.method != method.upper():
            return False

        if not self.url_pattern.search(url):
            return False

        if self.max_calls is not None and self.call_count >= self.max_calls:
            return False

        if self.params_matcher and not self._dict_matches(self.params_matcher, params or {}):
            return False

        if self.data_matcher and not self._dict_matches(self.data_matcher, data or {}):
            return False

        if self.json_matcher and not self._dict_matches(self.json_matcher, json or {}):
            return False

        if self.headers_matcher and not self._dict_matches(self.headers_matcher, headers or {}):
            return False

        # Check additional conditions
        request_context = {
            "method": method,
            "url": url,
            "params": params or {},
            "data": data or {},
            "json": json or {},
            "headers": headers or {},
        }

        for condition in self.conditions:
            if not condition(request_context):
                return False

        return True

    def get_response(self, **kwargs: Any) -> MockResponse:
        """
        Get the response for a matched request.

        Increments the call count and returns either the static MockResponse
        or calls the response function with the provided kwargs.

        Args:
            **kwargs: Request context parameters passed to the response callable

        Returns:
            A MockResponse instance
        """
        self.call_count += 1
        if callable(self.response):
            return self.response(**kwargs)
        return self.response

    @staticmethod
    def _dict_matches(matcher: Dict[str, Any], actual: Dict[str, Any]) -> bool:
        """
        Check if a dictionary matches the expected pattern.

        For each key-value pair in the matcher:
        - If the key doesn't exist in the actual dict, returns False
        - If the value is callable, it's treated as a predicate function and called with the actual value
        - Otherwise, values are compared for equality

        Args:
            matcher: Dictionary with expected keys and values/predicates
            actual: Dictionary to check against the matcher

        Returns:
            True if all matcher criteria are satisfied, False otherwise
        """
        for key, value in matcher.items():
            if key not in actual:
                return False
            if callable(value):
                if not value(actual[key]):
                    return False
            elif value != actual[key]:
                return False
        return True
