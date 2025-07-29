"""
Retry Module for CrudClient
===========================

This module provides retry functionality for the CrudClient library.
It contains classes and functions for managing retry policies and backoff strategies.

Classes:
    - RetryHandler: Manages retry policies and backoff strategies.
    - RetryStrategy: Base class for retry strategies.
    - FixedRetryStrategy: Implements a fixed delay retry strategy.
    - ExponentialBackoffStrategy: Implements an exponential backoff retry strategy.
"""

import logging
import time
from enum import Enum
from typing import Callable, List, Optional, Tuple, Union

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from ..exceptions import CrudClientError, NetworkError
from .retry_conditions import RetryCondition
from .retry_strategies import ExponentialBackoffStrategy, RetryStrategy

logger = logging.getLogger(__name__)


class RetryEvent(Enum):
    """Enum representing different retry events."""

    FORBIDDEN = 403
    UNAUTHORIZED = 401
    SERVER_ERROR = 500
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    CUSTOM = "custom"


class RetryHandler:
    """Handles the logic for retrying HTTP requests based on configured conditions."""

    max_retries: int
    retry_strategy: RetryStrategy
    retry_conditions: List[RetryCondition]
    on_retry_callback: Optional[Callable[[int, float, Optional[requests.Response], Optional[Exception]], None]]

    def __init__(
        self,
        max_retries: int = 3,
        retry_strategy: Optional[RetryStrategy] = None,
        retry_conditions: Optional[List[RetryCondition]] = None,
        on_retry_callback: Optional[Callable[[int, float, Optional[requests.Response], Optional[Exception]], None]] = None,
    ) -> None:
        """Initializes the RetryHandler.

        Args:
            max_retries: Maximum number of retry attempts (0 means no retries).
            retry_strategy: The strategy for calculating delays between retries.
                            Defaults to ExponentialBackoffStrategy.
            retry_conditions: A list of conditions that trigger a retry.
                              Defaults to retrying on common server errors (500, 502, 503, 504)
                              and network errors (Timeout, ConnectionError).
            on_retry_callback: An optional function called before each retry attempt.
                               It receives (attempt, delay, last_response, last_exception).

        Raises:
            ValueError: If max_retries is negative.
            TypeError: If retry_strategy, retry_conditions, or on_retry_callback have incorrect types.
        """
        if not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer")
        if retry_strategy is not None and not isinstance(retry_strategy, RetryStrategy):
            raise TypeError("retry_strategy must be an instance of RetryStrategy or None")
        if retry_conditions is not None and not isinstance(retry_conditions, list):
            raise TypeError("retry_conditions must be a list of RetryCondition objects or None")
        if retry_conditions and not all(isinstance(c, RetryCondition) for c in retry_conditions):
            raise TypeError("All items in retry_conditions must be RetryCondition objects")
        if on_retry_callback is not None and not callable(on_retry_callback):
            raise TypeError("on_retry_callback must be callable or None")

        self.max_retries = max_retries
        self.retry_strategy = retry_strategy or ExponentialBackoffStrategy()
        self.on_retry_callback = on_retry_callback

        if retry_conditions is None:
            self.retry_conditions = [
                RetryCondition(
                    status_codes=[500, 502, 503, 504],
                    exceptions=[Timeout, ConnectionError],
                )
            ]
        else:
            self.retry_conditions = retry_conditions if isinstance(retry_conditions, list) else [retry_conditions]

    def should_retry(self, attempt: int, response: Optional[requests.Response] = None, exception: Optional[Exception] = None) -> bool:
        """
        Determine whether a request should be retried.

        Args:
            attempt (int): The current retry attempt number (0-based).
            response (Optional[requests.Response]): The response from the request, if any.
            exception (Optional[Exception]): The exception raised by the request, if any.

        Returns:
            bool: True if the request should be retried, False otherwise.
        """
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")

        # Removed redundant isinstance checks for response and exception,
        # as type hints Optional[requests.Response] and Optional[Exception]
        # already cover this for mypy.

        if attempt >= self.max_retries:
            logger.debug(f"Max retries ({self.max_retries}) reached. Not retrying.")
            return False

        for condition in self.retry_conditions:
            if condition.should_retry(response=response, exception=exception):
                logger.debug(f"Retry condition matched by {condition}. Will retry.")
                return True

        return False

    def get_delay(self, attempt: int) -> float:
        """
        Calculate the delay before the next retry attempt.

        Args:
            attempt (int): The current retry attempt number (1-based).

        Returns:
            float: The delay in seconds before the next retry.
        """
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")

        if attempt < 1:
            raise ValueError(f"attempt must be a positive integer, got {attempt}")
        return self.retry_strategy.get_delay(attempt)

    def _execute_request(
        self,
        request_func: Callable[[], requests.Response],
        method: str,
        url: str,
        attempt: int,
    ) -> Tuple[Optional[requests.Response], Optional[Exception]]:
        """Executes the request function and handles exceptions."""
        # Implementation moved from docstring
        try:
            response = request_func()
            return response, None
        except RequestException as e:
            logger.error(
                "Network error during request %s %s (attempt %d/%d): %s - %s", method.upper(), url, attempt, self.max_retries + 1, type(e).__name__, e
            )
            return None, e
        except Exception as e:
            logger.exception(
                "Unexpected error during request function execution for %s %s (attempt %d/%d)", method.upper(), url, attempt, self.max_retries + 1
            )
            # Re-raise unexpected errors immediately
            raise e

    def _handle_response(
        self,
        response: Optional[requests.Response],
        exception: Optional[Exception],
        attempt: int,
        method: str,
        url: str,
    ) -> Tuple[Optional[requests.Response], bool]:
        """Processes the response or exception, determining if retry is needed."""
        # Implementation moved from docstring
        if exception:
            # Handle RequestException
            if isinstance(exception, RequestException):
                should_retry_flag = self.should_retry(attempt - 1, response=None, exception=exception)
                if not should_retry_flag or attempt > self.max_retries:
                    logger.error(
                        f"Not retrying {method.upper()} {url} after exception {type(exception).__name__} on attempt {attempt}. "
                        f"Retry flag: {should_retry_flag}, Max retries: {self.max_retries}"
                    )
                    raise NetworkError(
                        message=f"Request failed after {attempt} attempts due to network error: {exception}",
                        original_exception=exception,
                    )
                return None, True  # Retry needed
            else:
                # Unexpected exception already logged, re-raised by _execute_request
                # This path shouldn't be hit if _execute_request raises correctly.
                raise exception  # Should not happen

        # Handle Response
        if response is not None:
            if response.ok:
                logger.debug(f"Request {method.upper()} {url} successful on attempt {attempt} with status {response.status_code}")
                return response, False  # No retry needed, success

            # Non-OK response
            logger.warning(f"Request {method.upper()} {url} received non-OK status {response.status_code} on attempt {attempt}")
            should_retry_flag = self.should_retry(attempt - 1, response=response, exception=None)
            if not should_retry_flag or attempt > self.max_retries:
                logger.warning(
                    f"Not retrying {method.upper()} {url} after status {response.status_code} on attempt {attempt}. "
                    f"Retry flag: {should_retry_flag}, Max retries: {self.max_retries}"
                )
                return response, False  # No retry needed, return non-OK response
            return response, True  # Retry needed

        # Should not happen if response or exception is always present
        raise CrudClientError("Internal error: No response or exception received from request execution.")

    def _perform_retry_delay_and_callbacks(
        self,
        attempt: int,
        last_response: Optional[requests.Response],
        last_exception: Optional[Exception],
        setup_auth_func: Optional[Callable[[], None]],
        method: str,
        url: str,
    ) -> None:
        """Calculates delay, sleeps, and calls callbacks before the next retry."""
        # Implementation moved from docstring
        delay = self.get_delay(attempt)

        if self.on_retry_callback:
            try:
                self.on_retry_callback(attempt, delay, last_response, last_exception)
            except Exception as cb_exc:
                logger.exception(f"Error in on_retry_callback during attempt {attempt}: {cb_exc}")

        reason = "unknown condition"
        if last_exception:
            reason = f"exception '{type(last_exception).__name__}'"
        elif last_response is not None:
            reason = f"status code {last_response.status_code}"

        logger.info(
            "Retrying request %s %s (attempt %d/%d) in %.2fs due to %s.", method.upper(), url, attempt + 1, self.max_retries + 1, delay, reason
        )

        # Attempt auth refresh on 401 before sleeping
        if setup_auth_func and last_response is not None and last_response.status_code == 401:
            logger.info("Attempting to refresh authentication before retry %d due to status 401", attempt + 1)
            try:
                setup_auth_func()
                logger.info("Authentication refreshed successfully.")
            except Exception as auth_exc:
                logger.exception(f"Failed to refresh authentication during retry attempt {attempt + 1}: {auth_exc}")
                # Decide if auth failure should prevent retry? Currently, it doesn't.

        time.sleep(delay)

    def execute_with_retry(
        self,
        method: str,
        url: str,
        request_func: Callable[[], requests.Response],
        session: Optional[requests.Session] = None,  # session is passed to request_func closure, not directly used here
        setup_auth_func: Optional[Callable[[], None]] = None,
    ) -> Tuple[Union[requests.Response, Exception], int]:
        """Executes a request function with retry logic.

        Handles retries based on configured conditions and strategy. Logs errors
        and raises NetworkError if retries are exhausted due to network issues.
        Returns the final response or caught exception along with the attempt count.

        Args:
            method: The HTTP method (for logging).
            url: The request URL (for logging).
            request_func: The function that executes the actual HTTP request.
            session: The requests.Session object (optional, for context).
            setup_auth_func: An optional function to refresh authentication,
                             typically called on 401 errors before retrying.

        Returns:
            A tuple containing:
            - The final `requests.Response` on success or retryable non-OK status.
            - The caught `Exception` if the request function failed unexpectedly
              (and was not retryable or retries exhausted).
            - The total number of attempts made (including the final one).

        Raises:
            NetworkError: If a `requests.RequestException` occurs and retries are
                          exhausted or the exception is not configured for retry.
            TypeError: If `request_func` or `setup_auth_func` are not callable.
        """
        if not callable(request_func):
            raise TypeError(f"request_func must be callable, got {type(request_func).__name__}")
        if setup_auth_func is not None and not callable(setup_auth_func):
            raise TypeError(f"setup_auth_func must be callable or None, got {type(setup_auth_func).__name__}")
        # session validation removed as it's not directly used

        attempt = 0
        last_exception: Optional[Exception] = None
        last_response: Optional[requests.Response] = None

        while True:
            attempt += 1
            response, exception = self._execute_request(request_func, method, url, attempt)
            last_response, last_exception = response, exception

            final_result, retry_needed = self._handle_response(response, exception, attempt, method, url)

            if not retry_needed:
                # Return successful response or non-retried error response/exception
                if isinstance(final_result, requests.Response):
                    return final_result, attempt
                # If _handle_response raises NetworkError, it propagates out.
                # If _handle_response returns a non-OK response without retry, final_result is that response.
                # The case where final_result is an Exception other than NetworkError shouldn't occur here.
                else:  # Safeguard for unexpected state
                    raise CrudClientError(f"Request failed after {attempt} attempts, but final state is unclear.")

            # If retry is needed, perform delay and callbacks
            self._perform_retry_delay_and_callbacks(
                attempt=attempt, last_response=last_response, last_exception=last_exception, setup_auth_func=setup_auth_func, method=method, url=url
            )
        # The loop should only exit via return or exception.
