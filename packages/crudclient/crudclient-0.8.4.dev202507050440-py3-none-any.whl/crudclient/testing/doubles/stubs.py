import json
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

# Removed unused imports: copy, re, uuid, Callable, Type, datetime
# Removed unused imports: API, Client, ClientConfig


class Response:
    """Abstract base class defining the interface for an HTTP response object."""

    def __init__(self) -> None:
        pass

    @property
    def status_code(self) -> int:
        """The HTTP status code of the response."""
        raise NotImplementedError

    @property
    def content(self) -> bytes:
        """The response body as bytes."""
        raise NotImplementedError

    @property
    def text(self) -> str:
        """The response body decoded as text."""
        raise NotImplementedError

    @property
    def headers(self) -> Dict[str, str]:
        """A dictionary of response headers."""
        raise NotImplementedError

    def json(self) -> Any:
        """Parse the response body as JSON."""
        raise NotImplementedError

    def raise_for_status(self) -> None:
        """Raise an HTTPError for bad status codes (4xx or 5xx)."""
        raise NotImplementedError


# CrudBase moved to stubs_crud.py
class StubResponse(Response):
    """A concrete stub implementation of the Response interface for testing."""

    def __init__(
        self,
        status_code: int = 200,
        content: Optional[Union[str, bytes, Dict[str, Any], List[Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: str = "utf-8",
        elapsed: Optional[timedelta] = None,
    ):
        """Initialize the StubResponse."""
        super().__init__()
        self._status_code = status_code
        self._headers = headers or {}
        self._encoding = encoding
        self._elapsed = elapsed or timedelta(milliseconds=50)

        # Handle different content types
        if content is None:
            self._content = b""
            self._text = ""
            self._json_data = None
        elif isinstance(content, (dict, list)):
            self._json_data = content
            self._text = json.dumps(content)
            self._content = self._text.encode(encoding)
        elif isinstance(content, str):
            self._text = content
            self._content = content.encode(encoding)
            try:
                self._json_data = json.loads(content)
            except json.JSONDecodeError:
                self._json_data = None
        elif isinstance(content, bytes):
            self._content = content
            self._text = content.decode(encoding, errors="replace")
            try:
                self._json_data = json.loads(self._text)
            except json.JSONDecodeError:
                self._json_data = None
        else:
            raise TypeError(f"Unsupported content type: {type(content)}")

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def content(self) -> bytes:
        return self._content

    @property
    def text(self) -> str:
        return self._text

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def encoding(self) -> str:
        """The encoding used for text decoding."""
        return self._encoding

    @property
    def elapsed(self) -> timedelta:
        """The simulated time elapsed for the request."""
        return self._elapsed

    def json(self) -> Any:
        if self._json_data is None:
            try:
                self._json_data = json.loads(self._text)
                return self._json_data
            except json.JSONDecodeError:
                raise ValueError("Response content is not valid JSON")
        return self._json_data

    def raise_for_status(self) -> None:
        import requests

        if 400 <= self._status_code < 600:
            # Create a simple error message
            error_msg = f"HTTP error {self._status_code}"

            # Raise HTTPError directly without trying to set response attributes
            raise requests.HTTPError(error_msg)


# StubClient moved to stubs_client.py
# StubCrud moved to stubs_crud.py
# StubAPI moved to stubs_api.py
