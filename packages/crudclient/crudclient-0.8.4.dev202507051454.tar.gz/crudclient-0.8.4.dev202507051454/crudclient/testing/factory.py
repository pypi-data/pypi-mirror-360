"""
Factory Pattern Implementation for Mock Client Creation.

This module utilizes the **Factory pattern** to provide a centralized and
flexible way to create and configure various mock client instances
(`MockClient`) needed for testing different scenarios. It encapsulates the
complex setup logic behind simple creation methods.

Key Components:
* `MockClientFactory`: A class implementing Factory Methods (`create`,
  `from_client_config`, etc.) to produce configured `MockClient` instances.
"""

# Re-export the factory class from its dedicated module
from .mock_client_factory import MockClientFactory

# Make linters happy about unused imports
__all__ = ["MockClientFactory"]
