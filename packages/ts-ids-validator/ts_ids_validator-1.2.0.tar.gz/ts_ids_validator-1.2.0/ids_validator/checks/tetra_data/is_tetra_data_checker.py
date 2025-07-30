from pydash import get

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.checks.constants import CONVENTION_VERSION, IS_TETRA_DATA_SCHEMA
from ids_validator.ids_node import Node, NodePath


class IsTetraDataSchemaChecker(
    AbstractChecker
):  # pylint: disable=missing-class-docstring)
    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        if node.path == NodePath(("root",)):
            convention_version = get(
                context.artifact.schema, f"properties.{CONVENTION_VERSION}"
            )
            if convention_version:
                if IS_TETRA_DATA_SCHEMA in context.artifact.schema:
                    logs.append(
                        CheckResult.warning(
                            f"Both '{CONVENTION_VERSION}' and '{IS_TETRA_DATA_SCHEMA}' are defined in the IDS."
                            f" '{IS_TETRA_DATA_SCHEMA}' will replace '{CONVENTION_VERSION}' in a future release. "
                            f"Please remove '{CONVENTION_VERSION}' in favor of '{IS_TETRA_DATA_SCHEMA}'."
                        )
                    )
                else:
                    logs.append(
                        CheckResult.warning(
                            f"'{CONVENTION_VERSION}' will be deprecated in a future release."
                            " To mark an IDS as one that should follow Tetra Data modeling conventions, please"
                            f" remove the '{CONVENTION_VERSION}' field and add '{IS_TETRA_DATA_SCHEMA}'"
                            f" as a top-level metadata field and set its value to the boolean `true`."
                        )
                    )

        return logs
