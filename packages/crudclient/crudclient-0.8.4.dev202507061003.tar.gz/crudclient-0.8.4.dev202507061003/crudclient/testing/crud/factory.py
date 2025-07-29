"""
Factory for creating CRUD mock objects.

This module provides a factory class for creating various types of CRUD mock objects,
making it easier to set up test environments with different CRUD operation mocks.
"""

from .combined import CombinedCrudMock
from .create import CreateMock
from .delete import DeleteMock
from .read import ReadMock
from .update import UpdateMock


class CrudMockFactory:
    """
    Factory for creating CRUD mock objects.

    This factory provides static methods for creating different types of CRUD mock objects,
    including individual operation mocks (create, read, update, delete) and a combined mock
    that supports all operations.
    """

    @staticmethod
    def create() -> CreateMock:
        """
        Create a mock for create operations.

        Returns:
            A new CreateMock instance configured for testing create operations.
        """
        return CreateMock()

    @staticmethod
    def read() -> ReadMock:
        """
        Create a mock for read operations.

        Returns:
            A new ReadMock instance configured for testing read operations.
        """
        return ReadMock()

    @staticmethod
    def update() -> UpdateMock:
        """
        Create a mock for update operations.

        Returns:
            A new UpdateMock instance configured for testing update operations.
        """
        return UpdateMock()

    @staticmethod
    def delete() -> DeleteMock:
        """
        Create a mock for delete operations.

        Returns:
            A new DeleteMock instance configured for testing delete operations.
        """
        return DeleteMock()

    @staticmethod
    def combined() -> CombinedCrudMock:
        """
        Create a combined mock supporting all CRUD operations.

        Returns:
            A new CombinedCrudMock instance configured for testing all CRUD operations.
        """
        return CombinedCrudMock()
