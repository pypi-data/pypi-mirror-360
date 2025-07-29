# crudclient/testing/factory_helpers.py

from typing import Any, Dict, List, Union

from crudclient.testing.auth import (
    ApiKeyAuthMock,
    BasicAuthMock,
    BearerAuthMock,
    CustomAuthMock,
    OAuthMock,
)
from crudclient.testing.core.client import MockClient
from crudclient.testing.response_builder.api_patterns import (
    APIPatternBuilder,
    PatternDict,
)


def _create_api_patterns(api_type: str, **kwargs: Any) -> List[PatternDict]:
    """
    Create API response patterns based on the specified API type and configuration.

    Args:
        api_type: The type of API to create patterns for ('rest', 'oauth').
        **kwargs: Additional configuration parameters specific to the API type.
            For 'rest': 'api_resources' dictionary with resource configurations.
            For 'oauth': 'oauth_config' dictionary with OAuth flow configuration.

    Returns:
        A list of API pattern dictionaries that can be used to configure mock responses.
    """
    patterns: List[PatternDict] = []

    if api_type.lower() == "rest":
        # Create patterns for REST resources
        resources = kwargs.get("api_resources", {})
        for resource_name, resource_config in resources.items():
            resource_patterns = APIPatternBuilder.rest_resource(
                base_path=resource_config.get("base_path", resource_name),
                resource_id_pattern=resource_config.get("id_pattern", r"\d+"),
                list_response=resource_config.get("list_response"),
                get_response=resource_config.get("get_response"),
                create_response=resource_config.get("create_response"),
                update_response=resource_config.get("update_response"),
                delete_response=resource_config.get("delete_response"),
                search_response=resource_config.get("search_response"),
                filter_response=resource_config.get("filter_response"),
                patch_response=resource_config.get("patch_response"),
            )
            patterns.extend(resource_patterns)

            # Add batch operations if configured
            if resource_config.get("batch_operations"):
                batch_config = resource_config.get("batch_operations", {})
                batch_patterns = APIPatternBuilder.batch_operations(
                    base_path=resource_config.get("base_path", resource_name),
                    batch_create_response=batch_config.get("create_response"),
                    batch_update_response=batch_config.get("update_response"),
                    batch_delete_response=batch_config.get("delete_response"),
                )
                patterns.extend(batch_patterns)

            # Add nested resources if configured
            nested_resources = resource_config.get("nested_resources", {})
            for nested_name, nested_config in nested_resources.items():
                nested_patterns = APIPatternBuilder.nested_resource(
                    parent_path=resource_config.get("base_path", resource_name),
                    child_path=nested_config.get("base_path", nested_name),
                    parent_id_pattern=resource_config.get("id_pattern", r"\d+"),
                    child_id_pattern=nested_config.get("id_pattern", r"\d+"),
                    list_response=nested_config.get("list_response"),
                    get_response=nested_config.get("get_response"),
                    create_response=nested_config.get("create_response"),
                    update_response=nested_config.get("update_response"),
                    delete_response=nested_config.get("delete_response"),
                )
                patterns.extend(nested_patterns)

    # Removed GraphQL section as requested

    elif api_type.lower() == "oauth":
        # Create patterns for OAuth flow
        oauth_config = kwargs.get("oauth_config", {})
        oauth_patterns = APIPatternBuilder.oauth_flow(
            token_url_pattern=oauth_config.get("token_url_pattern", r"/oauth/token$"),
            success_response=oauth_config.get("success_response"),
            error_response=oauth_config.get("error_response"),
            valid_credentials=oauth_config.get("valid_credentials"),
        )
        patterns.extend(oauth_patterns)

    return patterns


def _add_error_responses(client: MockClient, error_configs: Dict[str, Any]) -> None:
    """
    Add common error responses to a MockClient instance.

    Configures the client with predefined error responses for validation errors,
    rate limiting, and authentication failures based on the provided configurations.

    Args:
        client: The MockClient instance to configure.
        error_configs: Dictionary containing error configuration settings.
            Supported keys: 'validation', 'rate_limit', 'auth'.
    """
    # Add validation error response
    if "validation" in error_configs:
        config = error_configs["validation"]
        validation_error_data = {
            "error": {
                "code": config.get("error_code", "VALIDATION_ERROR"),
                "message": config.get("message", "Validation failed"),
                "fields": config.get("fields", {"field": "Invalid value"}),
            }
        }
        client.configure_response(
            method=config.get("method", "POST"),
            path=config.get("url_pattern", r".*"),
            status_code=config.get("status_code", 422),
            data=validation_error_data,
            headers={"Content-Type": "application/json"},
        )

    # Add rate limit error response
    if "rate_limit" in error_configs:
        config = error_configs["rate_limit"]
        rate_limit_data = {"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded. Please try again later."}}
        rate_limit_headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(config.get("limit", 100)),
            "X-RateLimit-Remaining": str(config.get("remaining", 0)),
            "X-RateLimit-Reset": str(config.get("reset_seconds", 60)),
        }
        client.configure_response(
            method=config.get("method", "GET"),
            path=config.get("url_pattern", r".*"),
            status_code=429,
            data=rate_limit_data,
            headers=rate_limit_headers,
        )

    # Add authentication error response
    if "auth" in error_configs:
        config = error_configs["auth"]
        error_type = config.get("error_type", "invalid_token")
        error_messages = {
            "invalid_token": "The access token is invalid or has expired",
            "invalid_credentials": "Invalid username or password",
            "missing_credentials": "Authentication credentials were not provided",
            "insufficient_scope": "The access token does not have the required scope",
            "mfa_required": "Multi-factor authentication is required",
        }
        message = error_messages.get(error_type, "Authentication failed")
        auth_error_data = {"error": {"code": error_type.upper(), "message": message}}
        auth_headers = {"Content-Type": "application/json", "WWW-Authenticate": f'Bearer error="{error_type}", error_description="{message}"'}
        client.configure_response(
            method=config.get("method", "GET"),
            path=config.get("url_pattern", r".*"),
            status_code=config.get("status_code", 401),
            data=auth_error_data,
            headers=auth_headers,
        )


def _configure_auth_mock(auth_mock: Union[BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock, OAuthMock], config: Dict[str, Any]) -> None:
    """
    Configure an authentication mock with various settings.

    Sets up authentication behavior including failure scenarios, token expiration,
    refresh tokens, MFA requirements, and custom headers/parameters.

    Args:
        auth_mock: The authentication mock instance to configure.
        config: Dictionary containing configuration settings for the auth mock.
    """
    # Configure failure behavior
    if config.get("should_fail", False):
        auth_mock.with_failure(
            failure_type=config.get("failure_type", "invalid_token"),
            status_code=config.get("status_code", 401),
            message=config.get("message", "Authentication failed"),
        )

    # Configure token expiration
    if "expires_in_seconds" in config:
        auth_mock.with_token_expiration(expires_in_seconds=config["expires_in_seconds"])

    # Configure expired token
    if config.get("token_expired", False):
        auth_mock.with_expired_token()

    # Configure refresh token
    if "refresh_token" in config:
        auth_mock.with_refresh_token(refresh_token=config["refresh_token"])

    # Configure expired refresh token
    if config.get("refresh_token_expired", False):
        auth_mock.with_expired_refresh_token()

    # Configure MFA
    if config.get("mfa_required", False):
        auth_mock.with_mfa_required(verified=config.get("mfa_verified", False))

    # Configure failure after X requests
    if "fail_after_requests" in config:
        auth_mock.fail_after(request_count=config["fail_after_requests"])

    # Configure custom headers
    custom_headers = config.get("custom_headers", {})
    for name, value in custom_headers.items():
        auth_mock.with_custom_header(name, value)

    # Configure custom params
    custom_params = config.get("custom_params", {})
    for name, value in custom_params.items():
        auth_mock.with_custom_param(name, value)
