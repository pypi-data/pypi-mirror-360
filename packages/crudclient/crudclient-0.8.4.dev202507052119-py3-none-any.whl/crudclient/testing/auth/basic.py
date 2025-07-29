"""
Basic authentication mock for testing.

This module provides a mock implementation of Basic authentication
for testing API clients with username/password authentication.
"""

import base64
import re
from typing import TYPE_CHECKING, List, Optional, Pattern, Tuple

from apiconfig.testing.auth_verification import AuthHeaderVerification

from crudclient.auth import AuthStrategy, BasicAuth
from crudclient.exceptions import AuthenticationError

from .auth_extraction_utils import AuthExtractionUtils
from .base import AuthMockBase

if TYPE_CHECKING:
    from ..response_builder import MockResponse


class BasicAuthMock(AuthMockBase):
    """
    Mock implementation of Basic authentication.

    This class provides a configurable mock for Basic authentication,
    supporting username/password validation, pattern matching, and
    various authentication scenarios.
    """

    username: str
    password: str
    auth_strategy: BasicAuth
    valid_credentials: List[Tuple[str, str]]
    username_pattern: Optional[Pattern]
    password_pattern: Optional[Pattern]
    password_min_length: Optional[int]
    password_complexity: bool
    case_sensitive: bool
    max_attempts: Optional[int]
    current_attempts: int

    def __init__(self, username: str = "user", password: str = "pass"):
        """
        Initialize a BasicAuthMock instance.

        Args:
            username: Initial username
            password: Initial password
        """
        super().__init__()
        self.username = username
        self.password = password
        self.auth_strategy = BasicAuth(username=username, password=password)
        self.valid_credentials = [(username, password)]
        self.username_pattern = None
        self.password_pattern = None
        self.password_min_length = None
        self.password_complexity = False
        self.case_sensitive = True
        self.max_attempts = None
        self.current_attempts = 0

    def with_credentials(self, username: str, password: str) -> "BasicAuthMock":
        """
        Configure the mock with specific credentials.

        Args:
            username: Username
            password: Password

        Returns:
            Self for method chaining
        """
        self.username = username
        self.password = password
        self.auth_strategy = BasicAuth(username=username, password=password)
        self.valid_credentials = [(username, password)]
        return self

    def with_additional_valid_credentials(self, username: str, password: str) -> "BasicAuthMock":
        """
        Add additional valid credentials.

        Args:
            username: Additional valid username
            password: Additional valid password

        Returns:
            Self for method chaining
        """
        self.valid_credentials.append((username, password))
        return self

    def with_username_pattern(self, pattern: str) -> "BasicAuthMock":
        """
        Configure the mock with username pattern validation.

        Args:
            pattern: Regular expression pattern for valid usernames

        Returns:
            Self for method chaining
        """
        self.username_pattern = re.compile(pattern)
        return self

    def with_password_requirements(self, min_length: Optional[int] = None, complexity: bool = False) -> "BasicAuthMock":
        """
        Configure the mock with password requirements.

        Args:
            min_length: Minimum password length
            complexity: Whether to enforce password complexity rules

        Returns:
            Self for method chaining
        """
        self.password_min_length = min_length
        self.password_complexity = complexity
        return self

    def with_case_insensitive_username(self) -> "BasicAuthMock":
        """
        Configure the mock to use case-insensitive username matching.

        Returns:
            Self for method chaining
        """
        self.case_sensitive = False
        return self

    def with_max_attempts(self, max_attempts: int) -> "BasicAuthMock":
        """
        Configure the mock with a maximum number of authentication attempts.

        Args:
            max_attempts: Maximum number of authentication attempts

        Returns:
            Self for method chaining
        """
        self.max_attempts = max_attempts
        self.current_attempts = 0
        return self

    def verify_auth_header(self, header_value: str) -> bool:
        """Verify that the authentication header has the correct format."""
        try:
            AuthHeaderVerification.verify_basic_auth_header(header_value)
            username, password = AuthExtractionUtils.extract_basic_auth_credentials(header_value)
        except (AuthenticationError, ValueError):
            return False

        return self.validate_credentials(username, password)

    def validate_credentials(self, username: str, password: str) -> bool:
        """
        Validate a set of credentials.

        Args:
            username: Username to validate
            password: Password to validate

        Returns:
            True if the credentials are valid, False otherwise
        """
        # Track authentication attempts if max_attempts is set
        if self.max_attempts is not None:
            self.current_attempts += 1
            if self.current_attempts > self.max_attempts:
                return False

        # Check username pattern if configured
        if self.username_pattern and not self.username_pattern.match(username):
            return False

        # Check password requirements if configured
        if self.password_min_length is not None and len(password) < self.password_min_length:
            return False

        # Check password complexity if required
        if self.password_complexity:
            # Simple complexity check: must contain at least one uppercase, one lowercase,
            # one digit, and one special character
            if not (
                re.search(r"[A-Z]", password)
                and re.search(r"[a-z]", password)
                and re.search(r"[0-9]", password)
                and re.search(r"[^A-Za-z0-9]", password)
            ):
                return False

        # Check against valid credentials
        for valid_username, valid_password in self.valid_credentials:
            if self.case_sensitive:
                username_match = username == valid_username
            else:
                username_match = username.lower() == valid_username.lower()

            if username_match and password == valid_password:
                self.current_attempts = 0  # Reset on success
                return True

        return False

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers.

        Returns:
            Tuple of (header_name, header_value) or None if no credentials are available
        """
        if not self.username or self.password is None:
            # Should ideally not happen due to __init__ defaults
            return None
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return ("Authorization", f"Basic {encoded_credentials}")

    def handle_auth_error(self, response: "MockResponse") -> bool:
        """
        Handle an authentication error.

        Args:
            response: Mock response with authentication error

        Returns:
            True if the error was handled successfully, False otherwise
        """
        # Basic auth typically fails outright, no refresh mechanism
        return False

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the underlying authentication strategy.

        Returns:
            BasicAuth instance
        """
        return self.auth_strategy

    def reset_attempts(self) -> "BasicAuthMock":
        """
        Reset the authentication attempt counter.

        Returns:
            Self for method chaining
        """
        self.current_attempts = 0
        return self
