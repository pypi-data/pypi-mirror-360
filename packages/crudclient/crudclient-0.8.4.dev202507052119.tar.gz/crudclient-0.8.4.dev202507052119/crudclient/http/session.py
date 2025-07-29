"""
Module `session.py`
==================

This module defines the SessionManager class, which is responsible for managing HTTP sessions
and their lifecycle. It handles session creation, configuration, authentication, and cleanup.

Class `SessionManager`
---------------------

The `SessionManager` class provides a centralized way to manage HTTP sessions for API clients.
It includes methods for setting up authentication, configuring retries and timeouts, and
cleaning up resources when the session is no longer needed.

To use the SessionManager:
    1. Create a ClientConfig object with the necessary configuration.
    2. Initialize a SessionManager instance with the config.
    3. Use the SessionManager to manage the HTTP session lifecycle.

Example:
    config = ClientConfig(hostname="https://api.example.com", api_key="your_api_key")
    session_manager = SessionManager(config)
    session = session_manager.session
    # Use the session for making requests
    session_manager.close()  # Clean up when done

Classes:
    - SessionManager: Main class for managing HTTP sessions.
"""

# mypy: disable-error-code="unreachable"

import logging
from typing import Dict

import requests
from requests.adapters import HTTPAdapter

from ..config import ClientConfig

# Set up logging
logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages HTTP sessions and their lifecycle.

    This class is responsible for creating, configuring, and cleaning up HTTP sessions.
    It handles authentication, retries, timeouts, and other session parameters.

    Attributes:
        config (ClientConfig): Configuration object for the session.
        session (requests.Session): The HTTP session managed by this instance.
        timeout (float): The timeout for requests in seconds.
    """

    config: ClientConfig
    session: requests.Session
    timeout: float

    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize the SessionManager with a configuration.

        Args:
            config (ClientConfig): Configuration for the session.

        Raises:
            TypeError: If the provided config is not a ClientConfig object.
        """
        if not isinstance(config, ClientConfig):
            raise TypeError("config must be a ClientConfig object")

        self.config = config
        self.session = requests.Session()
        self.is_closed = False

        # Set up authentication
        self._setup_auth()

        # Set up default headers, if any
        if self.config.headers:
            self.session.headers.update(self.config.headers)

        # Set up retries and timeouts
        self._setup_retries_and_timeouts()

    def _setup_auth(self) -> None:
        """
        Set up authentication for the requests session.

        This method configures the session with the appropriate authentication headers
        based on the authentication strategy defined in the config.

        It first tries to use the new auth strategy approach, and if that's not available,
        falls back to the old auth method for backward compatibility.
        """
        self.config.prepare()

        # Try the new auth strategy first
        if hasattr(self.config, "auth_strategy") and self.config.auth_strategy is not None:
            # Use duck typing instead of isinstance to support both crudclient and apiconfig auth strategies
            if hasattr(self.config.auth_strategy, "prepare_request_headers"):
                logger.debug("Applying authentication using %s", type(self.config.auth_strategy).__name__)
                auth_headers = self.config.get_auth_headers()
                if auth_headers:
                    self.session.headers.update(auth_headers)
                return

        # Fall back to the old auth method for backward compatibility
        # This handles the case where auth() is overridden in a subclass
        # Check if the config class has an auth method (old style)
        if hasattr(self.config, "auth") and callable(getattr(self.config, "auth")):
            auth = self.config.auth()
            if auth is not None:
                if isinstance(auth, dict):
                    logger.debug("Applying authentication via direct header dictionary")
                    self.session.headers.update(auth)
                elif isinstance(auth, tuple) and len(auth) == 2:
                    logger.debug("Applying authentication via session.auth tuple")
                    self.session.auth = auth
                elif callable(auth):
                    logger.debug("Applying authentication via callable: %s", type(auth).__name__)
                    auth(self.session)

    def _setup_retries_and_timeouts(self) -> None:
        """
        Set up retries and timeouts for the requests session.

        This method configures the session with the appropriate retry and timeout settings
        based on the configuration. It creates an HTTPAdapter with the specified number of
        retries and mounts it to both 'http://' and 'https://' URLs in the session.

        It also sets the timeout duration for the session.
        """
        retries = self.config.retries or 3
        timeout = self.config.timeout or 5

        adapter = HTTPAdapter(max_retries=retries)

        # Mount the adapter to both 'http://' and 'https://' URLs in the session
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set the timeout duration for the session
        self.timeout = timeout

    def update_headers(self, headers: Dict[str, str]) -> None:
        """
        Update the session headers with the provided headers.

        Args:
            headers (Dict[str, str]): Headers to add to the session.

        Raises:
            TypeError: If headers is not a dictionary.
        """
        # Runtime type check
        if not isinstance(headers, dict):
            raise TypeError(f"headers must be a dictionary, got {type(headers).__name__}")
        if headers:
            self.session.headers.update(headers)

    def set_content_type(self, content_type: str) -> None:
        """
        Set the Content-Type header for the session.

        Args:
            content_type (str): The content type to set.

        Raises:
            TypeError: If content_type is not a string.
        """
        # Runtime type check
        if not isinstance(content_type, str):
            raise TypeError(f"content_type must be a string, got {type(content_type).__name__}")
        self.session.headers["Content-Type"] = content_type

    def refresh_auth(self) -> None:
        """
        Refresh the authentication for the session.

        This method can be called when authentication needs to be refreshed,
        such as after a token expires.
        """
        self._setup_auth()

    def close(self) -> None:
        """
        Close the HTTP session and clean up resources.

        This method should be called when the session is no longer needed
        to ensure proper cleanup of resources.
        """
        self.session.close()
        self.is_closed = True
        logger.debug("Session closed.")
