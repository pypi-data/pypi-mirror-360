import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal, Tuple, Type, Union

import pyarrow as pa
from typing_extensions import Self

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.checks.schema_evolution.schema_conversion import get_pyarrow_schema
from ids_validator.ids_node import Node
from ids_validator.models.json_schema import JSONSchema, JSONSchemaType


@dataclass
class ComparisonSuccess:
    compatible: Literal[True] = True


@dataclass
class ComparisonFailure:
    reason: str = ""
    compatible: Literal[False] = False


ComparisonResult = Union[ComparisonSuccess, ComparisonFailure]


class MergeIncompatible(ValueError):
    pass


REVERSE_TYPE_MESSAGE_MAP: Dict[str, JSONSchemaType] = {
    "bool": "boolean",
    "int64": "integer",
    "double": "number",
    "string": "string",
    "struct": "object",
    "list": "array",
}


def transform_pyarrow_message(message: str):
    """Parse the unify_schema error message into a shorter form

    Pyarrow's unify_schemas error message follows this pattern:

    ```
    Unable to merge: Field A has incompatible types: {type_before} vs {type_after}
    ```

    If `type_before` and `type_after` are both container types like `struct<{children}>`
    then there will be further messages drilling down into child elements until it
    reaches a primitive type, e.g.:

    ```
    Unable to merge: Field {A} has incompatible types: {B: {subtype_before}, ...} vs {B: {subtype_after}}
    Unable to merge: Field {B} has incompatible types: int vs struct<...>
    ```

    This message is parsed, extracting each `Field {name}` and everything after
    `incompatible types:`. Then a new message is made formatted like:

    ```
    Cannot merge: methods.item.calibration.item.curves.item.average_cal_points.item: string vs struct
    ```

    Note if the final type comparison contains a container type like `struct<...>`, its
    children `<...>` are not included.
    """
    matches: List[Tuple[str, str]] = re.findall(
        r"Unable to merge: Field ([^ ]+) has incompatible types: (.+?)(?=: Unable to merge:|$):? ?",
        message,
    )
    if not matches:
        # Unable to parse the error message as expected, just return the full message
        return message
    field_path = ".".join(m[0].strip() for m in matches)
    type_before, type_after = matches[-1][1].split(" vs ")
    # Strip child types if there are any
    type_before = type_before.split("<")[0]
    type_after = type_after.split("<")[0]
    # Replace with JSON Schema type name, falling back to pyarrow type name if unknown
    type_before = REVERSE_TYPE_MESSAGE_MAP.get(type_before, type_before)
    type_after = REVERSE_TYPE_MESSAGE_MAP.get(type_after, type_before)
    return f"Cannot merge schemas: '{field_path}' changed from {type_before} to {type_after}"


def pyarrow_merge(
    schemas: Iterable[pa.Schema],
) -> ComparisonResult:
    try:
        return pa.unify_schemas(schemas)
    except pa.ArrowTypeError as e:
        raise MergeIncompatible(transform_pyarrow_message(str(e)))


@dataclass
class MergedSchema:
    """Represents the merged pyarrow schema from a collection of schemas."""

    versions: Tuple[Union[str, None], ...]
    schema: pa.Schema
    group_reason: str = ""
    """The reason this group was not merged with the previous group"""

    def merge(self, schema: JSONSchema) -> Self:
        """
        Merge a JSON Schema into the current pyarrow schema, return the new schema.
        """
        versions = (
            *self.versions,
            schema.get("properties", {}).get("@idsVersion", {}).get("const", None),
        )
        return type(self)(
            versions=versions,
            schema=pyarrow_merge([self.schema, get_pyarrow_schema(schema)]),
            group_reason=self.group_reason,
        )

    @classmethod
    def from_jsonschema(cls: Type[Self], *schemas: JSONSchema) -> Self:
        """Merge one or more JSON Schemas into a merged pyarrow schema."""
        versions = tuple(
            schema.get("properties", {}).get("@idsVersion", {}).get("const", None)
            for schema in schemas
        )
        return cls(
            versions=versions,
            schema=pyarrow_merge([get_pyarrow_schema(schema) for schema in schemas]),
        )


class MergeCompatibilityChecker(AbstractChecker):
    """
    Check for merge compatibility according to Delta.io schema evolution rules.
    """

    bulk_checker = True

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs = []
        artifact_range = context.artifact_range
        if artifact_range is None:
            # No artifact versions provided, can't check merge compatibility
            logs.append(
                CheckResult.critical(
                    "Lakehouse merge compatibility requires a method for accessing "
                    "existing IDS versions to compare against. "
                    "See documentation for downloading versions from TDP or using git "
                    "tags."
                )
            )
            if context.previous_artifact is not None:
                # Continue to show merge compatibility results using `--previous-ids`
                logs.append(
                    CheckResult.info(
                        "Running merge compatibility checks against the supplied "
                        "previous IDS version for information."
                    )
                )
                artifact_range = [context.previous_artifact]
            else:
                # No artifact range and no previous-artifact, nothing else to do
                return logs

        if len(artifact_range) == 0:
            # Artifact versions were provided, but none matched the criteria for
            # needing to be checked (e.g. this is a major version bump)
            return logs

        # Find the existing merged schema of the existing Delta table
        try:
            existing_merged_schema = MergedSchema.from_jsonschema(
                *(artifact.schema for artifact in artifact_range)
            )
        except MergeIncompatible as exception:
            logs.append(
                CheckResult.critical(
                    "Lakehouse merge compatibility check failed: the existing schemas "
                    "are invalid. The existing Lakehouse schema should be a "
                    "combination of these versions, but they are not merge compatible: "
                    f"{[x.identity.version for x in artifact_range]}. "
                    "Bump the major version to avoid merge conflicts. "
                    f"Merge error: {exception}."
                )
            )
            return logs
        # Merge the new schema into the existing schema
        try:
            existing_merged_schema.merge(context.artifact.schema)
        except MergeIncompatible as exception:
            logs.append(
                CheckResult.critical(
                    "Lakehouse merge compatibility check failed: the new schema "
                    "cannot be merged with the existing merged schema from version(s) "
                    f"{existing_merged_schema.versions}.\n{exception}."
                )
            )

        return logs
