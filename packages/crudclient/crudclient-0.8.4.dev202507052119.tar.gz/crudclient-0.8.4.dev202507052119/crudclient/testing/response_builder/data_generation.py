# crudclient/testing/response_builder/data_generation.py
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union


class DataGenerationBuilder:
    """
    Utility class for generating random test data based on a schema definition.

    Provides methods to create random data for testing API responses, following
    a specified schema structure.
    """

    @staticmethod
    def create_random_data(schema: Dict[str, Any], count: int = 1) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Generate random data based on a schema definition.

        The schema is a dictionary where keys are field names and values define the data type.
        Supported types include:
        - Primitive types: 'string'/str, 'int'/int, 'float'/float, 'bool'/bool
        - Special types: 'email', 'name', 'date', 'datetime', 'uuid', 'url', 'ip'
        - Nested objects (as dictionaries)
        - Arrays (as lists with a single item defining the array element type)

        Args:
            schema: A dictionary defining the structure and types of data to generate
            count: Number of items to generate (if 1, returns a single item; otherwise a list)

        Returns:
            Either a single dictionary or a list of dictionaries with randomly generated data
            that matches the provided schema.

        Examples:
            ```python
            # Generate a single user
            user = DataGenerationBuilder.create_random_data({
                "id": "uuid",
                "name": "name",
                "email": "email",
                "age": "int",
                "is_active": "bool",
                "created_at": "datetime",
                "address": {
                    "street": "string",
                    "city": "string",
                    "zip": "string"
                },
                "tags": ["string"]
            })

            # Generate multiple users
            users = DataGenerationBuilder.create_random_data({
                "id": "uuid",
                "name": "name"
            }, count=5)
            ```
        """
        if count == 1:
            return DataGenerationBuilder._generate_item(schema)
        else:
            return [DataGenerationBuilder._generate_item(schema) for _ in range(count)]

    @staticmethod
    def _generate_item(schema_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a single item based on the schema definition.

        Args:
            schema_def: A dictionary defining the structure and types of data to generate

        Returns:
            A dictionary with randomly generated data that matches the provided schema
        """
        result = {}
        for key, value_type in schema_def.items():
            result[key] = DataGenerationBuilder._process_field_value(value_type)
        return result

    @staticmethod
    def _process_field_value(value_type: Any) -> Any:
        """
        Process a field value based on its type.

        Handles different types of values in the schema, including nested objects,
        arrays, and primitive types.

        Args:
            value_type: The type definition from the schema

        Returns:
            A randomly generated value of the appropriate type
        """
        if isinstance(value_type, dict):
            # Nested object
            return DataGenerationBuilder._generate_item(value_type)
        elif isinstance(value_type, list) and len(value_type) > 0:
            # Array of items
            return DataGenerationBuilder._generate_array(value_type[0])
        else:
            # Primitive type
            return DataGenerationBuilder._generate_primitive(value_type)

    @staticmethod
    def _generate_array(element_type: Any) -> List[Any]:
        """
        Generate an array of items based on the element type.

        Creates a random-length array (between 1 and 5 items) of the specified type.

        Args:
            element_type: The type definition for elements in the array

        Returns:
            A list of randomly generated values of the appropriate type
        """
        array_count = random.randint(1, 5)

        if isinstance(element_type, dict):
            # Array of objects
            return [DataGenerationBuilder._generate_item(element_type) for _ in range(array_count)]
        else:
            # Array of primitives
            return [DataGenerationBuilder._generate_primitive(element_type) for _ in range(array_count)]

    @staticmethod
    def _generate_primitive(type_hint: Any) -> Any:
        """
        Generate a primitive value based on the type hint.

        Supports various primitive types and special formats like email, name, date, etc.

        Args:
            type_hint: The type hint string or type object

        Returns:
            A randomly generated value of the appropriate type
        """
        # String types
        if type_hint in ("string", str):
            return DataGenerationBuilder._generate_random_string()
        elif type_hint == "email":
            return DataGenerationBuilder._generate_email()
        elif type_hint == "name":
            return DataGenerationBuilder._generate_name()
        elif type_hint == "url":
            return DataGenerationBuilder._generate_url()
        elif type_hint == "ip":
            return DataGenerationBuilder._generate_ip()
        # Number types
        elif type_hint in ("int", int):
            return random.randint(1, 1000)
        elif type_hint in ("float", float):
            return round(random.uniform(1.0, 1000.0), 2)
        # Boolean type
        elif type_hint in ("bool", bool):
            return random.choice([True, False])
        # Date and time types
        elif type_hint == "date":
            return DataGenerationBuilder._generate_date()
        elif type_hint == "datetime":
            return DataGenerationBuilder._generate_datetime()
        # ID types
        elif type_hint == "uuid":
            return str(uuid.uuid4())
        # Default case
        else:
            return str(type_hint)  # Default to string representation

    @staticmethod
    def _generate_random_string(length: Optional[int] = None) -> str:
        """
        Generate a random string of letters.

        Args:
            length: The length of the string to generate. If None, a random length
                   between 5 and 10 is used.

        Returns:
            A random string of the specified length
        """
        if length is None:
            length = random.randint(5, 10)
        return "".join(random.choices(string.ascii_letters, k=length))

    @staticmethod
    def _generate_email() -> str:
        """
        Generate a random email address.

        Returns:
            A random email address in the format username@example.com
        """
        username = "".join(random.choices(string.ascii_lowercase, k=8))
        return f"{username}@example.com"

    @staticmethod
    def _generate_name() -> str:
        """
        Generate a random full name.

        Returns:
            A random full name consisting of a first name and last name
        """
        first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @staticmethod
    def _generate_date() -> str:
        """
        Generate a random date string in YYYY-MM-DD format.

        Returns:
            A random date string within the last two years
        """
        days = random.randint(0, 365 * 2)
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def _generate_datetime() -> str:
        """
        Generate a random datetime string in ISO format.

        Returns:
            A random datetime string within the last two years in ISO format (YYYY-MM-DDTHH:MM:SSZ)
        """
        days = random.randint(0, 365 * 2)
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        dt = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _generate_url() -> str:
        """
        Generate a random URL.

        Returns:
            A random URL in the format https://example.com/path
        """
        path = "".join(random.choices(string.ascii_lowercase, k=8))
        return f"https://example.com/{path}"

    @staticmethod
    def _generate_ip() -> str:
        """
        Generate a random IP address.

        Returns:
            A random IPv4 address string
        """
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
