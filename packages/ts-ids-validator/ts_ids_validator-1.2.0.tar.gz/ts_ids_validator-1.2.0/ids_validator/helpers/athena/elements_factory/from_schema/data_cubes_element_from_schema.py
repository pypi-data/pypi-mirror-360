from typing import List

from ids_validator.helpers.athena.athena_logger import athena_logger
from ids_validator.helpers.athena.elements_factory.element_interface import (
    ElementToWorkWith,
)


class DataCubesElementFromSchema(ElementToWorkWith):
    def __init__(self):
        self.logger = athena_logger("DataCubesElement")

    def generate_value(
        self, _running_schema_property, input_json, parent_object
    ) -> List:
        """generate value for a field that are not object or arrays
        Excluded till https://tetrascience.atlassian.net/browse/DL-747
        """
        self.logger.debug(f"skipping {_running_schema_property}")
        return []
