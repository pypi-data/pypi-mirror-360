"""
Module `crud`.

This module defines the Crud class, which provides a generic implementation of CRUD
(Create, Read, Update, Delete) operations for API resources. It supports both top-level
and nested resources, and can be easily extended for specific API endpoints.
"""

from .base import Crud, CrudInstance, CrudType, HttpMethodString, T

__all__ = ["Crud", "HttpMethodString", "CrudInstance", "CrudType", "T"]
