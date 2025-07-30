from typing import Any, Dict, List, Optional, Type

from rich.console import Console

from ids_validator.checks import tetra_data
from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    Log,
)
from ids_validator.checks.generic import (
    AdditionalPropertyChecker,
    AthenaChecker,
    DatacubesChecker,
    RequiredPropertiesChecker,
    RootNodeChecker,
    TypeChecker,
)
from ids_validator.checks.generic.athena_column_name_resolution_check import (
    AthenaColumnNameResolutionCheck,
)
from ids_validator.checks.generic.athena_normalized_field_name import (
    AthenaNormalizedFieldNameChecker,
)
from ids_validator.checks.generic.elasticsearch import validate_elasticsearch_json
from ids_validator.checks.generic.expected import ExpectedChecker
from ids_validator.checks.generic.reserved_property_names import ReservedNameChecker
from ids_validator.checks.generic.root_node import (
    IdChecker,
    IdsVersionChecker,
    MetaSchemaChecker,
)
from ids_validator.checks.generic.schema_breaking_change import (
    CSVAthenaBreakingChangeChecker,
    format_csv_athena_failures,
)
from ids_validator.checks.schema_evolution.merge_compatible import (
    MergeCompatibilityChecker,
)
from ids_validator.checks.tetra_data.nodes_checker import ENFORCED_NODE_CHECKS
from ids_validator.ids_node import Node, NodePath
from ids_validator.models.validator_parameters import ValidatorParameters

generic_checks: List[Type[AbstractChecker]] = [
    AdditionalPropertyChecker,
    DatacubesChecker,
    RequiredPropertiesChecker,
    RootNodeChecker,
    IdsVersionChecker,
    IdChecker,
    MetaSchemaChecker,
    TypeChecker,
    ExpectedChecker,
    AthenaChecker,
    AthenaColumnNameResolutionCheck,
    AthenaNormalizedFieldNameChecker,
    ReservedNameChecker,
    MergeCompatibilityChecker,
    CSVAthenaBreakingChangeChecker,
]

tetra_data_checks = (
    generic_checks
    + tetra_data.ENFORCED_NODE_CHECKS
    + [
        tetra_data.IsTetraDataSchemaChecker,
        tetra_data.SnakeCaseChecker,
        tetra_data.SampleNodeChecker,
        tetra_data.SystemNodeChecker,
        tetra_data.UserNodeChecker,
        tetra_data.RelatedFilesChecker,
    ]
)


ROOT_NODE_KEY = "root"
BULK_NODE_KEY = "bulk"

default_console = Console()


class Validator:  # pylint: disable=too-many-instance-attributes
    """Main class that runs validation of IDS."""

    def __init__(
        self,
        validator_parameters: ValidatorParameters,
        checks_list: Optional[List[Type[AbstractChecker]]] = None,
        console: Console = default_console,
    ):
        self.is_tetra_data_schema = validator_parameters.artifact.is_tetra_data_schema
        if checks_list is not None:
            # A non-standard set of checks has been specified
            self.display_info = False
            self.checks_list = checks_list
        else:
            self.display_info = True
            self.checks_list = (
                tetra_data_checks if self.is_tetra_data_schema else generic_checks
            )

        self.parameters = validator_parameters
        self.console = console
        self.property_failures: Dict[str, CheckResults] = {}
        self.has_critical_failures = False
        self.csv_athena_logs: CheckResults = []

        self.missing_nodes: List[NodePath] = []
        if self.is_tetra_data_schema:
            for node_checker in tetra_data.ENFORCED_NODE_CHECKS:
                self.missing_nodes += node_checker.enforced_nodes

    def _traverse(self, schema: dict, path: NodePath = NodePath((ROOT_NODE_KEY,))):
        node = Node(schema=schema, path=path)

        failures = []
        for checker in self.checks_list:
            if checker.bulk_checker:
                continue

            if checker is CSVAthenaBreakingChangeChecker:
                self.csv_athena_logs += checker.run(node, self.parameters)
                continue

            if checker in ENFORCED_NODE_CHECKS:
                if node.path.has_prefix(checker.reserved_path_prefix):
                    if node.path in self.missing_nodes:
                        self.missing_nodes.remove(node.path)
                else:
                    continue
            failures += checker.run(node, self.parameters)

        if failures:
            self.property_failures[str(node.path)] = list(failures)
            self.log(failures, str(node.path))

        for key, value in schema.items():
            if isinstance(value, dict):
                self._traverse(value, path=path.join(key))

    def _bulk_validation(self, schema: Dict[str, Any]):
        node = Node(schema=schema, path=NodePath(("root",)))
        failures = []
        for checker in self.checks_list:
            if checker.bulk_checker:
                failures += checker.run(node, context=self.parameters)

        if failures:
            self.property_failures["bulk"] = list(failures)
            self.log(failures, "bulk")

    def display_validator_info(self):
        """Display information at the start of validation."""
        info_logs = [
            CheckResult.info(
                f"Validating IDS artifact: {self.parameters.artifact.identity}"
            )
        ]

        if self.parameters.artifact_range is not None:
            versions = [a.identity.version for a in self.parameters.artifact_range]
            git_tags = [a.git_tag for a in self.parameters.artifact_range]
            info_logs.append(
                CheckResult.info(
                    "Versions being used for versioning compatibility checks: "
                    f"{versions if versions else 'None (this is the first schema with this major version)'}"
                    + (f" from git tags {git_tags}" if any(git_tags) else "")
                )
            )
        info_logs.append(
            CheckResult.info(
                "Using Tetra Data conventions validator"
                if self.is_tetra_data_schema
                else "Using platform requirements validator"
            )
        )
        self.log(info_logs, "Validation info", sort_logs=False)

    def validate_ids(self):
        """Validate full IDS using ValidatorParameters passed during class construction."""
        if self.display_info:
            # Only show info for complete validation, not e.g. during unit testing
            self.display_validator_info()
        self._traverse(schema=self.parameters.artifact.schema)

        if self.missing_nodes:
            # Including spaces in below for formatting with self.console.print
            format_spaces = " " * 8
            missing_nodes = f"\n{format_spaces}".join(
                str(path) for path in self.missing_nodes
            )
            result = [
                CheckResult.critical(
                    f"The following fields must be included but are missing:\n{format_spaces}{missing_nodes}"
                )
            ]
            check_name = "Required nodes missing"
            self.log(result, check_name)
            self.property_failures[check_name] = result

        self._bulk_validation(schema=self.parameters.artifact.schema)

        if self.csv_athena_logs:
            check_name = "CSV Athena versioning"
            formatted_failures = [
                format_csv_athena_failures(
                    self.csv_athena_logs,
                    # previous_artifact cannot be `None` inside this if statement
                    self.parameters.previous_artifact.identity,  # type: ignore
                    self.parameters.artifact.identity,
                )
            ]
            self.property_failures[check_name] = formatted_failures
            self.log(formatted_failures, check_name)

        es_validation_errors = validate_elasticsearch_json(self.parameters)
        if es_validation_errors:
            check_name = "elasticsearch.json"
            self.log(es_validation_errors, check_name)
            self.property_failures[check_name] = es_validation_errors

    def log(
        self,
        messages: CheckResults,
        property_name: str,
        prop_color: str = "red",
        sort_logs: bool = True,
    ):
        """Add message to the validation log."""
        self.console.print(f"[b u  {prop_color}]{property_name}[/b u {prop_color}]:")

        for result in sorted(messages) if sort_logs else messages:
            if result.level == Log.CRITICAL:
                self.has_critical_failures = True

            msg_level = {
                Log.INFO: "Info",
                Log.WARNING: "Warning",
                Log.CRITICAL: "Error",
            }[result.level]
            msg_color = "yellow" if result.level == Log.CRITICAL else "white"
            self.console.print(
                f"[italic {msg_color}]    {msg_level}: {result.message}[italic {msg_color}]"
            )
