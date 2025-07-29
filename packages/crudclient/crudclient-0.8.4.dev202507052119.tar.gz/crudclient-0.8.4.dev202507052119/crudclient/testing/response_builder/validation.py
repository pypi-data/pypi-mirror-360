from typing import Any, Callable, Dict, List, Optional

from .response import MockResponse


class ValidationErrorBuilder:
    """
    Provides static methods to create MockResponse objects representing
    various schema validation errors.
    """

    @staticmethod
    def create_schema_validation_error(
        invalid_fields: Dict[str, str],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
        error_format: str = "standard",
    ) -> MockResponse:
        """
        Creates a MockResponse for a schema validation error.

        Args:
            invalid_fields: A dictionary mapping field names to error messages.
            status_code: The HTTP status code for the response.
            error_code: A custom error code string.
            message: The main error message.
            error_format: The format of the error response ('standard', 'json_api', 'detailed', 'simple').

        Returns:
            A MockResponse object representing the validation error.
        """
        response_data: Dict[str, Any]
        if error_format == "standard":
            response_data = {
                "error": error_code,
                "message": message,
                "errors": [{"field": field, "message": error_msg} for field, error_msg in invalid_fields.items()],
            }
        elif error_format == "json_api":
            response_data = {
                "errors": [
                    {
                        "status": str(status_code),
                        "code": error_code,
                        "title": message,
                        "source": {"pointer": f"/data/attributes/{field}"},
                        "detail": error_msg,
                    }
                    for field, error_msg in invalid_fields.items()
                ]
            }
        elif error_format == "detailed":
            details = [
                {
                    "field": field,
                    "message": error_msg,
                    "code": f"{error_code}_{field.upper()}",
                }
                for field, error_msg in invalid_fields.items()
            ]
            response_data = {
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": details,
                }
            }
        else:
            # Simple format
            response_data = {"error": message, "fields": invalid_fields}

        return MockResponse(status_code=status_code, json_data=response_data)

    @staticmethod
    def create_field_validator(
        field_name: str,
        validators: List[Callable[[Any], Optional[str]]],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        error_format: str = "standard",
    ) -> Callable[[Dict[str, Any]], Optional[MockResponse]]:
        """
        Creates a validator function for a single field.

        Args:
            field_name: The name of the field to validate.
            validators: A list of validator functions for the field.
            status_code: The status code for validation errors.
            error_code: The error code for validation errors.
            error_format: The error format for validation errors.

        Returns:
            A function that takes request data and returns a MockResponse if validation fails, else None.
        """

        def validator_function(data: Any) -> Optional[MockResponse]:
            if not isinstance(data, dict):
                return ValidationErrorBuilder.create_schema_validation_error(
                    {field_name: "Invalid data format"},
                    status_code=status_code,
                    error_code=error_code,
                    error_format=error_format,
                )

            if field_name not in data:
                return ValidationErrorBuilder.create_schema_validation_error(
                    {field_name: "Field is required"},
                    status_code=status_code,
                    error_code=error_code,
                    error_format=error_format,
                )

            field_value = data[field_name]

            for validator in validators:
                error_message = validator(field_value)
                if error_message:
                    return ValidationErrorBuilder.create_schema_validation_error(
                        {field_name: error_message}, status_code=status_code, error_code=error_code, error_format=error_format
                    )

            return None  # No validation errors

        return validator_function

    @staticmethod
    def create_data_validator(
        validators: Dict[str, List[Callable[[Any], Optional[str]]]],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
        error_format: str = "standard",
        require_all_fields: bool = False,
    ) -> Callable[[Dict[str, Any]], Optional[MockResponse]]:
        """
        Creates a validator function for multiple fields in a data dictionary.

        Args:
            validators: A dictionary mapping field names to lists of validator functions.
            status_code: The status code for validation errors.
            error_code: The error code for validation errors.
            message: The main error message for validation failures.
            error_format: The error format for validation errors.
            require_all_fields: If True, missing fields defined in validators will cause an error.

        Returns:
            A function that takes request data and returns a MockResponse if validation fails, else None.
        """

        def validator_function(data: Any) -> Optional[MockResponse]:
            if not isinstance(data, dict):
                return ValidationErrorBuilder.create_schema_validation_error(
                    {"_general": "Invalid data format"},
                    status_code=status_code,
                    error_code=error_code,
                    message=message,
                    error_format=error_format,
                )

            invalid_fields = {}

            for field_name, field_validators in validators.items():
                if field_name not in data:
                    if require_all_fields:
                        invalid_fields[field_name] = "Field is required"
                    continue

                field_value = data[field_name]

                for validator in field_validators:
                    error_message = validator(field_value)
                    if error_message:
                        invalid_fields[field_name] = error_message
                        break

            if invalid_fields:
                return ValidationErrorBuilder.create_schema_validation_error(
                    invalid_fields,
                    status_code=status_code,
                    error_code=error_code,
                    message=message,
                    error_format=error_format,
                )

            return None  # No validation errors

        return validator_function


class BusinessLogicConstraintBuilder:
    """
    Provides static methods to create MockResponse objects representing
    various business logic constraint violations.
    """

    @staticmethod
    def create_business_rule_error(
        rule_name: str,
        message: str,
        status_code: int = 422,
        error_code: str = "BUSINESS_RULE_VIOLATION",
        details: Optional[Dict[str, Any]] = None,
    ) -> MockResponse:
        """
        Creates a MockResponse for a generic business rule violation.

        Args:
            rule_name: The name of the violated rule.
            message: The error message describing the violation.
            status_code: The HTTP status code.
            error_code: The custom error code.
            details: Optional additional details about the error.

        Returns:
            A MockResponse object representing the business rule error.
        """
        response_data: Dict[str, Any] = {"error": error_code, "message": message, "rule": rule_name}

        if details:
            response_data["details"] = details

        return MockResponse(status_code=status_code, json_data=response_data)

    @staticmethod
    def create_unique_constraint_error(
        field_name: str,
        value: Any,
        entity_type: str = "resource",
        status_code: int = 409,
        error_code: str = "UNIQUE_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Creates a MockResponse for a unique constraint violation.

        Args:
            field_name: The name of the field that must be unique.
            value: The value that caused the violation.
            entity_type: The type of entity being created/updated.
            status_code: The HTTP status code (typically 409 Conflict).
            error_code: The custom error code.

        Returns:
            A MockResponse object representing the unique constraint error.
        """
        message = f"A {entity_type} with {field_name} '{value}' already exists"

        return MockResponse(status_code=status_code, json_data={"error": error_code, "message": message, "field": field_name, "value": value})

    @staticmethod
    def create_foreign_key_constraint_error(
        field_name: str,
        value: Any,
        referenced_entity: str,
        status_code: int = 422,
        error_code: str = "FOREIGN_KEY_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Creates a MockResponse for a foreign key constraint violation.

        Args:
            field_name: The name of the foreign key field.
            value: The value provided for the foreign key.
            referenced_entity: The type of entity being referenced.
            status_code: The HTTP status code.
            error_code: The custom error code.

        Returns:
            A MockResponse object representing the foreign key constraint error.
        """
        message = f"No {referenced_entity} found with {field_name} '{value}'"

        return MockResponse(
            status_code=status_code,
            json_data={"error": error_code, "message": message, "field": field_name, "value": value, "referenced_entity": referenced_entity},
        )

    @staticmethod
    def create_state_transition_error(
        entity_type: str,
        current_state: str,
        target_state: str,
        allowed_transitions: List[str],
        status_code: int = 422,
        error_code: str = "INVALID_STATE_TRANSITION",
    ) -> MockResponse:
        """
        Creates a MockResponse for an invalid state transition error.

        Args:
            entity_type: The type of entity whose state transition failed.
            current_state: The current state of the entity.
            target_state: The attempted target state.
            allowed_transitions: A list of valid target states from the current state.
            status_code: The HTTP status code.
            error_code: The custom error code.

        Returns:
            A MockResponse object representing the state transition error.
        """
        message = f"Cannot transition {entity_type} from '{current_state}' to '{target_state}'"

        return MockResponse(
            status_code=status_code,
            json_data={
                "error": error_code,
                "message": message,
                "current_state": current_state,
                "target_state": target_state,
                "allowed_transitions": allowed_transitions,
            },
        )

    @staticmethod
    def create_dependency_constraint_error(
        entity_type: str,
        entity_id: str,
        dependent_entities: List[Dict[str, Any]],
        status_code: int = 422,
        error_code: str = "DEPENDENCY_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Creates a MockResponse for a dependency constraint violation.

        Args:
            entity_type: The type of the entity that cannot be modified/deleted.
            entity_id: The ID of the entity.
            dependent_entities: A list of entities that depend on this one.
            status_code: The HTTP status code.
            error_code: The custom error code.

        Returns:
            A MockResponse object representing the dependency constraint error.
        """
        message = f"Cannot perform operation on {entity_type} '{entity_id}' due to existing dependencies"

        return MockResponse(
            status_code=status_code,
            json_data={
                "error": error_code,
                "message": message,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "dependencies": dependent_entities,
            },
        )

    @staticmethod
    def create_business_rule_validator(
        rule_name: str,
        validator_function: Callable[[Dict[str, Any]], bool],
        error_message: str,
        status_code: int = 422,
        error_code: str = "BUSINESS_RULE_VIOLATION",
        details_function: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> Callable[[Dict[str, Any]], Optional[MockResponse]]:
        """
        Creates a validator function based on a custom business rule.

        Args:
            rule_name: The name of the business rule.
            validator_function: A function that takes data and returns True if the rule passes, False otherwise.
            error_message: The error message to use if the rule fails.
            status_code: The status code for the error response.
            error_code: The error code for the error response.
            details_function: An optional function to generate details for the error response.

        Returns:
            A function that takes request data and returns a MockResponse if the rule fails, else None.
        """

        def rule_validator(data: Dict[str, Any]) -> Optional[MockResponse]:
            if not validator_function(data):
                details = None
                if details_function:
                    details = details_function(data)

                return BusinessLogicConstraintBuilder.create_business_rule_error(
                    rule_name=rule_name, message=error_message, status_code=status_code, error_code=error_code, details=details
                )

            return None  # Rule satisfied

        return rule_validator


# Common validator functions are now in the 'validators' module.
