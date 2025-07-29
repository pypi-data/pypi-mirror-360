"""
Module `config.py`.

Defines the `ClientConfig` base class used for configuring API clients.
"""

import logging
from typing import Any, Dict, Optional

from apiconfig.config.base import ClientConfig as _ApiConfigClientConfig
from apiconfig.exceptions.config import MissingConfigError

# Import AuthStrategy from crudclient for type hints
from crudclient.auth import AuthStrategy

# Set up logging
logger = logging.getLogger(__name__)


class ClientConfig(_ApiConfigClientConfig):
    """
    Configuration class for crudclient API clients.

    Extends apiconfig's ClientConfig with crudclient-specific functionality
    including 403 retry hooks and legacy authentication support.

    Attributes
    ----------
    api_key : Optional[str]
        Legacy credential for authentication.
    auth_type : str
        Legacy auth type ("bearer", "basic", etc).
    """

    # Override apiconfig defaults to require explicit hostname configuration
    hostname: Optional[str] = None
    api_key: Optional[str] = None
    auth_type: str = "bearer"

    def __init__(
        self,
        hostname: Optional[str] = None,
        version: Optional[str] = None,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        auth_strategy: Optional[AuthStrategy] = None,
        auth_type: Optional[str] = None,
        log_request_body: Optional[bool] = None,
        log_response_body: Optional[bool] = None,
    ) -> None:
        """
        Initialize configuration with crudclient-specific extensions.

        Parameters
        ----------
        hostname : Optional[str], optional
            Base hostname of the API.
        version : Optional[str], optional
            API version string.
        api_key : Optional[str], optional
            Legacy authentication credential.
        headers : Optional[Dict[str, str]], optional
            Default headers for requests.
        timeout : Optional[float], optional
            Request timeout in seconds.
        retries : Optional[int], optional
            Number of retry attempts.
        auth_strategy : Optional[AuthStrategy], optional
            Authentication strategy instance.
        auth_type : Optional[str], optional
            Legacy auth type (default: "bearer").
        log_request_body : Optional[bool], optional
            Flag to enable request body logging.
        log_response_body : Optional[bool], optional
            Flag to enable response body logging.
        """
        super().__init__(
            hostname=hostname,
            version=version,
            headers=headers,
            timeout=timeout,
            retries=retries,
            auth_strategy=auth_strategy,
            log_request_body=log_request_body,
            log_response_body=log_response_body,
        )

        self.api_key = api_key or self.__class__.api_key
        self.auth_type = auth_type or self.__class__.auth_type

    def enable_rate_limiter(
        self,
        state_path: Optional[str] = None,
        buffer: int = 10,
        track_delays: bool = False,
        buffer_time: float = 1.0,
    ) -> "ClientConfig":
        """
        Enable rate limiting for this configuration.

        .. warning::
            **EXPERIMENTAL FEATURE**: The rate limiting functionality is experimental
            and may change in future releases. Use with caution in production environments.

            Known limitations:
            - Only supports Tripletex API headers currently
            - Cross-process coordination via file locks may have edge cases
            - State persistence format may change between versions

        Parameters
        ----------
        state_path : Optional[str], optional
            Directory to store rate limiter state files.
            If None, uses system cache directory.
        buffer : int, optional
            Buffer size for rate limit threshold calculation.
            Added to detected worker count.
        track_delays : bool, optional
            Whether to track rate limiting delays for testing.
        buffer_time : float, optional
            Time buffer in seconds to add when waiting (default: 1.0).
            Can be reduced for faster tests.

        Returns
        -------
        ClientConfig
            Self for method chaining.
        """
        self._rate_limiter_enabled = True
        self._rate_limiter_state_path = state_path
        self._rate_limiter_buffer = buffer
        self._rate_limiter_track_delays = track_delays
        self._rate_limiter_buffer_time = buffer_time
        return self

    @property
    def base_url(self) -> str:
        """
        Override to maintain crudclient's ValueError for backward compatibility.

        This is a trivial change to keep the same exception type.

        Returns
        -------
        str
            The base URL of the API.

        Raises
        ------
        ValueError
            If the hostname is not configured.
        """
        try:
            return super().base_url
        except MissingConfigError as e:
            logger.error("Hostname is required")
            raise ValueError("hostname is required") from e

    def get_auth_token(self) -> Optional[str]:
        """
        Return the raw authentication token or credential.

        Returns
        -------
        Optional[str]
            Token or credential used for authentication.
        """
        return self.api_key

    def get_auth_header_name(self) -> str:
        """
        Return the name of the HTTP header used for authentication.

        Returns
        -------
        str
            Name of the header (default: "Authorization").
        """
        return "Authorization"

    def prepare(self) -> None:
        """
        Implement pre-request setup logic.

        Override in subclasses to implement setup steps such as refreshing tokens,
        validating credentials, or preparing session context.

        This method is called once at client startup.
        """

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Build authentication headers for requests.

        If an AuthStrategy is set, uses it to prepare request headers.
        Otherwise, returns an empty dictionary.

        Returns
        -------
        Dict[str, str]
            Headers to include in requests.
        """
        if self.auth_strategy:
            return self.auth_strategy.prepare_request_headers()
        return {}

    def auth(self) -> Dict[str, str]:
        """
        Legacy method for backward compatibility.

        Returns authentication headers based on the auth_type and token.
        New code should use the AuthStrategy pattern instead.

        Returns
        -------
        Dict[str, str]
            Authentication headers.
        """
        if isinstance(self.auth_strategy, AuthStrategy):
            return self.get_auth_headers()

        token = self.get_auth_token()
        if not token:
            return {}

        header_name = self.get_auth_header_name()

        if self.auth_type == "basic":
            return {header_name: f"Basic {token}"}
        elif self.auth_type == "bearer":
            return {header_name: f"Bearer {token}"}
        else:
            return {header_name: token}

    def should_retry_on_403(self) -> bool:
        """
        Indicate whether the client should retry once after a 403 Forbidden response.

        Override in subclasses to enable fallback retry logic, typically used in APIs
        where sessions or tokens may expire and require refresh.

        Returns
        -------
        bool
            True to enable 403 retry, False by default.
        """
        return False

    def handle_403_retry(self, client: Any) -> None:
        """
        Handle 403 response fallback logic (e.g., token/session refresh).

        Called once when a 403 response is received and `should_retry_on_403()` returns True.
        The method may update headers, refresh tokens, or mutate session state.

        Parameters
        ----------
        client : Any
            Reference to the API client instance making the request.
        """

    def create_auth_strategy(self) -> Optional[AuthStrategy]:
        """
        Create the authentication strategy.

        Overrides the parent method to ensure proper auth strategy creation
        with legacy support.

        Returns
        -------
        Optional[AuthStrategy]
            AuthStrategy instance if authentication is configured, None otherwise.
        """
        if self.auth_strategy:
            return self.auth_strategy

        if self.api_key:
            from crudclient.auth import create_auth_strategy

            return create_auth_strategy(
                auth_type=self.auth_type,
                token=self.api_key,
            )

        return None

    def get_config_errors(self) -> Dict[str, str]:
        """
        Get configuration validation errors.

        Returns
        -------
        Dict[str, str]
            Dict of field names to error messages.
        """
        errors: Dict[str, str] = {}

        # Check if hostname is None or empty, or if it's the default value from apiconfig
        if not self.hostname or self.hostname == "api.example.com":
            errors["hostname"] = "hostname is required"

        return errors
