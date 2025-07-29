"""Standalone helper functions for verifying interactions with ``EnhancedSpyBase`` spies."""

from typing import Any, Dict, List

from .enhanced import EnhancedSpyBase


def verify_call_sequence(spy: EnhancedSpyBase, *method_names: str) -> None:
    """Verify that the given methods were called in the exact sequence provided."""
    calls = spy.get_calls()
    if len(calls) < len(method_names):
        raise AssertionError("Not enough calls recorded for sequence verification")

    call_methods = [call.method_name for call in calls]
    for i, method_name in enumerate(method_names):
        if call_methods[i] != method_name:
            raise AssertionError(f"Expected call {i} to be '{method_name}', got '{call_methods[i]}'")


def verify_no_unexpected_calls(spy: EnhancedSpyBase, expected_methods: List[str]) -> None:
    """Verify that only ``expected_methods`` were called on ``spy``."""
    for call in spy.get_calls():
        if call.method_name not in expected_methods:
            raise AssertionError(f"Unexpected method call: {call.method_name}")


def verify_call_timing(spy: EnhancedSpyBase, method_name: str, max_duration: float) -> None:
    """Verify that all calls to ``method_name`` completed within ``max_duration`` seconds."""
    calls = spy.get_calls(method_name)
    if not calls:
        raise AssertionError(f"Method {method_name} was not called")

    for call in calls:
        if call.duration is not None and call.duration > max_duration:
            raise AssertionError(f"Call to {method_name} took {call.duration:.6f}s which exceeds {max_duration:.6f}s")


def verify_call_arguments(spy: EnhancedSpyBase, method_name: str, expected_args: Dict[str, Any]) -> None:
    """Verify that at least one call to ``method_name`` matches ``expected_args``."""
    calls = spy.get_calls(method_name)
    if not calls:
        raise AssertionError(f"Method {method_name} was not called")

    for call in calls:
        params: Dict[str, Any] = {f"arg{i}": arg for i, arg in enumerate(call.args)}
        params.update(call.kwargs)
        if all(params.get(k) == v for k, v in expected_args.items()):
            return

    raise AssertionError(f"No call to {method_name} matched expected arguments {expected_args}")
