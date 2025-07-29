"""Combined mock implementation for all CRUD operations."""

import re
from typing import Any, Dict, List, Optional, cast

from crudclient.testing.types import ResponseBody

from .create import CreateMock
from .delete import DeleteMock
from .read import ReadMock
from .request_record import RequestRecord
from .update import UpdateMock


class CombinedCrudMock:
    """Unified interface exposing create, read, update and delete mocks."""

    def __init__(self) -> None:
        """Create individual mocks and initialise shared request history."""
        self.create_mock = CreateMock()
        self.read_mock = ReadMock()
        self.update_mock = UpdateMock()
        self.delete_mock = DeleteMock()
        self.request_history: List[RequestRecord] = []
        self._parent_id_handling = True

    def get(self, url: str, **kwargs: Any) -> ResponseBody:
        """Delegate GET requests to the ``ReadMock``."""
        result = cast(ResponseBody, self.read_mock.get(url, **kwargs))
        self.request_history.extend(self.read_mock.request_history)
        return result

    def post(self, url: str, **kwargs: Any) -> ResponseBody:
        """Delegate POST requests to the ``CreateMock``."""
        result = cast(ResponseBody, self.create_mock.post(url, **kwargs))
        self.request_history.extend(self.create_mock.request_history)  # type: ignore[arg-type]
        return result

    def put(self, url: str, **kwargs: Any) -> ResponseBody:
        """Delegate PUT requests to the ``UpdateMock``."""
        result = cast(ResponseBody, self.update_mock.put(url, **kwargs))
        self.request_history.extend(self.update_mock.request_history)  # type: ignore[arg-type]
        return result

    def patch(self, url: str, **kwargs: Any) -> ResponseBody:
        """Delegate PATCH requests to the ``UpdateMock``."""
        result = cast(ResponseBody, self.update_mock.patch(url, **kwargs))
        self.request_history.extend(self.update_mock.request_history)  # type: ignore[arg-type]
        return result

    def delete(self, url: str, **kwargs: Any) -> ResponseBody:
        """Delegate DELETE requests to the ``DeleteMock``."""
        result = cast(ResponseBody, self.delete_mock.delete(url, **kwargs))
        self.request_history.extend(self.delete_mock.request_history)  # type: ignore[arg-type]
        return result

    def with_parent_id_handling(self, enabled: bool = True) -> "CombinedCrudMock":
        """Enable or disable ``parent_id`` handling for all mocks."""
        self._parent_id_handling = enabled
        self.create_mock.with_parent_id_handling(enabled)
        self.read_mock.with_parent_id_handling(enabled)
        self.update_mock.with_parent_id_handling(enabled)
        self.delete_mock.with_parent_id_handling(enabled)
        return self

    def verify_request_count(self, count: int, url_pattern: Optional[str] = None) -> None:
        """Assert that a certain number of requests were made."""
        matching_requests = self.request_history
        if url_pattern:
            pattern = re.compile(url_pattern)
            matching_requests = [r for r in matching_requests if pattern.search(r.url)]

        actual_count = len(matching_requests)
        assert actual_count == count, f"Expected {count} matching requests, but found {actual_count}. " f"Filter: url_pattern={url_pattern}"

    def verify_request_sequence(self, sequence: List[Dict[str, Any]], strict: bool = False) -> None:
        """Assert that requests were made in a specific order."""
        if not sequence:
            return

        if strict and len(sequence) != len(self.request_history):
            raise AssertionError(f"Expected {len(sequence)} requests, but found {len(self.request_history)}")

        # Find subsequence match
        history_idx = 0
        sequence_idx = 0

        while history_idx < len(self.request_history) and sequence_idx < len(sequence):
            request = self.request_history[history_idx]
            matcher = sequence[sequence_idx]

            method_match = True
            if "method" in matcher:
                method_match = request.method == matcher["method"].upper()

            url_match = True
            if "url_pattern" in matcher:
                url_match = bool(re.search(matcher["url_pattern"], request.url))

            if method_match and url_match:
                sequence_idx += 1

            history_idx += 1

        if sequence_idx < len(sequence):
            raise AssertionError(f"Request sequence not found. Matched {sequence_idx} of {len(sequence)} expected requests.")

    def verify_crud_operation_sequence(self, operations: List[str], resource_id: Optional[str] = None, url_pattern: Optional[str] = None) -> None:
        """Assert that CRUD operations were performed in the given order."""
        # Map operation names to HTTP methods
        method_map = {"create": "POST", "read": "GET", "update": "PUT", "partial_update": "PATCH", "delete": "DELETE"}

        # Build sequence matchers
        sequence = []
        for op in operations:
            matcher = {"method": method_map.get(op, op.upper())}
            if url_pattern:
                matcher["url_pattern"] = url_pattern
            if resource_id and op != "create":
                # For non-create operations, include resource_id in the URL pattern
                if "url_pattern" in matcher:
                    matcher["url_pattern"] = f"{matcher['url_pattern']}.*{resource_id}"
                else:
                    matcher["url_pattern"] = f".*{resource_id}"
            sequence.append(matcher)

        self.verify_request_sequence(sequence)
