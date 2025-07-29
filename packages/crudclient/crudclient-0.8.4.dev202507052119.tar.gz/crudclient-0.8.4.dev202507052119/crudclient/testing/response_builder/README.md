# `crudclient.testing.response_builder`

## Overview

This module provides a suite of tools for constructing mock HTTP responses (`MockResponse`) specifically designed for testing API clients built with or interacting like `crudclient`. It allows developers to simulate various API behaviors, including different data structures, common API patterns (REST, pagination, errors), data generation, relationship management, and request validation logic.

The primary goal is to enable the creation of realistic and predictable responses for different test scenarios without needing a live API backend.

## Core Components

The module is composed of several builders and utility classes:

1.  **`MockResponse` (`response.py`)**
    *   A simple data class representing a simulated HTTP response. It holds attributes like `status_code`, `json_data`, `text`, and `headers`. This is the object type returned by the various builders.

2.  **`BasicResponseBuilder` (`basic.py`)**
    *   Provides foundational methods (`create_response`, `created`, `no_content`) for constructing `MockResponse` objects.
    *   Establishes a standard structure for JSON responses, often including top-level keys like `data`, `metadata`, `links`, and `errors`.
    *   Handles basic HTTP status codes (e.g., 200, 201, 204) and content types (JSON vs. raw text/bytes).

3.  **`DataGenerationBuilder` (`data_generation.py`)**
    *   A utility to generate random, structured data based on a provided schema dictionary.
    *   Supports various primitive types (string, int, float, bool, email, URL, date, UUID, etc.), nested objects, and arrays.
    *   Useful for populating mock responses with realistic-looking data payloads.

4.  **`APIPatternBuilder` (`api_patterns.py`)**
    *   A helper class to generate configurations for common API architectural patterns.
    *   Includes methods for standard REST resources (`rest_resource`), nested resources (`nested_resource`), batch operations (`batch_operations`), GraphQL endpoints (`graphql_endpoint`), and OAuth flows (`oauth_flow`).
    *   These methods typically return lists of dictionaries defining route patterns (method, URL regex, matchers) and their corresponding responses, simplifying the setup of mock API behavior.

5.  **`EntityRelationshipBuilder` (`entity_relationships.py`)**
    *   Provides tools for managing relationships within mock data.
    *   `create_related_entities`: Links a primary entity with related ones (embedding full objects or just IDs).
    *   `create_entity_graph`: Builds a graph of interconnected entities based on defined relationship rules (cardinality, embedding).
    *   `create_consistent_response_sequence`: Generates stateful response *factories* for simulating CRUD operations (list, get, create, update, delete) on a dataset, ensuring consistency across sequential calls (e.g., a deleted item won't appear in a subsequent list).

6.  **`ErrorResponseBuilder` (`error.py`)**
    *   A specialized builder for creating standardized `MockResponse` objects representing various error conditions.
    *   Includes methods for generic errors (`create_error_response`), validation errors (`create_validation_error`), rate limit errors (`create_rate_limit_error`), and authentication/authorization errors (`create_auth_error`).
    *   Automatically includes relevant HTTP headers (e.g., `Retry-After`, `X-RateLimit-*`, `WWW-Authenticate`).

7.  **`PaginationResponseBuilder` (`pagination.py`)**
    *   Dedicated builder for creating paginated list responses (`create_paginated_response`).
    *   Takes a list of items and pagination parameters (page, per_page, totals).
    *   Calculates the items for the current page, generates pagination metadata, and optionally includes HATEOAS-style navigation links (`self`, `first`, `last`, `prev`, `next`).

8.  **`ResponsePattern` (`patterns.py`)**
    *   Represents the core request-matching rule. An instance holds the HTTP method, a compiled URL regex, optional matchers for request parameters, data/JSON body, and headers.
    *   Each pattern is associated with a response, which can be a static `MockResponse` or a callable function that generates one dynamically.
    *   Supports features like limiting the number of times a pattern can be matched and adding custom condition functions for complex matching logic. This class is likely used internally by mock client implementations to determine which response to return.

9.  **Validation (`validation.py`, `validators.py`)**
    *   `ValidationErrorBuilder`: Creates mock error responses for schema-level validation failures (e.g., invalid field format, missing fields). Supports different error formatting styles (standard, JSON:API).
    *   `BusinessLogicConstraintBuilder`: Creates mock error responses for violations of business rules or data integrity (e.g., unique constraints, foreign key issues, invalid state transitions).
    *   Validator Factories (`create_field_validator`, `create_data_validator`, `create_business_rule_validator`): Generate functions that take request data and apply validation rules. These functions return `None` if the data is valid or a `MockResponse` containing the specific error if invalid.
    *   `validators.py`: Provides a collection of common, reusable validation functions (e.g., `required_field`, `min_length`, `max_value`, `pattern_match`, `is_email`, `is_date`) used by the validator factories.

## Usage Concept

These components are designed to be used together to build mock API interactions for testing:

1.  Define the structure and patterns of your mock API, potentially using `APIPatternBuilder` to generate configurations for standard routes.
2.  For each route or pattern, determine the response needed.
3.  Use `DataGenerationBuilder` to create sample data if required.
4.  Use `BasicResponseBuilder`, `PaginationResponseBuilder`, `ErrorResponseBuilder`, or other builders to construct the `MockResponse` object with the desired status code, headers, and body (containing generated data, error details, or pagination info).
5.  For complex scenarios involving related data or state changes across requests, use `EntityRelationshipBuilder`.
6.  To simulate request validation, use the validator factories from `validation.py` along with functions from `validators.py` to create checks that return appropriate error responses generated by `ValidationErrorBuilder` or `BusinessLogicConstraintBuilder`.
7.  These patterns and responses are typically registered with a mock client or adapter, which uses the logic (likely based on `ResponsePattern`) to match incoming test requests and return the corresponding `MockResponse`.

## Basic Example

```python
from crudclient.testing.response_builder.basic import BasicResponseBuilder
from crudclient.testing.response_builder.data_generation import DataGenerationBuilder

# Define a simple schema for a user
user_schema = {
    "id": "uuid",
    "name": "name",
    "email": "email",
    "created_at": "datetime"
}

# Generate some random user data
random_user_data = DataGenerationBuilder.create_random_data(user_schema)

# Create a basic 200 OK response using the generated data
mock_response = BasicResponseBuilder.create_response(
    status_code=200,
    data=random_user_data
)

# mock_response can now be used in a test setup to simulate
# a successful API call returning user data.
# print(mock_response.status_code)  # Output: 200
# print(mock_response.json())
# Output: {'data': {'id': '...', 'name': '...', 'email': '...', 'created_at': '...'}}