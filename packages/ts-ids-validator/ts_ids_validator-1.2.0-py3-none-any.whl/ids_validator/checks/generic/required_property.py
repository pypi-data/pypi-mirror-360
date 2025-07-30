from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.ids_node import Node


class RequiredPropertiesChecker(AbstractChecker):
    """If a node has defined `required: list` and `properties: dict`,
    this check makes sure, every value in `required` list is present in
    `properties.keys()`

    logs a failure if the check fails.
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        if node.has_required_list:
            missing_properties = node.missing_properties
            if missing_properties:
                logs.append(
                    CheckResult.critical(
                        f"Required Properties are missing: {missing_properties}"
                    )
                )

        return logs
