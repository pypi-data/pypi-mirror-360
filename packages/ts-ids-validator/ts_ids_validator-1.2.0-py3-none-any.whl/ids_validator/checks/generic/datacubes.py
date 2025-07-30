from enum import Enum
from typing import Optional, Tuple

from pydash import get

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.ids_node import Node, NodePath

VALUE_NODE = "items.properties.measures.items.properties.value"
DIMENSION_NODE = "items.properties.dimensions"
SCALES_NODE = "items.properties.dimensions.items.properties.scale"


class Message(Enum):
    """Datacube checker log messages"""

    TYPE_CHECK = "'type' must be an array"
    REQUIRED_CHECK = (
        "'required' must exist and contain at least ['name','measures','dimensions']"
    )
    PROPERTY_CHECK = "'properties' must exist and contain all the required properties"
    MEASURES_UNDEFINED = "'measures' must be defined and 'measures.type' must be array"
    MEASURE_MIN_MAX_CHECK = "measures.minItems must be equal to measures.maxItems"
    MEASURE_MIN_MAX_MISSING = (
        "'measures' must have both 'minItems' and 'maxItems' defined"
    )
    DIMENSIONS_MIN_MAX_MISSING = (
        "'dimension' must have both 'minItems' and 'maxItems' defined"
    )
    DIMENSIONS_UNDEFINED = (
        "'dimensions' must be defined and 'dimension.type' must be array"
    )
    DIMENSIONS_MIN_MAX_CHECK = (
        "dimensions.minItems must be equal to dimensions.maxItems"
    )
    MEASURES_VALUES_DIMENSIONALITY_ERROR = (
        "'measures.value': Dimensionality of data stored in `measures.value` must be "
        "equal to `dimensions.minItems` or `dimensions.maxItems`"
    )
    MEASURES_VALUES_TYPE_ERROR = (
        "'measures.value': Type Error. Type must be either be `number` or `string`. "
        "It can be nullable"
    )
    MEASURES_VALUES_NESTED_ARRAY_TYPE_ERROR = (
        "'measures.value': Type Error. Nested objects/dicts must be `array` types"
    )
    DIMENSIONS_SCALE_TYPE_ERROR = "'dimensions.scale': Type Error. Type must be 'array'"
    DIMENSIONS_SCALE_ITEMS_TYPE_ERROR = (
        "'dimensions.scale.items': Type Error. Type must be 'number'"
    )

    def __str__(self):
        return self.value


class DatacubesChecker(AbstractChecker):
    """It run only when the node path is "root.properties.datacubes" and
    checks for following:
        - `type` of `datacubes` must be an array
        - Minimum required properties are present.
        - `minItems == maxItems` for `dimensions` and `measures`
        - Nesting levels of `measures.value` is equal to `dimensions.maxItem`
        - Type of nested levels must be an array except for the innermost array.
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        if node.path == NodePath(("root", "properties", "datacubes")):
            logs += cls.check_datacubes_type(node)
            logs += cls.check_datacubes_properties(node)
            logs += cls.check_datacubes_measures(node)
            logs += cls.check_datacubes_dimensions(node)
            logs += cls.check_measures_values_dimensions(node)
            logs += cls.check_measures_values_type(node)
            logs += cls.check_dimensions_scale_type(node)

        return logs

    @staticmethod
    def check_datacubes_type(datacubes: Node) -> CheckResults:
        """Check that `datacubes` has type `array`"""
        logs: CheckResults = []
        if get(datacubes, "type") != "array":
            logs += [CheckResult.critical(Message.TYPE_CHECK.value)]
        return logs

    @staticmethod
    def check_datacubes_properties(datacubes: Node) -> CheckResults:
        """It checks for following:

        - `datacubes.items: dict` exists.
        - `required: list` must at least contain `minimum_properties`
        - `properties: dict` must at least contain `minimum_properties`

        where `minimum_properties = {'name', 'dimensions', 'measures'}`

        Args:
            datacubes (Node): Root level datacubes property

        Returns:
            list: list of failed check
        """
        logs: CheckResults = []
        items = datacubes.get("items")

        if not items or not isinstance(items, dict):
            logs += [
                CheckResult.critical(Message.REQUIRED_CHECK.value),
                CheckResult.critical(Message.PROPERTY_CHECK.value),
            ]
            return logs

        items = Node(items)
        minimum_required = {"name", "dimensions", "measures"}

        if not items.required_contains_values(minimum_required):
            logs += [CheckResult.critical(Message.REQUIRED_CHECK.value)]

        if not items.has_properties(list(minimum_required)):
            logs += [CheckResult.critical(Message.PROPERTY_CHECK.value)]

        return list(set(logs))

    @staticmethod
    def check_datacubes_measures(datacubes: Node) -> CheckResults:
        """It checks for following:

        - `datacubes.measures` is defined in schema
        - `datacubes.measrues: dict` must contain `minItems`
        and `maxItems`
        - `measures.minItems` must be equal to `measures.maxItems`

        Args:
            datacubes (Node): Root level datacubes property

        Returns:
            list: list of failed check
        """
        logs: CheckResults = []
        measures = get(datacubes, "items.properties.measures")
        if not measures:
            logs += [CheckResult.critical(Message.MEASURES_UNDEFINED.value)]
            return logs

        if measures.get("type") != "array":
            logs += [CheckResult.critical(Message.MEASURES_UNDEFINED.value)]

        min_items = get(measures, "minItems")
        max_items = get(measures, "maxItems")

        if all([min_items, max_items]):
            if min_items != max_items:
                logs += [CheckResult.critical(Message.MEASURE_MIN_MAX_CHECK.value)]
        else:
            logs += [CheckResult.critical(Message.MEASURE_MIN_MAX_MISSING.value)]
        return list(set(logs))

    @staticmethod
    def check_datacubes_dimensions(datacubes: Node) -> CheckResults:
        """It checks for following:

        - `datacubes.dimesions` is defined in schema
        - `datacubes.dimesions: dict` must contain `minItems`
        and `maxItems`
        - `dimesions.minItems` must be equal to `dimesions.maxItems`

        Args:
            datacubes (Node): Root level datacubes property

        Returns:
            list: list of failed check
        """
        logs: CheckResults = []
        dimensions = get(datacubes, "items.properties.dimensions")
        if not dimensions:
            logs += [CheckResult.critical(Message.DIMENSIONS_UNDEFINED.value)]
            return logs

        if dimensions.get("type") != "array":
            logs += [CheckResult.critical(Message.DIMENSIONS_UNDEFINED.value)]

        min_items = get(dimensions, "minItems")
        max_items = get(dimensions, "maxItems")

        if all([min_items, max_items]):
            if min_items != max_items:
                logs += [CheckResult.critical(Message.DIMENSIONS_MIN_MAX_CHECK.value)]
        else:
            logs += [CheckResult.critical(Message.DIMENSIONS_MIN_MAX_MISSING.value)]

        return list(set(logs))

    @classmethod
    def check_measures_values_dimensions(cls, datacubes: Node) -> CheckResults:
        """Ensures the nested depth of `measures.value` is equal to
        `dimensions.minItems` or `dimensions.maxItems`
        Args:
            datacubes (Node): Root level datacubes property

        Returns:
            list: list of failed check
        """
        logs: CheckResults = []
        values = get(datacubes, VALUE_NODE)
        dimensions = get(datacubes, DIMENSION_NODE)

        num_dimensions = get(dimensions, "minItems") or get(dimensions, "maxItems")
        if not (
            (values and isinstance(values, dict))
            and (dimensions and isinstance(dimensions, dict))
            and num_dimensions
        ):
            logs += [
                CheckResult.critical(Message.MEASURES_VALUES_DIMENSIONALITY_ERROR.value)
            ]
            return logs

        value_dimensions = cls.get_value_dimensions(values)

        if num_dimensions != value_dimensions:
            logs += [
                CheckResult.critical(Message.MEASURES_VALUES_DIMENSIONALITY_ERROR.value)
            ]

        return list(set(logs))

    @classmethod
    def check_measures_values_type(cls, datacubes: Node) -> CheckResults:
        """It makes sure that `measures.values` is a nested `dicts` of `array`,
        with innermost `dict` being a `number` or `string` type, nullable or not.

        Args:
            datacubes (Node): The root level datacubes property

        Returns:
            list: list of failed checks
        """
        logs: CheckResults = []
        values = Node(get(datacubes, VALUE_NODE) or {})
        error, msg = cls._check_measures_value_for_type_error(values)
        if error:
            logs += [CheckResult.critical(msg.value)]
        return logs

    @staticmethod
    def check_dimensions_scale_type(datacubes: Node) -> CheckResults:
        """Check type for `dimensions.scale`. It must be
        nested inside an `array` with type equals `number`

        Args:
            datacubes (Node): The root level datacubes property

        Returns:
            list: list of failed check
        """
        logs: CheckResults = []
        scale = get(datacubes, SCALES_NODE, {})
        if not scale:
            logs += [CheckResult.critical(Message.DIMENSIONS_SCALE_TYPE_ERROR.value)]

        if get(scale, "type") != "array":
            logs += [CheckResult.critical(Message.DIMENSIONS_SCALE_TYPE_ERROR.value)]

        valid_items_type = ["number", ["null", "number"], ["number", "null"]]
        if get(scale, "items.type") not in valid_items_type:
            logs += [
                CheckResult.critical(Message.DIMENSIONS_SCALE_ITEMS_TYPE_ERROR.value)
            ]

        return list(set(logs))

    @classmethod
    def get_value_dimensions(cls, node: Node) -> int:
        """Calculate Depth of nesting only for `measures.value`.

        Args:
            node (dict): `dict` for `measures.value`

        Returns:
            int: Depth/dimensions of `measures.value`
        """

        node_items = get(node, "items")
        if node_items:
            return 1 + cls.get_value_dimensions(
                node_items,
            )
        return 0

    @classmethod
    def _check_measures_value_for_type_error(
        cls, node: dict
    ) -> Tuple[bool, Optional[Message]]:
        """This is a helper function for valdating type of `measures.value`.
        It must be nested inside `array` types with innermost
        being either be a `number` or `string`, nullable or not.
        Args:
            node (dict): `measures.value`

        Returns:
            bool, Message: Return (False, None) if there is no error.
            Return (True, Message) in case validation fails
        """
        node_items = get(node, "items")
        node_type = get(node, "type")

        if node_items:
            if node_type != "array":
                return True, Message.MEASURES_VALUES_NESTED_ARRAY_TYPE_ERROR
            return cls._check_measures_value_for_type_error(node_items)

        if isinstance(node_type, list):
            if sorted(node_type) not in [
                sorted(["null", "string"]),
                sorted(["null", "number"]),
            ]:
                return True, Message.MEASURES_VALUES_TYPE_ERROR
        elif node_type not in ["string", "number"]:
            return True, Message.MEASURES_VALUES_TYPE_ERROR

        return False, None
