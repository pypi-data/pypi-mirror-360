from copy import deepcopy

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.helpers.athena.AthenaDataRetrival import AthenaDataRetrival
from ids_validator.helpers.athena.exceptions import (
    InvalidColumn,
    InvalidSchemaDefinition,
    MergeException,
    UnknownFieldType,
)
from ids_validator.ids_node import Node


class AthenaColumnNameResolutionCheck(AbstractChecker):
    """Checks if Node has a property `type` and
    is a valid JSON type or array of types
    """

    bulk_checker = True

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []

        schema_processor = AthenaDataRetrival()

        schema_processor.set_null_result("none")
        try:
            node.update({"version": node["properties"]["@idsVersion"]["const"]})
            node.update({"slug": node["properties"]["@idsType"]["const"]})
            node.update({"namespace": node["properties"]["@idsNamespace"]["const"]})
            node.update({"schema": deepcopy(context.artifact.schema)})
            node.update({"athena": deepcopy(context.artifact.athena)})
            node.update(
                {
                    "table_prefix": schema_processor.get_table_prefix(
                        node["slug"], node["version"]
                    )
                }
            )
        except (KeyError, ValueError):
            # Other validator messages have more detailed info about fixing these fields
            return [
                CheckResult.critical(
                    "Validating Tetra SQL column names requires a valid @idsNamespace, @idsType and @idsVersion"
                )
            ]

        schema_processor.set_schema_response(node)

        # TODO: streamline comparators. We have now 4, it should be 4 in 3 in 2 in 1

        try:
            schema_processor.validate_schema()
        except (
            MergeException,
            UnknownFieldType,
            KeyError,
            InvalidSchemaDefinition,
            InvalidColumn,
        ) as exp:
            message = "Error in Tetra SQL column name resolution checks.\n" + "\n".join(
                (str(message) for message in exp.args)
            )
            logs.append(CheckResult.critical(message))

        return logs
