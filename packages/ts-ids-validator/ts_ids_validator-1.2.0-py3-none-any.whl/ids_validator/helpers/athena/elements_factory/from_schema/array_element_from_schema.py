from __future__ import annotations

import ids_validator.helpers.athena.builders.data_object_builder as s
import ids_validator.helpers.athena.elements_factory.elements_abstract_factory as eaf
from ids_validator.helpers.athena.athena_logger import athena_logger
from ids_validator.helpers.athena.constants import get_primitive_types
from ids_validator.helpers.athena.elements_factory.arrays_size_factory import (
    ArraysSizeFactory,
)
from ids_validator.helpers.athena.elements_factory.element_interface import (
    ElementToWorkWith,
)


class ArrayElementFromSchema(ElementToWorkWith):
    def __init__(self):
        self.logger = athena_logger("ArrayElement")

    def generator(
        self, field_type, _running_schema_property, input_json, parent_object
    ) -> dict:
        """
        The client code works with an instance of a concrete ElementsFactory, albeit through
        its base interface. As long as the client keeps working with the ElementsFactory via
        the base interface, you can pass it any ElementsFactory's subclass.
        """

        elements_generator = (
            eaf.ElementsAbstractFactory()
            .pick_factory_from("schema")
            .pick_generator(field_type)
        )

        return elements_generator.generate_value(
            _running_schema_property, input_json, parent_object
        )

    def generate_value(
        self, _property, input_json, parent_object: s.DataObjectFromSchemaBuilder
    ) -> list:
        items_type = input_json[_property]["items"]["type"]

        # When encountering an array of string, boolean, number, or any of the preceding as nullable
        if items_type in get_primitive_types() or isinstance(items_type, list):
            return [
                self.generator(
                    input_json[_property]["items"]["type"],
                    _property,
                    input_json[_property]["items"],
                    input_json,
                )
                for _ in range(
                    ArraysSizeFactory().get_array_size(
                        input_json["table_prefix"] + _property
                    )
                )
            ]

        else:
            # not a plain field, either object or array
            return [
                s.DataObjectFromSchemaBuilder(parent_object.material[_property])
                .with_material(parent_object.material[_property]["items"])
                .with_parent_json_node(f"{parent_object.full_path}/{_property}")
                .with_root_table(parent_object.root_table)
                .with_parent_table_name(parent_object.parent_table_name)
                .with_table_prefix(input_json["table_prefix"])
                .build()
                for _ in range(
                    ArraysSizeFactory().get_array_size(
                        input_json["table_prefix"] + _property
                    )
                )
            ]
