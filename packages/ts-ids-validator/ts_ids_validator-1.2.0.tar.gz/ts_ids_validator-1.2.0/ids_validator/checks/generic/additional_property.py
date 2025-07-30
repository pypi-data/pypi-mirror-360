from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
)
from ids_validator.ids_node import Node
from ids_validator.models.validator_parameters import ValidatorParameters


class AdditionalPropertyChecker(AbstractChecker):
    """If a node is object type, then it have additionalProperties
    defined as one of the key and it must be set to False

    If type is not object or is not defined, additionalProperties
    must not exist.
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []

        if node.get("type") != "object" and "additionalProperties" in node:
            logs.append(
                CheckResult.critical(
                    "'additionalProperties' can only be defined for 'type = object'"
                )
            )

        if (
            node.get("type") == "object"
            and node.get("additionalProperties") is not False
        ):
            logs.append(
                CheckResult.critical(
                    "'additionalProperties' must be present and set to 'false' for "
                    "'object' types"
                )
            )

        return logs
