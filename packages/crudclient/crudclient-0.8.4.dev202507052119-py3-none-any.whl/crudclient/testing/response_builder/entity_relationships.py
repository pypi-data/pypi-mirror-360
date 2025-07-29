"""
Entity relationship builder utilities for mock client.

This module provides utilities for creating related entities and entity graphs for testing API responses that involve relationships between different resources.
"""

import random
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from .response import MockResponse


class EntityRelationshipBuilder:
    """
    Builder for creating related entities and entity graphs.

    This class provides static methods for generating mock API responses that
    represent relationships between different entities, supporting both embedded
    and referenced relationships.
    """

    @staticmethod
    def create_related_entities(
        primary_entity: Dict[str, Any],
        related_entities: List[Dict[str, Any]],
        relation_key: str,
        foreign_key: str = "id",
        embed: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a primary entity with relationships to other entities.

        This method establishes relationships between a primary entity and a list
        of related entities, either by embedding the full related entities or by
        including only their IDs.

        Args:
            primary_entity: The main entity to which relationships will be added
            related_entities: List of entities to relate to the primary entity
            relation_key: The key in the primary entity where the relationship will be stored
            foreign_key: The key in the related entities to use for reference (typically "id")
            embed: If True, embeds the full related entities; if False, includes only their IDs

        Returns:
            A copy of the primary entity with the relationships added
        """
        result = primary_entity.copy()

        if embed:
            # Embed the full related entities
            result[relation_key] = related_entities
        else:
            # Just include the IDs of related entities
            result[relation_key] = [entity[foreign_key] for entity in related_entities if foreign_key in entity]

        return result

    @staticmethod
    def create_entity_graph(
        entities_by_type: Dict[str, List[Dict[str, Any]]],
        relationships: Dict[str, Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create a graph of related entities based on defined relationships.

        This method generates a complex entity graph with various types of relationships
        (one-to-one, one-to-many) between different entity types. It supports both
        embedded and referenced relationships.

        Args:
            entities_by_type: Dictionary mapping entity types to lists of entities
            relationships: Dictionary defining the relationships between entity types.
                           Format:
                               {
                                   "source_type": {
                                       "relation_key": {
                                           "target_type": "target_entity_type",
                                           "cardinality": "one" or "many",
                                           "embed": True or False,
                                           "foreign_key": "id",
                                           "count": optional count for "many" relationships
                                       }
                                   }
                               }

        Returns:
            A dictionary containing all entities with their relationships established
        """
        result = {k: [item.copy() for item in v] for k, v in entities_by_type.items()}

        # Process each relationship
        for source_type, relations in relationships.items():
            if source_type not in result:
                continue

            source_entities = result[source_type]

            for relation_key, relation_config in relations.items():
                target_type = relation_config.get("target_type")
                if target_type not in result:
                    continue

                target_entities = result[target_type]
                cardinality = relation_config.get("cardinality", "many")
                embed = relation_config.get("embed", False)
                foreign_key = relation_config.get("foreign_key", "id")

                # Update each source entity with the relationship
                for source_entity in source_entities:
                    if cardinality == "one":
                        # One-to-one relationship
                        if target_entities:
                            target = random.choice(target_entities)
                            if embed:
                                source_entity[relation_key] = target
                            else:
                                source_entity[relation_key] = target.get(foreign_key)
                    else:
                        # One-to-many or many-to-many relationship
                        count = relation_config.get("count", random.randint(0, min(3, len(target_entities))))
                        related = random.sample(target_entities, min(count, len(target_entities)))

                        if embed:
                            source_entity[relation_key] = related
                        else:
                            source_entity[relation_key] = [entity.get(foreign_key) for entity in related if foreign_key in entity]

        return result

    @staticmethod
    def _extract_entity_id_from_url(url: str, entity_type: str) -> Tuple[str, Optional[MockResponse]]:
        """
        Extract entity ID from URL or return error response if not possible.

        Args:
            url: The URL to extract the ID from
            entity_type: The type of entity (used in error messages)

        Returns:
            A tuple containing the extracted ID and an optional error response.
            If extraction is successful, the second element will be None.
            If extraction fails, the first element will be an empty string and
            the second element will be a 404 error response.
        """
        parts = url.rstrip("/").split("/")
        if not parts:
            return "", MockResponse(status_code=404, json_data={"error": f"{entity_type} not found"})
        return parts[-1], None

    @staticmethod
    def _create_entity_not_found_response(entity_type: str, entity_id: str) -> MockResponse:
        """
        Create a standard 404 response for entity not found.

        Args:
            entity_type: The type of entity (used in error messages)
            entity_id: The ID of the entity that was not found

        Returns:
            A MockResponse with a 404 status code and appropriate error message
        """
        return MockResponse(status_code=404, json_data={"error": f"{entity_type} not found with id {entity_id}"})

    @staticmethod
    def _create_list_factory(entities: List[Dict[str, Any]], entity_type: str) -> Callable[..., MockResponse]:
        """
        Create a factory function for list operation.

        Args:
            entities: The list of entities to return
            entity_type: The type of entity (used in error messages)

        Returns:
            A factory function that returns a MockResponse with the entities
        """

        def list_factory(**kwargs: Any) -> MockResponse:
            return MockResponse(status_code=200, json_data={"data": entities, "count": len(entities)})

        return list_factory

    @staticmethod
    def _create_get_factory(entity_map: Dict[str, Dict[str, Any]], entity_type: str) -> Callable[..., MockResponse]:
        """
        Create a factory function for get operation.

        Args:
            entity_map: A dictionary mapping entity IDs to entity data
            entity_type: The type of entity (used in error messages)

        Returns:
            A factory function that extracts an entity ID from the URL and
            returns the corresponding entity or an error response
        """

        def get_factory(**kwargs: Any) -> MockResponse:
            url = kwargs.get("url", "")
            entity_id, error_response = EntityRelationshipBuilder._extract_entity_id_from_url(url, entity_type)
            if error_response:
                return error_response

            if entity_id in entity_map:
                return MockResponse(status_code=200, json_data=entity_map[entity_id])
            else:
                return EntityRelationshipBuilder._create_entity_not_found_response(entity_type, entity_id)

        return get_factory

    @staticmethod
    def _create_create_factory(
        entities: List[Dict[str, Any]], entity_map: Dict[str, Dict[str, Any]], entity_type: str, id_field: str
    ) -> Callable[..., MockResponse]:
        """
        Create a factory function for create operation.

        Args:
            entities: The list of entities to add the new entity to
            entity_map: A dictionary mapping entity IDs to entity data
            entity_type: The type of entity (used in error messages)
            id_field: The field name used as the identifier in the entities

        Returns:
            A factory function that creates a new entity and returns it
            in a MockResponse with a 201 status code
        """

        def create_factory(**kwargs: Any) -> MockResponse:
            json_data = kwargs.get("json", {})
            if not json_data:
                return MockResponse(status_code=400, json_data={"error": f"Invalid {entity_type} data"})

            # Generate a new ID if not provided
            if id_field not in json_data:
                json_data[id_field] = str(uuid.uuid4())

            # Add created_at timestamp
            if "created_at" not in json_data:
                json_data["created_at"] = datetime.now().isoformat()

            # Add to entities
            entity_id = str(json_data[id_field])
            entity_map[entity_id] = json_data
            entities.append(json_data)

            return MockResponse(status_code=201, json_data=json_data)

        return create_factory

    @staticmethod
    def _create_update_factory(entity_map: Dict[str, Dict[str, Any]], entity_type: str) -> Callable[..., MockResponse]:
        """
        Create a factory function for update operation.

        Args:
            entity_map: A dictionary mapping entity IDs to entity data
            entity_type: The type of entity (used in error messages)

        Returns:
            A factory function that updates an existing entity and returns it
            in a MockResponse with a 200 status code
        """

        def update_factory(**kwargs: Any) -> MockResponse:
            url = kwargs.get("url", "")
            json_data = kwargs.get("json", {})

            entity_id, error_response = EntityRelationshipBuilder._extract_entity_id_from_url(url, entity_type)
            if error_response:
                return error_response

            if entity_id not in entity_map:
                return EntityRelationshipBuilder._create_entity_not_found_response(entity_type, entity_id)

            # Update entity
            entity = entity_map[entity_id]
            entity.update(json_data)

            # Add updated_at timestamp
            entity["updated_at"] = datetime.now().isoformat()

            return MockResponse(status_code=200, json_data=entity)

        return update_factory

    @staticmethod
    def _create_delete_factory(
        entities: List[Dict[str, Any]], entity_map: Dict[str, Dict[str, Any]], entity_type: str
    ) -> Callable[..., MockResponse]:
        """
        Create a factory function for delete operation.

        Args:
            entities: The list of entities to remove the entity from
            entity_map: A dictionary mapping entity IDs to entity data
            entity_type: The type of entity (used in error messages)

        Returns:
            A factory function that deletes an entity and returns a
            MockResponse with a 204 status code
        """

        def delete_factory(**kwargs: Any) -> MockResponse:
            url = kwargs.get("url", "")

            entity_id, error_response = EntityRelationshipBuilder._extract_entity_id_from_url(url, entity_type)
            if error_response:
                return error_response

            if entity_id not in entity_map:
                return EntityRelationshipBuilder._create_entity_not_found_response(entity_type, entity_id)

            # Remove entity
            entity = entity_map.pop(entity_id)
            entities.remove(entity)

            return MockResponse(status_code=204, json_data=None)

        return delete_factory

    @staticmethod
    def create_consistent_response_sequence(
        entity_type: str,
        base_entities: List[Dict[str, Any]],
        operations: List[str],
        id_field: str = "id",
    ) -> List[Callable[..., MockResponse]]:
        """
        Create a sequence of response factories that maintain consistency across CRUD operations.

        This method generates a list of response factory functions that simulate a consistent
        API behavior across a sequence of operations (list, get, create, update, delete).
        Each operation maintains the state changes from previous operations.

        Args:
            entity_type: The type of entity being operated on (used in error messages)
            base_entities: The initial set of entities to use as the data source
            operations: List of operations to include in the sequence ("list", "get", "create", "update", "delete")
            id_field: The field name used as the identifier in the entities

        Returns:
            A list of callable factory functions that generate MockResponse objects.
            Each factory accepts kwargs that may include:
            - url: The URL of the request (used to extract IDs for get/update/delete)
            - json: The request body data (used for create/update operations)
        """
        # Create a mutable copy of entities that will be modified by operations
        entities = [entity.copy() for entity in base_entities]
        entity_map = {str(entity.get(id_field)): entity for entity in entities if id_field in entity}

        # Map operations to their factory creation methods
        operation_factory_map = {
            "list": lambda: EntityRelationshipBuilder._create_list_factory(entities, entity_type),
            "get": lambda: EntityRelationshipBuilder._create_get_factory(entity_map, entity_type),
            "create": lambda: EntityRelationshipBuilder._create_create_factory(entities, entity_map, entity_type, id_field),
            "update": lambda: EntityRelationshipBuilder._create_update_factory(entity_map, entity_type),
            "delete": lambda: EntityRelationshipBuilder._create_delete_factory(entities, entity_map, entity_type),
        }

        # Create response factories for each requested operation
        response_factories = []
        for operation in operations:
            if operation in operation_factory_map:
                response_factories.append(operation_factory_map[operation]())

        return response_factories
