"""
This module provides logging utilities for HTTP requests and responses.

It includes a `HttpLifecycleLogger` class that handles logging of request and response
details, including bodies and headers, with sensitive information redaction.
"""

import json as json_lib
import logging
import time
from typing import Any, Dict, Optional, Union

import requests
from requests.structures import CaseInsensitiveDict

from ..config import ClientConfig
from .utils import redact_json_body, redact_sensitive_headers

_BODY_LOG_TRUNCATION_LIMIT = 1024


class HttpLifecycleLogger:
    """Handles logging for the HTTP request/response lifecycle."""

    config: ClientConfig
    logger: logging.Logger

    def __init__(self, config: ClientConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger

    def log_request_body_content(self, kwargs: Dict[str, Any]) -> None:
        """Log the content of the request body, redacting if necessary."""
        body_to_log: Optional[str] = None
        content_type = kwargs.get("headers", {}).get("Content-Type", "").lower()
        content_type_display = content_type or "unknown"
        is_json = "application/json" in content_type

        if is_json and "json" in kwargs and kwargs["json"] is not None:
            try:
                original_body = kwargs["json"]
                redacted_body = redact_json_body(original_body)
                body_to_log = json_lib.dumps(redacted_body)
                content_type_display = "application/json (redacted)"
            except Exception as e:
                self.logger.warning(f"Failed to redact/serialize JSON request body for logging: {e}", exc_info=True)
                try:
                    body_to_log = str(kwargs["json"])
                    content_type_display = "application/json (raw fallback)"
                except Exception:
                    body_to_log = "[Unloggable JSON Body]"
                    content_type_display = "application/json (unloggable)"

        elif "data" in kwargs and kwargs["data"] is not None:
            try:
                body_to_log = str(kwargs["data"])
                content_type_display = content_type if content_type and not is_json else "unknown (from data)"
            except Exception:
                body_to_log = "[Unloggable Data Body]"
                content_type_display = content_type if content_type and not is_json else "unknown (unloggable)"

        if body_to_log is not None:
            truncated_indicator = ""
            if len(body_to_log) > _BODY_LOG_TRUNCATION_LIMIT:
                body_snippet = body_to_log[:_BODY_LOG_TRUNCATION_LIMIT]
                truncated_indicator = "... (truncated)"
            else:
                body_snippet = body_to_log
            self.logger.debug(f"Request body ({content_type_display}{truncated_indicator}): {body_snippet}")
        else:
            self.logger.debug("Request body logging enabled but body is empty or not logged (no 'json' or 'data').")

    def log_response_body_content(self, response: requests.Response) -> None:
        """Log the content of the response body, redacting if necessary."""
        try:
            body_text = response.text
            if not body_text:
                self.logger.debug("Response body logging enabled but body is empty.")
                return

            content_type = response.headers.get("Content-Type", "").lower()
            body_to_log: Optional[str] = None
            log_content_type_display = content_type or "unknown"

            if content_type.startswith("application/json"):
                try:
                    parsed_body = json_lib.loads(body_text)
                    redacted_body = redact_json_body(parsed_body)
                    body_to_log = json_lib.dumps(redacted_body)
                    log_content_type_display = "application/json (redacted)"
                except json_lib.JSONDecodeError as json_err:
                    self.logger.warning(f"Failed to parse JSON response body for redaction: {json_err}")
                    body_to_log = body_text
                    log_content_type_display = "application/json (parse error, raw)"
                except Exception as e:
                    self.logger.warning(f"Error during response body redaction/serialization: {e}", exc_info=True)
                    body_to_log = body_text
                    log_content_type_display = "application/json (redaction error, raw)"
            else:
                body_to_log = body_text

            if body_to_log is not None:
                truncated_indicator = ""
                if len(body_to_log) > _BODY_LOG_TRUNCATION_LIMIT:
                    body_snippet = body_to_log[:_BODY_LOG_TRUNCATION_LIMIT]
                    truncated_indicator = "... (truncated)"
                else:
                    body_snippet = body_to_log
                self.logger.debug(f"Response body ({log_content_type_display}{truncated_indicator}): {body_snippet}")

        except Exception as e:
            self.logger.warning(f"Could not access or log response body due to error: {e}", exc_info=True)

    def log_response_details(self, method: str, url: str, response: requests.Response) -> None:
        """Log details about the received HTTP response."""
        self.logger.debug("Received response for %s %s: Status %d", method, url, response.status_code)
        if response.status_code in (401, 403):
            self.logger.warning("Authentication failed for %s %s: Status %d", method, url, response.status_code)
        elif 400 <= response.status_code < 500:
            self.logger.warning("Client error for %s %s: Status %d", method, url, response.status_code)
        elif response.status_code >= 500:
            self.logger.error("Server error for %s %s: Status %d", method, url, response.status_code)

        # Ensure headers is a dictionary-like object for redaction
        headers_to_log = response.headers
        if not isinstance(headers_to_log, (dict, CaseInsensitiveDict)):
            # Convert if necessary, though response.headers usually is CaseInsensitiveDict
            headers_to_log = dict(headers_to_log)  # type: ignore

        self.logger.debug("Response Headers: %s", redact_sensitive_headers(headers_to_log))

        if self.config.log_response_body:
            self.log_response_body_content(response)
        else:
            self.logger.debug("Response body logging is disabled.")

    def log_request_details(self, method: str, url: str, kwargs: Dict[str, Any]) -> None:
        """Log details about the outgoing HTTP request."""
        params = kwargs.get("params")
        if params:
            self.logger.debug("Sending request: %s %s Params: %s", method, url, params)
        else:
            self.logger.debug("Sending request: %s %s", method, url)

        # Ensure headers is a dictionary-like object for redaction
        headers_to_log = kwargs.get("headers", {})
        if not isinstance(headers_to_log, (dict, CaseInsensitiveDict)):
            headers_to_log = dict(headers_to_log)

        self.logger.debug("Request Headers: %s", redact_sensitive_headers(headers_to_log))

        if self.config.log_request_body:
            self.log_request_body_content(kwargs)
        else:
            self.logger.debug("Request body logging is disabled.")

    def log_request_completion(
        self,
        start_time: float,
        method: str,
        url: str,
        attempt_count: int,
        final_outcome: Union[requests.Response, Exception, None],
    ) -> None:
        """Log the final outcome and duration of an HTTP request."""
        end_time = time.monotonic()
        duration_ms = int((end_time - start_time) * 1000)
        if isinstance(final_outcome, requests.Response):
            response = final_outcome
            if response.ok:
                self.logger.info(
                    "Request %s %s completed successfully: %d %s in %dms.", method, url, response.status_code, response.reason, duration_ms
                )
            else:
                self.logger.info(
                    "Request %s %s failed after %d attempts: %d %s in %dms.",
                    method,
                    url,
                    attempt_count,
                    response.status_code,
                    response.reason,
                    duration_ms,
                )
        elif isinstance(final_outcome, Exception):
            self.logger.info(
                "Request %s %s failed after %d attempts: %s in %dms.", method, url, attempt_count, type(final_outcome).__name__, duration_ms
            )
        elif final_outcome is None:
            self.logger.warning("Request %s %s completed with no outcome recorded in %dms.", method, url, duration_ms)

    def log_http_error(
        self,
        e: requests.exceptions.HTTPError,
        method: Optional[str] = None,  # Method might not be available if request is None
        url: Optional[str] = None,  # URL might not be available if request is None
    ) -> None:
        """Log details about an HTTPError."""
        response = e.response
        request = e.request

        # Try to get method/url from request if not provided directly
        req_method = method or (request.method if request else "UNKNOWN_METHOD")
        req_url = url or (request.url if request else "UNKNOWN_URL")

        if response is not None:
            log_level = logging.WARNING if 400 <= response.status_code < 500 else logging.ERROR
            try:
                response_snippet = response.text[:_BODY_LOG_TRUNCATION_LIMIT] + ("..." if len(response.text) > _BODY_LOG_TRUNCATION_LIMIT else "")
            except Exception:
                response_snippet = "[Could not read response text]"

            self.logger.log(
                log_level, "HTTP error encountered for %s %s: Status %d - Response: %s", req_method, req_url, response.status_code, response_snippet
            )
        else:
            # Log even if response is None
            self.logger.error("HTTPError occurred without a response object for %s %s: %s", req_method, req_url, e)
