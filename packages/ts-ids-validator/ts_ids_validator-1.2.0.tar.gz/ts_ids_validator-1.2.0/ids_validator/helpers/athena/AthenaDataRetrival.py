import copy

from ids_validator.helpers.athena.helpers.get_test_objects import get_test_objects
from ids_validator.helpers.helpers_methods import snake_case


class AthenaDataRetrival:
    def __init__(self):
        self._schema_response = {}
        self._null_result = None
        self.schema_name = None

    def set_null_result(self, value: str):
        """
        TODO: move to ENUM
        :param self: Used to Access the class attributes.
        :param value: can be
                        "Partial Allowed" - random setting null for fields that are xxx_nullable type
                        "All Allowed"       set all fields that are xxx_nullable type to null
                        "All Not Allowed":  set all fields that are NOT xxx_nullable type to null
                        anything else       no null field would be generated

        """
        self._null_result = value

    def set_schema_response(self, o):
        self._schema_response = copy.deepcopy(o)
        self.schema_name = snake_case(
            f"{self._schema_response['namespace']}"
            f"/{self._schema_response['slug']}"
            f":{self._schema_response['version']}"
        )

    def validate_schema(self) -> None:
        # Validation occurs in the following call
        get_test_objects(self._schema_response)

    def get_table_prefix(self, slug: str, version: str):
        # Raises exception if version str does not contain "." in an invalid IDS
        _cut_version = version[: version.index(".")]
        string_to_return = slug.replace("-", "_")
        string_to_return += "_"
        string_to_return += _cut_version
        string_to_return += "_"
        return string_to_return
