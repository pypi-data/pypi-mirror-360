"""
Request record for tracking HTTP requests in CRUD mocks.

This module provides a class for recording and tracking HTTP requests made during
testing, allowing for later inspection and verification of request details.
"""

import time
from typing import Any, Dict, Optional

from crudclient.testing.response_builder.response import MockResponse


class RequestRecord:
    """
    Record of an HTTP request made during testing.

    This class stores details about HTTP requests, including method, URL, parameters,
    payload data, headers, and the associated response. It also records the timestamp
    when the request was made, allowing for chronological analysis of request sequences.
    """

    def __init__(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        response: Optional[MockResponse] = None,
    ) -> None:
        """
        Initialize a new request record.

        Args:
            method: HTTP method used for the request (e.g., GET, POST)
            url: URL of the request
            params: URL query parameters (optional)
            data: Form data sent with the request (optional)
            json: JSON data sent with the request (optional)
            headers: HTTP headers sent with the request (optional)
            response: MockResponse object returned for this request (optional)
        """
        self.method: str = method.upper()
        self.url: str = url
        self.params: Optional[Dict[str, Any]] = params
        self.data: Optional[Dict[str, Any]] = data
        self.json: Optional[Dict[str, Any]] = json
        self.headers: Dict[str, Any] = headers or {}
        self.response: Optional[MockResponse] = response
        self.timestamp: float = time.time()

        # Add URL parameters to the URL if they exist
        if params and params:
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            if "?" in self.url:
                self.url = f"{self.url}&{param_str}"
            else:
                self.url = f"{self.url}?{param_str}"

    def __repr__(self) -> str:
        """
        Get a string representation of the request record.

        Returns:
            A string in the format "<RequestRecord METHOD URL>"
        """
        return f"<RequestRecord {self.method} {self.url}>"
