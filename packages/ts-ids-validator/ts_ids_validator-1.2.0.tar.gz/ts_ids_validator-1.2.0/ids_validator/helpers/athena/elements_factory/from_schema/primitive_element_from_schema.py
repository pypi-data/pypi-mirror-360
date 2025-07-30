import copy

from ids_validator.helpers.athena.athena_helper import AthenaHelper
from ids_validator.helpers.athena.constants import (
    FIELD_TYPE_KEY,
    FIELD_VALUE_KEY,
    OBJECT_TYPE_IN_JSON_KEY,
    get_service_fields_names,
)
from ids_validator.helpers.athena.elements_factory.element_interface import (
    ElementToWorkWith,
)


class PrimitiveElementFromSchema(ElementToWorkWith):
    def generate_value(
        self, _running_schema_property, input_json, parent_object
    ) -> dict:
        """
        generate value for a field that are not object or arrays
        """
        # TODO: check for code duplication with regular_field_value
        # field_surrounding is the object the field (_running_schema_property) is part of
        # _running_schema_property is a single field being processed
        # Parent object is a DataObjectFromSchemaBuilder instance where this field was processed in the build() method
        field_surrounding: dict = copy.deepcopy(input_json)
        _field_details = {"required": False}
        if _running_schema_property not in field_surrounding:
            # in case of array[items]
            field_surrounding.update({_running_schema_property: field_surrounding})

        type_ = field_surrounding[_running_schema_property][OBJECT_TYPE_IN_JSON_KEY]
        if isinstance(type_, list):
            _field_details.update({FIELD_TYPE_KEY: type_})
        else:
            _field_details.update({FIELD_TYPE_KEY: [type_]})

        # _field_details.update({"required": False})
        if (
            "required_primitive_properties" in field_surrounding
            and _running_schema_property
            in field_surrounding["required_primitive_properties"]
        ):
            _field_details.update({"required": True})

        if "enum" in field_surrounding[_running_schema_property].keys():
            _field_details.update(
                {"enum": field_surrounding[_running_schema_property]["enum"]}
            )

        if _running_schema_property in get_service_fields_names():
            tmp_field_value = AthenaHelper().get_service_field_value(
                _running_schema_property, input_json
            )
        # TODO : const are not in documentation
        elif "const" in field_surrounding[_running_schema_property]:
            tmp_field_value = field_surrounding[_running_schema_property]["const"]
        else:
            tmp_field_value = AthenaHelper().fake_the_field(
                _field_details, _running_schema_property
            )

        _field_details.update({FIELD_VALUE_KEY: tmp_field_value})

        return _field_details
