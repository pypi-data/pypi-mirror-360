from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.ids_node import Node, NodePath

ignored_paths = [
    NodePath(
        (
            "root",
            "properties",
            "related_files",
            "items",
            "properties",
            "pointer",
            "properties",
            "fileId",
        )
    ),
    NodePath(
        (
            "root",
            "properties",
            "related_files",
            "items",
            "properties",
            "pointer",
            "properties",
            "fileKey",
        )
    ),
]

DEFINITIONS_PATH = NodePath(("root", "definitions"))


class SnakeCaseChecker(AbstractChecker):
    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []

        if node.path in ignored_paths or node.path.has_prefix(DEFINITIONS_PATH):
            return logs

        name: str = node.name
        checks = [
            name.islower() or name.isdigit(),
            len(name.split()) == 1,
            all([x.isalnum() for x in _filter_empty_string(name.split("_"))]),
        ]
        if not name.startswith("@") and not all(checks):
            logs.append(
                CheckResult.critical(f"'{node.name}' should be named as snake_case.")
            )

        return logs


def _filter_empty_string(str_list):
    return [str_val for str_val in str_list if str_val != ""]
