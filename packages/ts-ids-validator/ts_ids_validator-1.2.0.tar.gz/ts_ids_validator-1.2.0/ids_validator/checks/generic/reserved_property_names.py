from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
)
from ids_validator.ids_node import Node
from ids_validator.models.validator_parameters import ValidatorParameters


class ReservedNameChecker(AbstractChecker):
    """
    Properties cannot use certain reserved names which are used as SQL column names
    on TDP.
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        if not node.path.in_properties:
            # This isn't a schema node containing properties
            return []

        reserved_names = ("uuid", "parent_uuid")
        invalid_names = [name for name in reserved_names if name in node]

        if invalid_names:
            return [
                CheckResult.critical(
                    "Properties cannot have these names which are reserved for Athena "
                    f"in TDP: {reserved_names}. "
                    "Remove or rename these properties present in this schema: "
                    f"{invalid_names}."
                )
            ]

        return []
