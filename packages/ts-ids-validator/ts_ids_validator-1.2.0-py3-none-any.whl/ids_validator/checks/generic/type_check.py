from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.ids_node import Node


class TypeChecker(AbstractChecker):
    """Checks if Node has a property `type` and
    is a valid JSON type or array of types
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        type_is_valid, msg = node.has_valid_type
        if not type_is_valid:
            msg = msg if msg else f"Invalid 'type': {node.type_}"
            logs.append(CheckResult.critical(msg))

        properties = node.properties_dict

        if properties is None:
            return logs

        for key, val in properties.items():
            if isinstance(val, dict) and "type" not in val:
                logs += [
                    CheckResult.critical(
                        f"'{node.path}.{key}' has no 'type' defined. This could be "
                        f"caused by a missing 'type', or a typo in a 'type' or '$ref' "
                        f"keyword."
                    )
                ]
        return logs
