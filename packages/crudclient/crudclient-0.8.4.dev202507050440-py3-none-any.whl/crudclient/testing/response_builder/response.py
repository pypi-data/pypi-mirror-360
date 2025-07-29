from typing import Dict, Optional, Union


class MockResponse:
    """
    A mock object simulating an HTTP response, typically from libraries like requests or httpx.

    Used in testing scenarios to provide controlled response data without making actual network calls.
    """

    error: Optional[Exception] = None

    def __init__(
        self,
        status_code: int,
        json_data: Optional[Dict] = None,
        text: Optional[Union[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initializes the MockResponse.

        Args:
            status_code: The HTTP status code for the mock response.
            json_data: A dictionary representing the JSON body of the response.
            text: A string representing the raw text body of the response.
            headers: A dictionary representing the response headers.
        """
        self.status_code = status_code
        self.json_data = json_data
        self.text = text
        self.headers = headers if headers is not None else {}
        self.error = None

    def json(self) -> Optional[Dict]:
        """Returns the JSON data provided during initialization."""
        return self.json_data
