"""
Concrete ElementsFactory's override the factory method in order to change the resulting
product's type.
"""
import ids_validator.helpers.athena.builders.data_object_builder as s
from ids_validator.helpers.athena.elements_factory.element_interface import (
    ElementToWorkWith,
)


class ObjectElementFromSchema(ElementToWorkWith):
    def generate_value(self, _property, input_json, parent_object) -> dict:
        return (
            s.DataObjectFromSchemaBuilder(parent_object.material[_property])
            .with_material(parent_object.material[_property])
            .with_parent_json_node(f"{parent_object.full_path}/{_property}")
            .with_root_table(parent_object.root_table)
            .with_parent_table_name(parent_object.parent_table_name)
            .with_table_prefix(input_json["table_prefix"])
            .build()
        )
