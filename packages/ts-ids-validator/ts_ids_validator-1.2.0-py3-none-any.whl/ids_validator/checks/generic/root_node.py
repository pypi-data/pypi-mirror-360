from typing import Any, Dict

import jsonschema
from pydash import get

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
)
from ids_validator.ids_node import Node, NodePath
from ids_validator.models.validator_parameters import ValidatorParameters
from ids_validator.utils import get_ids_identity, parse_prefixed_version

root_minimum_required = ["@idsType", "@idsVersion", "@idsNamespace"]


def has_valid_version_format(version: str) -> bool:
    """Validate that a version string consists of a "v" followed by a valid SemVer."""

    try:
        parse_prefixed_version(version)
        return True
    except ValueError:
        return False


class RootNodeChecker(AbstractChecker):
    """Validate requirements in the schema root."""

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        if node.path == NodePath(("root",)):
            logs += cls._check_min_required_props(node)

            meta_paths = [f"properties.{name}" for name in root_minimum_required]
            for path in meta_paths:
                prop = get(node, path)
                meta_checks = [get(prop, "type") == "string", get(prop, "const")]
                if not prop or not all(meta_checks):
                    logs.append(
                        CheckResult.critical(
                            f"'{path}' must be present with type 'string' with "
                            f"non-empty 'const'"
                        )
                    )

            if "type" not in node.data:
                logs += [CheckResult.critical("'root.type' is not defined.")]
            elif node.type_ != "object":
                logs += [
                    CheckResult.critical(
                        f"'root.type' is '{node.type_}'. It must be set to 'object'"
                    )
                ]

        return logs

    @staticmethod
    def _check_min_required_props(node: Node):
        logs: CheckResults = []
        if not node.has_required_list:
            logs.append(CheckResult.critical("'root.required' must be a list"))

        if not node.required_contains_values(root_minimum_required):
            logs.append(
                CheckResult.critical(
                    f"'required' must contain: "
                    f"{', '.join(sorted(root_minimum_required))}"
                )
            )

        return logs


class IdsVersionChecker(AbstractChecker):
    """@idsVersion must have a const value of "v" followed by a semantic version."""

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        """Validate the format of @idsVersion."""
        if node.path != NodePath(("root", "properties", "@idsVersion")):
            # On a node which doesn't need this check
            return []

        if "const" not in node:
            return [
                CheckResult.critical("@idsVersion must have a `const` value defined")
            ]
        version = node["const"]
        if not has_valid_version_format(version):
            return [
                CheckResult.critical(
                    "@idsVersion's `const` value must be a string containing a 'v' "
                    "followed by a valid semantic version according to semver.org, "
                    "e.g. 'v1.0.0'. "
                    f"Found: '{version}'."
                )
            ]

        # Valid
        return []


class IdChecker(AbstractChecker):
    """Check that the URI in '$id' matches the expected URL format"""

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:

        if node.path != NodePath(("root",)):
            # On a node which doesn't need this check
            return []

        if "$id" not in node:
            return [
                CheckResult.critical(
                    "schema.json must contain an '$id' key at the top level, with a value "
                    "following this format: "
                    "'https://ids.tetrascience.com/<namespace>/<type>/<version>/schema.json'."
                )
            ]

        schema_id = node["$id"]
        identity = get_ids_identity(context.artifact.schema)

        if schema_id != identity.id_uri:
            return [
                CheckResult.critical(
                    "Unexpected value for '$id' in schema.json. It must have a format of "
                    "'https://ids.tetrascience.com/<namespace>/<type>/<version>/schema.json' "
                    "where the namespace, type and version match the constant values of the "
                    "'@idsNamespace', '@idsType' and '@idsVersion' properties. "
                    f"Expected an '$id' of '{identity.id_uri}', found '{schema_id}'. "
                    "Update either '$id' or the namespace, type and version properties."
                )
            ]

        return []


class MetaSchemaChecker(AbstractChecker):
    """Check that the '$schema' root keyword is valid."""

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        """
        Validate the root `$schema` exists, and the schema is valid against the JSON
        Schema draft 7 spec.
        """
        if node.path != NodePath(("root",)):
            # On a node which doesn't need this check
            return []

        preferred_schema_uri = "http://json-schema.org/draft-07/schema#"
        valid_schema_uris = (
            "http://json-schema.org/draft-07/schema",
            preferred_schema_uri,
        )
        if "$schema" not in node or node["$schema"] not in valid_schema_uris:
            return [
                CheckResult.critical(
                    "schema.json must contain '$schema' in the root object, whose "
                    "value must be the URI for JSON Schema draft 7: "
                    f"'{preferred_schema_uri}'."
                )
            ]

        return cls.validate_meta_schema(context.artifact.schema)

    @staticmethod
    def validate_meta_schema(schema: Dict[str, Any]) -> CheckResults:
        """Validate that the schema follows the JSON Schema draft 7 meta-schema."""
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except jsonschema.SchemaError as exception:
            return [
                CheckResult.critical(
                    "schema.json failed validation against the JSON Schema draft 7 "
                    f"meta-schema at the schema path '{exception.json_path}' while "
                    f"validating this part of the draft 7 schema: '{exception.schema}'."
                )
            ]

        return []
