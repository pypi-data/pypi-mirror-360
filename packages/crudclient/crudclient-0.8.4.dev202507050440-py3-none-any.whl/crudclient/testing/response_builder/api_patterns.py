"""
API pattern builder utilities for mock client.

This module provides utilities for creating mock responses that follow common API patterns,
such as REST resources, nested resources, batch operations, GraphQL endpoints, and OAuth flows.
"""

from typing import Any, Callable, Dict, List, Optional, TypedDict, Union

from .response import MockResponse


class PatternDict(TypedDict, total=False):
    """TypedDict for response pattern dictionaries."""

    method: str
    url_pattern: str
    response: Union[Dict[str, Any], List[Dict[str, Any]], Callable[..., MockResponse]]
    params_matcher: Callable[[Optional[Dict[str, str]]], bool]
    json_matcher: Callable[[Optional[Dict[str, Any]]], bool]


class APIPatternBuilder:
    """
    Builder for creating mock responses that follow common API patterns.

    This class provides static methods for generating response patterns that match
    common API design patterns, making it easier to create realistic mock APIs
    for testing client code.
    """

    @staticmethod
    def rest_resource(
        base_path: str,
        resource_id_pattern: str = r"\d+",
        list_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        get_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        create_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        update_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        delete_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        search_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        filter_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        patch_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[PatternDict]:
        """
        Create response patterns for a standard REST resource.

        This method generates response patterns for standard REST operations
        (list, get, create, update, delete) on a resource, as well as search
        and filter operations.

        Args:
            base_path: The base URL path for the resource (e.g., "users")
            resource_id_pattern: Regex pattern to match resource IDs in URLs
            list_response: Response for GET requests to the collection (list operation)
            get_response: Response for GET requests to a specific resource
            create_response: Response for POST requests to the collection (create operation)
            update_response: Response for PUT requests to a specific resource
            delete_response: Response for DELETE requests to a specific resource
            search_response: Response for GET requests with a search parameter
            filter_response: Response for GET requests with filter parameters
            patch_response: Response for PATCH requests to a specific resource

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        patterns = []

        # Ensure base_path starts with / and doesn't end with /
        base_path = f"/{base_path.strip('/')}"

        # GET collection (list)
        if list_response is not None:
            patterns.append(PatternDict(method="GET", url_pattern=f"{base_path}$", response=list_response))

        # GET resource (read)
        if get_response is not None:
            patterns.append(PatternDict(method="GET", url_pattern=f"{base_path}/{resource_id_pattern}$", response=get_response))

        # POST collection (create)
        if create_response is not None:
            patterns.append(PatternDict(method="POST", url_pattern=f"{base_path}$", response=create_response))

        # PUT resource (update)
        if update_response is not None:
            patterns.append(PatternDict(method="PUT", url_pattern=f"{base_path}/{resource_id_pattern}$", response=update_response))

        # PATCH resource (partial update)
        if patch_response is not None:
            patterns.append(PatternDict(method="PATCH", url_pattern=f"{base_path}/{resource_id_pattern}$", response=patch_response))

        # DELETE resource (delete)
        if delete_response is not None:
            patterns.append(PatternDict(method="DELETE", url_pattern=f"{base_path}/{resource_id_pattern}$", response=delete_response))

        # GET collection with search (search)
        if search_response is not None:
            # Define a properly typed matcher function for search params
            def search_params_matcher(params: Optional[Dict[str, str]]) -> bool:
                return bool(params and "search" in params)

            patterns.append(
                PatternDict(
                    method="GET",
                    url_pattern=f"{base_path}$",
                    params_matcher=search_params_matcher,
                    response=search_response,
                )
            )

        # GET collection with filters (filter)
        if filter_response is not None:
            # Define a properly typed matcher function for filter params
            def filter_params_matcher(params: Optional[Dict[str, str]]) -> bool:
                return bool(params and any(key != "search" and key != "page" and key != "limit" for key in params.keys()))

            patterns.append(
                PatternDict(
                    method="GET",
                    url_pattern=f"{base_path}$",
                    params_matcher=filter_params_matcher,
                    response=filter_response,
                )
            )

        return patterns

    @staticmethod
    def nested_resource(
        parent_path: str,
        child_path: str,
        parent_id_pattern: str = r"\d+",
        child_id_pattern: str = r"\d+",
        list_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        get_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        create_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        update_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        delete_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[PatternDict]:
        """
        Create response patterns for a nested resource.

        This method generates response patterns for operations on a resource that is
        nested under a parent resource (e.g., /users/{user_id}/posts/{post_id}).

        Args:
            parent_path: The path of the parent resource (e.g., "users")
            child_path: The path of the child resource (e.g., "posts")
            parent_id_pattern: Regex pattern to match parent resource IDs
            child_id_pattern: Regex pattern to match child resource IDs
            list_response: Response for GET requests to the child collection
            get_response: Response for GET requests to a specific child resource
            create_response: Response for POST requests to the child collection
            update_response: Response for PUT requests to a specific child resource
            delete_response: Response for DELETE requests to a specific child resource

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        patterns = []

        # Ensure paths are properly formatted
        parent_path = parent_path.strip("/")
        child_path = child_path.strip("/")
        base_path = f"/{parent_path}/{parent_id_pattern}/{child_path}"

        # GET child collection (list)
        if list_response is not None:
            patterns.append(PatternDict(method="GET", url_pattern=f"{base_path}$", response=list_response))

        # GET child resource (read)
        if get_response is not None:
            patterns.append(PatternDict(method="GET", url_pattern=f"{base_path}/{child_id_pattern}$", response=get_response))

        # POST child collection (create)
        if create_response is not None:
            patterns.append(PatternDict(method="POST", url_pattern=f"{base_path}$", response=create_response))

        # PUT child resource (update)
        if update_response is not None:
            patterns.append(PatternDict(method="PUT", url_pattern=f"{base_path}/{child_id_pattern}$", response=update_response))

        # DELETE child resource (delete)
        if delete_response is not None:
            patterns.append(PatternDict(method="DELETE", url_pattern=f"{base_path}/{child_id_pattern}$", response=delete_response))

        return patterns

    @staticmethod
    def batch_operations(
        base_path: str,
        batch_create_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        batch_update_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        batch_delete_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[PatternDict]:
        """
        Create response patterns for batch operations.

        This method generates response patterns for batch operations (create, update, delete)
        on a resource, which are commonly used for bulk operations.

        Args:
            base_path: The base URL path for the resource (e.g., "users")
            batch_create_response: Response for batch create operations
            batch_update_response: Response for batch update operations
            batch_delete_response: Response for batch delete operations

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        patterns = []

        # Ensure base_path starts with / and doesn't end with /
        base_path = f"/{base_path.strip('/')}"
        batch_path = f"{base_path}/batch"

        # POST batch create
        if batch_create_response is not None:
            patterns.append(PatternDict(method="POST", url_pattern=f"{batch_path}/create$", response=batch_create_response))

        # PUT/PATCH batch update
        if batch_update_response is not None:
            patterns.append(PatternDict(method="PUT", url_pattern=f"{batch_path}/update$", response=batch_update_response))
            patterns.append(PatternDict(method="PATCH", url_pattern=f"{batch_path}/update$", response=batch_update_response))

        # DELETE batch delete
        if batch_delete_response is not None:
            patterns.append(
                PatternDict(
                    method="POST",  # Often POST with IDs in body for batch delete
                    url_pattern=f"{batch_path}/delete$",
                    response=batch_delete_response,
                )
            )

        return patterns

    @staticmethod
    def graphql_endpoint(
        url_pattern: str = r"/graphql$",
        query_matchers: Optional[Dict[str, Union[Dict[str, Any], Callable[..., MockResponse]]]] = None,
        default_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[PatternDict]:
        """
        Create response patterns for a GraphQL endpoint.

        This method generates response patterns for a GraphQL endpoint, with support
        for matching specific queries and providing appropriate responses.

        Args:
            url_pattern: Regex pattern to match the GraphQL endpoint URL
            query_matchers: Dictionary mapping query patterns to responses
            default_response: Default response for queries that don't match any pattern

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        patterns = []

        # Add patterns for specific queries
        if query_matchers:
            for query_pattern, response in query_matchers.items():
                # Define a properly typed matcher function
                def create_matcher(pattern: str) -> Callable[[Optional[Dict[str, Any]]], bool]:
                    def matcher(json_data: Optional[Dict[str, Any]]) -> bool:
                        return bool(isinstance(json_data, dict) and "query" in json_data and pattern in json_data.get("query", ""))

                    return matcher

                patterns.append(
                    PatternDict(
                        method="POST",
                        url_pattern=url_pattern,
                        json_matcher=create_matcher(query_pattern),
                        response=response,
                    )
                )

        # Add default response for unmatched queries
        if default_response is not None:
            patterns.append(PatternDict(method="POST", url_pattern=url_pattern, response=default_response))

        return patterns

    @staticmethod
    def oauth_flow(
        token_url_pattern: str = r"/oauth/token$",
        success_response: Optional[Dict[str, Any]] = None,
        error_response: Optional[Dict[str, Any]] = None,
        valid_credentials: Optional[Dict[str, str]] = None,
    ) -> List[PatternDict]:
        """
        Create response patterns for an OAuth token endpoint.

        This method generates response patterns for an OAuth token endpoint,
        with support for validating credentials and returning appropriate
        success or error responses.

        Args:
            token_url_pattern: Regex pattern to match the token endpoint URL
            success_response: Response to return for valid credentials
            error_response: Response to return for invalid credentials
            valid_credentials: Dictionary of valid credentials to check against

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        if success_response is None:
            success_response = {
                "access_token": "mock-access-token",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "mock-refresh-token",
                "scope": "read write",
            }

        if error_response is None:
            error_response = {"error": "invalid_grant", "error_description": "Invalid credentials"}

        if valid_credentials is None:
            valid_credentials = {"client_id": "valid-client-id", "client_secret": "valid-client-secret"}

        def token_response_factory(**kwargs: Any) -> MockResponse:
            data: Dict[str, Any] = kwargs.get("data", {})

            # Check if credentials match
            for key, value in valid_credentials.items():
                if key not in data or data[key] != value:
                    return MockResponse(status_code=401, json_data=error_response)

            return MockResponse(status_code=200, json_data=success_response)

        patterns = [PatternDict(method="POST", url_pattern=token_url_pattern, response=token_response_factory)]

        return patterns
