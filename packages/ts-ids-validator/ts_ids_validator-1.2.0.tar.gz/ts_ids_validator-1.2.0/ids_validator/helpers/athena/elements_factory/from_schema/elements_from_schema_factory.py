from __future__ import annotations

from abc import ABC

from ids_validator.helpers.athena.constants import get_primitive_types
from ids_validator.helpers.athena.elements_factory.element_interface import (
    ElementToWorkWith,
)
from ids_validator.helpers.athena.elements_factory.elements_factory_interface import (
    ElementsFactory,
)
from ids_validator.helpers.athena.elements_factory.from_schema.array_element_from_schema import (
    ArrayElementFromSchema,
)
from ids_validator.helpers.athena.elements_factory.from_schema.custom_fields_element_from_schema import (
    CustomFieldsElementFromSchema,
)
from ids_validator.helpers.athena.elements_factory.from_schema.data_cubes_element_from_schema import (
    DataCubesElementFromSchema,
)
from ids_validator.helpers.athena.elements_factory.from_schema.object_element_from_schema import (
    ObjectElementFromSchema,
)
from ids_validator.helpers.athena.elements_factory.from_schema.primitive_element_from_schema import (
    PrimitiveElementFromSchema,
)
from ids_validator.helpers.athena.exceptions import UnknownFieldType


class ElementsFromSchemaFactory(ElementsFactory, ABC):
    def pick_generator(self, field_type) -> ElementToWorkWith:
        """
        Also note that, despite its name, the Creator's primary responsibility
        is not creating products. Usually, it contains some core business logic
        that relies on Product objects, returned by the factory method.
        Subclasses can indirectly change that business logic by overriding the
        factory method and returning a different type of product from it.
        """

        # Call the factory method to create a Product object.
        if field_type == "array":
            return ArrayElementFromSchema()
        if field_type == "object":
            return ObjectElementFromSchema()
        if field_type == "datacubes":
            return DataCubesElementFromSchema()
        if field_type == "custom_fields":
            return CustomFieldsElementFromSchema()
        if isinstance(field_type, list) or field_type in get_primitive_types():
            return PrimitiveElementFromSchema()
        raise UnknownFieldType(f"Unknown field type '{field_type}'.")
