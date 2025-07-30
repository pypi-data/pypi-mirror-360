from __future__ import annotations

import copy

from ids_validator.helpers.athena.athena_logger import athena_logger
from ids_validator.helpers.athena.constants import JSON_PATH, get_service_fields
from ids_validator.helpers.athena.elements_factory.elements_abstract_factory import (
    ElementsAbstractFactory,
)
from ids_validator.helpers.athena.exceptions import InvalidSchemaDefinition


class DataObjectFromSchemaBuilder:
    def __init__(self, root_schema: dict):
        self.full_path = ""
        self.partition = {}
        self._with_another_root = None
        self.factory_from = None
        self.parent_table_name = None
        self.material = None
        self.required = None
        self.definitions = None
        self.uuid = None
        self.root_table = None
        self.athena_string = None
        self.schema = None
        self.root_schema = root_schema
        self.table_prefix = None
        self.logger = athena_logger("DataObjectBuilder")

    def with_schema(self, schema: dict) -> DataObjectFromSchemaBuilder:
        """Setting up current level of table prefix."""
        self.schema = schema
        return self

    def with_table_prefix(self, table_prefix: dict) -> DataObjectFromSchemaBuilder:
        """Setting up table prefix."""
        self.table_prefix = table_prefix
        return self

    def with_root_table(self, root_table: str) -> DataObjectFromSchemaBuilder:
        self.root_table = root_table
        return self

    def with_parent_table_name(
        self, parent_table_name: str
    ) -> DataObjectFromSchemaBuilder:
        """Setting up nameof the parent table for the object."""
        self.parent_table_name = parent_table_name
        return self

    def with_material(self, material: dict) -> DataObjectFromSchemaBuilder:
        if "properties" in material:
            self.material = copy.deepcopy(material["properties"])
            if "required" in material:
                # to inherit required for the types with list not primitive
                self.material.update(
                    {"required_primitive_properties": material["required"]}
                )
        else:  # in case in array of primitives
            self.material = copy.deepcopy(material)
        return self

    def with_parent_json_node(self, param) -> DataObjectFromSchemaBuilder:
        self.full_path = param
        return self

    def generator(
        self, field_type: str, _running_schema_property, input_json: dict
    ) -> dict:
        """
        The client code works with an instance of a concrete ElementsFactory, albeit through
        its base interface. As long as the client keeps working with the ElementsFactory via
        the base interface, you can pass it any ElementsFactory's subclass.
        """
        json_to_send = copy.deepcopy(input_json)
        json_to_send.update({"table_prefix": self.table_prefix})

        elements_generator = (
            ElementsAbstractFactory()
            .pick_factory_from("schema")
            .pick_generator(field_type)
        )

        return elements_generator.generate_value(
            _running_schema_property, json_to_send, self
        )

    def build(self) -> dict:
        schema_with_data = {}
        for _property in self.material:
            _property_value = "nothing to set"
            if _property in get_service_fields():
                continue
            if _property in (
                "datacubes",
                "custom_fields",
            ):
                # Will always return empty list
                _property_value = self.generator(_property, _property, self.material)
            else:
                # array, object, primitive
                try:
                    _property_value = self.generator(
                        self.material[_property]["type"], _property, self.material
                    )
                except (KeyError, TypeError):
                    field = self.full_path.strip("/").replace("/", ".")
                    if (
                        self.material.get("type") == "array"
                        and self.root_schema.get("type") == "array"
                    ):
                        raise InvalidSchemaDefinition(
                            f"Invalids IDS definition found at field '{field}'."
                            f" Nested arrays are disallowed in IDSs."
                        )
                    else:
                        raise InvalidSchemaDefinition(
                            "Unexpected schema object definition found at field "
                            f"'{field}'. Could not find the object's 'type' field."
                        )

                if not isinstance(_property_value, list):
                    _property_value.update({JSON_PATH: f"{self.full_path}/{_property}"})
            if _property_value != "nothing to set":
                sanitize_property_name = _property
                schema_with_data.update({sanitize_property_name: _property_value})

        return schema_with_data
