from typing import List

import deepdiff
import pydash

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.checks.constants import ROOT_PROPERTIES
from ids_validator.ids_node import Node, NodePath
from ids_validator.utils import IdsIdentity, major_version_is_equal


def compare_nodes(node: Node, previous_node_schema: dict) -> dict:
    """Compare the same IDS schema node from the previous and current IDS versions

    Returns a dict of differences, excluding differences which are allowed, such as
    removing properties from the "required" schema metadata.
    """

    # we are validating only properties section of schema that is located in root.properties
    if not node.path.has_prefix(ROOT_PROPERTIES):
        return {}

    if node.path == NodePath(("root", "properties", "@idsVersion")):
        return {}

    if node.path.in_properties:
        # we are tracking changes for all keys in 'properties' section
        return deepdiff.DeepDiff(
            previous_node_schema.keys(),
            node.data.keys(),
            ignore_order=True,
        ).to_dict()


def format_csv_athena_failures(
    failures: List[CheckResult], previous_ids: IdsIdentity, current_ids: IdsIdentity
) -> CheckResult:
    """
    Format the resulting CheckResult instances produced by SchemaBreakingChangeChecker.run()
    into a single CheckResult instance for user readability.

    Args:
        failures: List of CheckResult instances produce by SchemaBreakingChangeChecker.run()
        previous_ids: Previous IDS IdsIdentity instance
        current_ids: Current IDS IdsIdentity instance

    Returns:
        Single CheckResult instance containing a single header with all failures included
    """
    failure_header = (
        f"The previous ({previous_ids.version}) and current ({current_ids.version}) IDSs "
        "contain changes which would not appear in CSV-backed Athena tables with a "
        "minor or patch update. "
        "If you intend to access any added columns in CSV-backed Athena, bump the major "
        "version of the IDS."
    )
    path_failures = "\n\n".join([failure.message for failure in failures])

    return CheckResult.warning(f"{failure_header}\n{path_failures}")


class CSVAthenaBreakingChangeChecker(AbstractChecker):
    """Checks if there is no breaking changes introduced.
    Breaking changes:
    - add/remove field in properties section
    - change field type excluding adding 'null'
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        if context.previous_artifact is None:
            # Can't check for breaking changes when there is no previous schema
            return logs

        previous_schema = context.previous_artifact.schema
        if not major_version_is_equal(previous_schema, context.artifact.schema):
            return logs

        # Use a unique default value so that `None` is treated as a valid return value
        missing_value = object()
        previous_node_schema = pydash.get(
            obj=previous_schema,
            path=str(node.path).replace("root.", "", 1),
            default=missing_value,
        )
        if previous_node_schema is missing_value:
            # We would get here if we have key in new schema that is not exist in previous schema.
            # That would be identified with deepdiff on previous step of recursion, so we do not need to report it here.
            return logs

        current_vs_previous = compare_nodes(
            node=node, previous_node_schema=previous_node_schema
        )

        if current_vs_previous:
            diff_string = str(current_vs_previous).replace("root[", f"{node.path}[")
            logs += [
                CheckResult.warning(
                    f"\t'{node.path}' contains the following change which affects CSV-backed Athena tables:"
                    f"\n\t\t{diff_string}."
                )
            ]
            return logs

        return logs
