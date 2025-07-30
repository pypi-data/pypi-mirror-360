import re
from typing import Any, Dict

import deepdiff
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.helpers.config import global_config
from ids_validator.ids_node import Node
from ids_validator.utils import major_version_is_equal, read_schema

TEMPLATES_DIR = global_config.project_path / "ids_validator" / "templates"
ATHENA_TEMPLATE = TEMPLATES_DIR / "athena.json"


class AthenaChecker(AbstractChecker):
    """Athena Checks run only at the root level of IDS Schema.
    It checks for following:
    - All the partition paths mentioned in `athena.js` are present in `schema.js`
    - Naming conflict between `path` and `name` of athena partition
    - Ancestor of any `partition.path` is not an array
    - breaking changes
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        """Run Athena-related validation of athena.json and schema.json"""
        logs: CheckResults = []
        if node.name == "root":
            athena = context.artifact.athena

            schema_node = context.root_node()

            athena_schema_results = cls._validate_athena_schema(athena)
            if athena_schema_results:
                # Stop here - the rest of the checks require a valid athena.json
                return athena_schema_results

            partition_paths = cls.get_athena_partitions_path(athena)
            logs += cls.check_all_paths_exist(partition_paths, schema_node)
            logs += cls.check_paths_nested_inside_array(partition_paths, schema_node)
            logs += cls.check_path_and_name_conflicts(athena)

            if context.previous_artifact is not None:
                if major_version_is_equal(
                    previous_schema=context.previous_artifact.schema,
                    new_schema=context.artifact.schema,
                ):
                    logs += cls.validate_no_partition_change(
                        context.previous_artifact.athena, athena
                    )

        return logs

    @classmethod
    def check_all_paths_exist(cls, partition_paths: list, ids: Node) -> CheckResults:
        logs: CheckResults = []
        missing = [path for path in partition_paths if not cls.path_exists(path, ids)]
        if missing:
            logs.append(
                CheckResult.critical(
                    f"athena.json: Cannot find following properties in IDS: "
                    f"{sorted(missing)}"
                )
            )
        return logs

    @staticmethod
    def validate_no_partition_change(
        previous_partition_paths: dict,
        new_partition_paths: dict,
    ) -> CheckResults:
        """
        Check that partition definitions are the same in  athena.json between schema versions.
        """
        logs: CheckResults = []

        diff = deepdiff.DeepDiff(
            previous_partition_paths, new_partition_paths, ignore_order=True
        )
        if diff:
            logs.append(
                CheckResult.critical(
                    f"athena.json partition definitions are different but the new schema does not have a major version change. athena.json diff:"
                    f"{diff.to_dict()}"
                )
            )
        return logs

    @classmethod
    def check_paths_nested_inside_array(
        cls, partition_paths: list, ids: Node
    ) -> CheckResults:
        logs: CheckResults = []
        existing_partition_paths = [
            path for path in partition_paths if cls.path_exists(path, ids)
        ]
        paths_nested_inside_array = sorted(
            [
                path
                for path in existing_partition_paths
                if cls.path_nested_in_array(path, ids)
            ]
        )
        if paths_nested_inside_array:
            logs.append(
                CheckResult.critical(
                    (
                        f"athena.json: Following paths are either array type or nested "
                        f"in array types: {paths_nested_inside_array}"
                    )
                )
            )
        return logs

    @classmethod
    def check_path_and_name_conflicts(cls, athena_dict: dict) -> CheckResults:
        """Check and log if there is a conflict in `partition.path`
        and `partition.name`.

        A conflict occurs when normalized value of the `partition.path` is equal to
        `partition.name`.

        Normalized path is obtained by replacing "." with "_" in `partiions[*].path`

        Args:
            athena_dict (Node): athena.json loaded as a python dict
        """
        logs: CheckResults = []
        partitions_name = set(cls.get_athena_partitions_name(athena_dict))
        normalized_paths = set(
            [
                cls.normalize_path_name(path)
                for path in cls.get_athena_partitions_path(athena_dict)
            ]
        )
        intersection = partitions_name.intersection(normalized_paths)
        if intersection:
            logs.append(
                CheckResult.critical(
                    f"athena.json: Following names are conflicting with path: "
                    f"{', '.join(intersection)}"
                )
            )
        return logs

    @staticmethod
    def path_nested_in_array(path: str, ids: Node):
        """Traverse on node's path and return True if any
        ancestor is an array. Except if the ancestor is Top-Level
        IDS property.
        """
        nodes = path.split(".")
        parent = ids
        for idx, node in enumerate(nodes):
            children = parent.properties_dict
            child = children.get(node)
            if (parent["type"] == "array" and idx > 1) or (
                child["type"] == "array" and idx > 0
            ):
                return True

            parent = Node(child)
        return False

    @staticmethod
    def path_exists(path: str, ids: Node) -> bool:
        """Given a path eg `systems.firmwares.types`,
        make sure it exists in root level ids when crawled
        form properties to properties.

        Args:
            path (str): A fully qualified path, delimited by "."
            ids (Node): root IDS node

        Returns:
            bool: True if path exists else false
        """
        nodes = path.split(".")
        parent = ids
        for node in nodes:
            children = parent.properties_dict or {}
            child = children.get(node)
            if not child:
                return False
            parent = Node(child)
        return True

    @staticmethod
    def get_athena_partitions_path(athena_schema) -> list:
        """From `athena.json`, get each `partitions[*].path`."""
        partitions = athena_schema.get("partitions", {})
        paths = [partition.get("path") for partition in partitions]
        return paths

    @staticmethod
    def get_athena_partitions_name(athena_schema) -> list:
        """From `athena.json`, get each `partitions[*].name`."""
        partitions = athena_schema.get("partitions", {})
        names = [partition.get("name") for partition in partitions]
        return names

    @staticmethod
    def normalize_path_name(path_name):
        """
        Weird-partition!@name -> weird_partition_name
        @fileId -> fileid
        project.name -> project_name
        """
        normalized_path = re.sub("[^A-Za-z0-9]+", "_", path_name)
        normalized_path = re.sub("[_]+", "_", normalized_path)
        normalized_path = normalized_path.lstrip("_")
        normalized_path = normalized_path.lower()
        return normalized_path

    @staticmethod
    def _validate_athena_schema(athena: Dict[str, Any]):
        logs: CheckResults = []

        template_schema = read_schema(ATHENA_TEMPLATE)
        try:
            validate(athena, template_schema)
        except ValidationError as exception:
            logs += [
                CheckResult.critical(
                    "athena.json does not have the expected content structure, "
                    f"validation failed with error message: {exception.message}"
                )
            ]
        return logs
