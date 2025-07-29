"""Network condition simulation for testing.

This module provides utilities for simulating various network conditions in
tests, such as latency, packet loss, and errors. These simulations help test the
robustness of code that makes network requests.
"""

import random
import time
from typing import Callable, Optional

import requests


class NetworkCondition:
    """Simulates various network conditions for testing.

    This class allows tests to simulate realistic network conditions like
    latency, packet loss, and errors. It can be used with mock HTTP clients to
    test how code handles different network scenarios without requiring actual
    network infrastructure.

    Example:
        ```python
        # Create a network condition with 100ms latency and 5% packet loss
        network = NetworkCondition(latency_ms=100, packet_loss_percentage=5.0)

        # Use in a request flow
        if not network.should_drop_packet():
            network.apply_latency()
            if network.should_raise_error():
                raise network.error_factory()
            # Process the request normally
        ```
    """

    def __init__(
        self,
        latency_ms: int = 0,
        packet_loss_percentage: float = 0.0,
        error_rate_percentage: float = 0.0,
        error_factory: Optional[Callable[[], Exception]] = None,
    ):
        """Initialize network condition simulator.

        Args:
            latency_ms: Simulated latency in milliseconds. Defaults to 0.
            packet_loss_percentage: Percentage of requests that will be dropped (0-100).
                Defaults to 0.0.
            error_rate_percentage: Percentage of requests that will raise errors (0-100).
                Defaults to 0.0.
            error_factory: Function to create network errors. If not provided, a default
                function that returns a ``requests.ConnectionError`` is used.
        """

        self.latency_ms = latency_ms
        self.packet_loss_percentage = min(100.0, max(0.0, packet_loss_percentage))
        self.error_rate_percentage = min(100.0, max(0.0, error_rate_percentage))
        self.error_factory = error_factory or (lambda: requests.ConnectionError("Simulated network error"))

    def should_drop_packet(self) -> bool:
        """Determine if a packet should be dropped based on the packet loss percentage.

        This method uses random sampling to determine if a request should be
        simulated as dropped (never reaching its destination).

        Returns:
            True if the packet should be dropped, False otherwise.
        """

        return random.random() * 100 < self.packet_loss_percentage

    def should_raise_error(self) -> bool:
        """Determine if an error should be raised based on the error rate percentage.

        This method uses random sampling to determine if a request should
        result in a network error.

        Returns:
            True if an error should be raised, False otherwise.
        """

        return random.random() * 100 < self.error_rate_percentage

    def apply_latency(self) -> None:
        """Apply the configured latency by sleeping.

        This method simulates network latency by pausing execution
        for the configured amount of time.
        """

        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)
