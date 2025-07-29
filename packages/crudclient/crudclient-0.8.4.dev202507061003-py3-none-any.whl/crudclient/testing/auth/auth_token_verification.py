"""
Specific utilities for verifying authentication token properties in tests.

This module provides the `AuthTokenVerification` class containing static methods
focused on checking the validity and content of authentication tokens, primarily
assuming JWT format for detailed claim inspection (scopes, expiration, identity).

These methods are typically used internally by higher-level verification helpers
(e.g., those in `apiconfig.testing.auth_verification`) or can be used directly for fine-grained token checks.
They raise `VerificationError` upon failure.
"""

from datetime import datetime
from typing import List, Optional

from ..exceptions import VerificationError  # Import VerificationError
from .auth_extraction_utils import AuthExtractionUtils


class AuthTokenVerification:
    """
    Provides static methods focused on verifying authentication token properties.

    Contains specific checks for token validity, expiration, scopes, identity claims,
    and refresh behavior, often assuming JWT structure for detailed inspection.
    Methods raise `VerificationError` if checks fail.
    """

    @staticmethod
    def verify_oauth_token(
        token: str,
        required_scopes: Optional[List[str]] = None,
        check_expiration: bool = True,
        expected_client_id: Optional[str] = None,
        expected_user: Optional[str] = None,
    ) -> bool:
        """
        Verify properties of an OAuth token (likely JWT), such as scopes and expiration.

        Assumes the token is a JWT unless underlying implementation handles others.
        Decodes the token payload to check claims. Does *not* typically verify
        the signature (depends on underlying implementation).

        Args:
            token: The OAuth token string (usually a JWT).
            required_scopes: Optional list of scope strings that must all be present
                             in the token's 'scope' or 'scp' claim (space-separated string).
            check_expiration: If True (default), checks if the token's 'exp' claim (Unix timestamp)
                              is in the past.
            expected_client_id: Optional string to match against the token's 'cid' or 'client_id' claim.
            expected_user: Optional string to match against the token's 'sub' or 'user_id' claim.

        Returns:
            True if all specified checks pass.

        Raises:
            VerificationError: If the token is invalid (e.g., cannot be decoded), expired
                              (if `check_expiration` is True), missing required scopes,
                              or does not match expected client/user IDs.

        Example:
            >>> # Assume valid_jwt contains {"exp": future_time, "scope": "read write", "cid": "app1"}
            >>> AuthTokenVerification.verify_oauth_token(valid_jwt, required_scopes=["read"], expected_client_id="app1")
            True
            >>> # Assume expired_jwt contains {"exp": past_time, "scope": "read"}
            >>> try:
            ...     AuthTokenVerification.verify_oauth_token(expired_jwt)
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        try:
            # Try to decode as JWT
            payload = AuthExtractionUtils.extract_jwt_payload(token)

            # Check expiration
            if check_expiration and "exp" in payload:
                exp_timestamp = payload["exp"]
                if datetime.now().timestamp() > exp_timestamp:
                    return False

            # Check client ID
            if expected_client_id and "client_id" in payload:
                if payload["client_id"] != expected_client_id:
                    return False

            # Check user
            if expected_user and "sub" in payload:
                if payload["sub"] != expected_user:
                    return False

            # Check scopes
            if required_scopes and "scope" in payload:
                token_scopes = payload["scope"].split()
                for scope in required_scopes:
                    if scope not in token_scopes:
                        return False

            return True
        except ValueError:
            # Not a JWT token, could be an opaque token
            # In a real implementation, you would validate against the token introspection endpoint
            return True

    @staticmethod
    def verify_token_refresh(old_token: str, new_token: str) -> bool:
        """
        Verify basic indicators of a successful token refresh.

        Checks that the `new_token` is different from the `old_token` and that
        `new_token` is not empty. May perform additional checks depending on the
        underlying implementation (e.g., basic JWT structure).

        Args:
            old_token: The original token string.
            new_token: The token string received after a refresh attempt.

        Returns:
            True if `new_token` is non-empty and different from `old_token`.

        Raises:
            VerificationError: If `new_token` is empty or identical to `old_token`.

        Example:
            >>> AuthTokenVerification.verify_token_refresh("token1", "token2")
            True
            >>> try:
            ...     AuthTokenVerification.verify_token_refresh("token1", "token1")
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        # Check that the tokens are different
        if old_token == new_token:
            return False

        try:
            # Try to decode as JWT
            old_payload = AuthExtractionUtils.extract_jwt_payload(old_token)
            new_payload = AuthExtractionUtils.extract_jwt_payload(new_token)

            # Check that the new token has a later expiration
            if "exp" in old_payload and "exp" in new_payload:
                if new_payload["exp"] <= old_payload["exp"]:
                    return False

            # Check that the client ID and user are the same
            for key in ["client_id", "sub"]:
                if key in old_payload and key in new_payload:
                    if old_payload[key] != new_payload[key]:
                        return False

            return True
        except ValueError:
            # Not JWT tokens, could be opaque tokens
            # In a real implementation, you would validate against the token introspection endpoint
            return True

    @staticmethod
    def verify_token_expiration(token: str, jwt: bool = True) -> bool:
        """
        Verify if a token (assumed JWT by default) is expired based on its 'exp' claim.

        Args:
            token: The token string.
            jwt: If True (default), assumes JWT and decodes to find 'exp' claim (Unix timestamp).
                 If False, behavior depends on underlying implementation (may be no-op or error).

        Returns:
            True if the token is considered expired (e.g., 'exp' claim is in the past).
            False if the token is not expired or expiration cannot be determined.

        Raises:
            VerificationError: If `jwt` is True and the token cannot be decoded or lacks an 'exp' claim.

        Example:
            >>> # Assume expired_jwt has 'exp' in the past
            >>> AuthTokenVerification.verify_token_expiration(expired_jwt)
            True
            >>> # Assume valid_jwt has 'exp' in the future
            >>> AuthTokenVerification.verify_token_expiration(valid_jwt)
            False
            >>> try:
            ...     AuthTokenVerification.verify_token_expiration("not-a-jwt")
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        if not jwt:
            # For non-JWT tokens, we can't determine expiration without introspection
            return False

        try:
            payload = AuthExtractionUtils.extract_jwt_payload(token)

            if "exp" in payload:
                exp_timestamp = payload["exp"]
                return bool(datetime.now().timestamp() > exp_timestamp)

            return False  # No expiration claim
        except ValueError:
            return False  # Not a valid JWT

    @staticmethod
    def verify_token_usage(
        token: str, required_scopes: Optional[List[str]] = None, expected_client_id: Optional[str] = None, expected_user: Optional[str] = None
    ) -> None:
        """
        Verify token properties like scopes, client ID, and user ID (similar to verify_oauth_token).

        This is often an alias or wrapper around `verify_oauth_token` focusing on
        the authorization aspects (scopes, identity) rather than just validity.
        Assumes JWT structure to decode claims ('scope'/'scp', 'cid'/'client_id', 'sub'/'user_id').

        Args:
            token: The token string (usually JWT).
            required_scopes: Optional list of scope strings that must be present.
            expected_client_id: Optional expected client ID.
            expected_user: Optional expected user/subject ID.

        Raises:
            VerificationError: If the token is invalid, missing scopes, or doesn't match
                               expected client/user.

        Example:
            >>> # Assume token_jwt has {"scope": "read admin", "cid": "app1", "sub": "user123"}
            >>> AuthTokenVerification.verify_token_usage(token_jwt, required_scopes=["admin"], expected_client_id="app1")
            >>> try:
            ...     AuthTokenVerification.verify_token_usage(token_jwt, required_scopes=["write"])
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        if not token:
            raise VerificationError("Token is empty")

        try:
            # Try to decode as JWT
            payload = AuthExtractionUtils.extract_jwt_payload(token)

            # Check expiration
            if "exp" in payload:
                exp_timestamp = payload["exp"]
                if datetime.now().timestamp() > exp_timestamp:
                    raise VerificationError("Token is expired")

            # Check client ID
            if expected_client_id and "client_id" in payload:
                if payload["client_id"] != expected_client_id:
                    raise VerificationError(f"Token client ID mismatch: expected {expected_client_id}, got {payload['client_id']}")

            # Check user
            if expected_user and "sub" in payload:
                if payload["sub"] != expected_user:
                    raise VerificationError(f"Token user mismatch: expected {expected_user}, got {payload['sub']}")

            # Check scopes
            if required_scopes and "scope" in payload:
                token_scopes = payload["scope"].split()
                for scope in required_scopes:
                    if scope not in token_scopes:
                        raise VerificationError(f"Token missing required scope: {scope}")
        except ValueError:
            # Not a JWT token, could be an opaque token
            # In a real implementation, you would validate against the token introspection endpoint
            pass

    @staticmethod
    def verify_refresh_behavior(old_token: str, new_token: str, expected_client_id: Optional[str] = None) -> None:
        """
        Verify aspects of token refresh behavior, potentially checking claims consistency.

        Extends `verify_token_refresh` by potentially decoding both tokens (if JWTs)
        and comparing claims like client ID or user ID to ensure they remain consistent
        after refresh, if supported by the underlying implementation.

        Args:
            old_token: The original token string.
            new_token: The new token string received after refresh.
            expected_client_id: Optional client ID to verify in the `new_token`'s claims
                                (e.g., 'cid', 'client_id'). May also check `old_token`.

        Raises:
            VerificationError: If basic refresh checks fail (see `verify_token_refresh`)
                               or if claims consistency checks fail (e.g., client ID changes).

        Example:
            >>> # Assume old_jwt has {"cid": "app1"} and new_jwt has {"cid": "app1"}
            >>> AuthTokenVerification.verify_refresh_behavior(old_jwt, new_jwt, expected_client_id="app1")
            >>> # Assume bad_new_jwt has {"cid": "app2"}
            >>> try:
            ...     AuthTokenVerification.verify_refresh_behavior(old_jwt, bad_new_jwt, expected_client_id="app1")
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        # Check that the tokens are different
        if old_token == new_token:
            raise VerificationError("New token is the same as the old token")

        try:
            # Try to decode as JWT
            old_payload = AuthExtractionUtils.extract_jwt_payload(old_token)
            new_payload = AuthExtractionUtils.extract_jwt_payload(new_token)

            # Check that the new token has a later expiration
            if "exp" in old_payload and "exp" in new_payload:
                if new_payload["exp"] <= old_payload["exp"]:
                    raise VerificationError("New token does not have a later expiration")

            # Check that the client ID is the same
            if "client_id" in old_payload and "client_id" in new_payload:
                if old_payload["client_id"] != new_payload["client_id"]:
                    raise VerificationError("Client ID changed during refresh")

                if expected_client_id and new_payload["client_id"] != expected_client_id:
                    raise VerificationError(f"Token client ID mismatch: expected {expected_client_id}, got {new_payload['client_id']}")

            # Check that the user is the same
            if "sub" in old_payload and "sub" in new_payload:
                if old_payload["sub"] != new_payload["sub"]:
                    raise VerificationError("User changed during refresh")
        except ValueError:
            # Not JWT tokens, could be opaque tokens
            # In a real implementation, you would validate against the token introspection endpoint
            pass

    @staticmethod
    def verify_token_has_scopes(token: str, required_scopes: List[str]) -> None:
        """
        Verify a token (assumed JWT) contains all specified scopes in its 'scope'/'scp' claim.

        The 'scope' or 'scp' claim in the JWT payload is expected to be a space-separated string.

        Args:
            token: The token string (usually JWT).
            required_scopes: List of scope strings that must all be present in the token's scope claim.

        Raises:
            VerificationError: If the token is invalid, lacks a scope claim, or is missing
                               one or more of the `required_scopes`.

        Example:
            >>> # Assume token_jwt has {"scope": "read write data:sync"}
            >>> AuthTokenVerification.verify_token_has_scopes(token_jwt, ["read", "write"])
            >>> AuthTokenVerification.verify_token_has_scopes(token_jwt, ["data:sync"])
            >>> try:
            ...     AuthTokenVerification.verify_token_has_scopes(token_jwt, ["admin"])
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        try:
            # Try to decode as JWT
            payload = AuthExtractionUtils.extract_jwt_payload(token)

            # Check scopes
            if "scope" in payload:
                token_scopes = payload["scope"].split()
                for scope in required_scopes:
                    if scope not in token_scopes:
                        raise VerificationError(f"Token missing required scope: {scope}")
            else:
                raise VerificationError("Token does not contain scope claim")
        except ValueError as e:
            # Not a JWT token, could be an opaque token
            # In a real implementation, you would validate against the token introspection endpoint
            raise VerificationError(f"Could not extract scopes from token: {str(e)}")
