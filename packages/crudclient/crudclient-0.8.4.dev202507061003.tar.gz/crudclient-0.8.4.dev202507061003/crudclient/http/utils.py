import logging
from typing import Any, Dict, Mapping

from apiconfig.utils.redaction.body import redact_body
from apiconfig.utils.redaction.headers import redact_headers

# Set up logging
logger = logging.getLogger(__name__)


# --- Header Redaction ---
def redact_sensitive_headers(headers: Mapping[str, str]) -> Dict[str, str]:
    """Return ``headers`` with sensitive values redacted."""

    return redact_headers(headers)


# --- End Header Redaction ---


# --- Body Redaction ---
def redact_json_body(data: Any) -> Any:
    """Return ``data`` with sensitive values redacted."""

    return redact_body(data)


# --- End Body Redaction ---
