import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import jsonref

from ids_validator.checks.constants import CONVENTION_VERSION, IS_TETRA_DATA_SCHEMA
from ids_validator.utils import IdsIdentity, get_ids_identity


@dataclass()
class IdsArtifact:
    """A class representing an complete IDS artifact"""

    schema: dict = field(default_factory=dict)
    athena: dict = field(default_factory=dict)
    elasticsearch: dict = field(default_factory=dict)
    expected: dict = field(default_factory=dict)
    path: Path = Path()
    git_tag: Optional[str] = None

    def __post_init__(self) -> None:
        # Dereference all definitions and then remove the definitions
        deref_schema: Dict[str, Any] = jsonref.replace_refs(
            self.schema,
            lazy_load=False,
            merge_props=True,
            proxies=False,  # Do not use JsonRef proxies: dereference the actual values
        )  # type: ignore
        if "definitions" in deref_schema:
            deref_schema.pop("definitions")
        self.schema = deref_schema

    @staticmethod
    def from_schema_path(schema_path: Path) -> "IdsArtifact":
        """Create validator parameters given the path to schema.json"""

        ids_folder_path = schema_path.parent
        athena_path = ids_folder_path.joinpath("athena.json")
        elasticsearch_path = ids_folder_path.joinpath("elasticsearch.json")
        expected_path = ids_folder_path.joinpath("expected.json")

        missing_files = tuple(
            file.name
            for file in (schema_path, athena_path, elasticsearch_path, expected_path)
            if not file.exists()
        )
        if missing_files:
            raise FileNotFoundError(
                "The following artifact files must exist but were not found: "
                f"{missing_files}. Check the previous artifact."
            )
        schema = json.loads(schema_path.read_text())
        athena = json.loads(athena_path.read_text())
        elasticsearch = json.loads(elasticsearch_path.read_text())
        expected = json.loads(expected_path.read_text())

        return IdsArtifact(
            schema=schema,
            athena=athena,
            elasticsearch=elasticsearch,
            expected=expected,
            path=ids_folder_path,
        )

    @staticmethod
    def from_ids_folder(ids_path: Path) -> "IdsArtifact":
        """Create validator parameters given the path to schema.json"""
        return IdsArtifact.from_schema_path(ids_path.joinpath("schema.json"))

    def write(self, folder: Path) -> None:
        """Write the artifact files to `folder`."""
        folder.joinpath("schema.json").write_text(json.dumps(self.schema, indent=2))
        folder.joinpath("elasticsearch.json").write_text(
            json.dumps(self.elasticsearch, indent=2)
        )
        folder.joinpath("athena.json").write_text(json.dumps(self.athena, indent=2))
        folder.joinpath("expected.json").write_text(json.dumps(self.expected, indent=2))

    def get_identity(self) -> IdsIdentity:
        """Populate the IDS identity from the schema."""
        return get_ids_identity(self.schema)

    @property
    def identity(self) -> IdsIdentity:
        """IDS identity (namespace/slug/version) according to the schema."""
        return get_ids_identity(self.schema)

    @property
    def is_tetra_data_schema(self) -> bool:
        """
        Check if the schema is a tetra data schema (i.e. follows modeling conventions).

        Returns:
            True if the schema is a tetra data schema, otherwise False
        """
        is_tetra_data = False
        if IS_TETRA_DATA_SCHEMA in self.schema:
            is_tetra_data = self.schema.get(IS_TETRA_DATA_SCHEMA)
            if not isinstance(is_tetra_data, bool):
                raise ValueError(
                    f"The value of the top-level metadata field '{IS_TETRA_DATA_SCHEMA}' must be"
                    f" a boolean if this field is defined in the IDS. Found {is_tetra_data}."
                )

        if CONVENTION_VERSION in self.schema.get("properties", {}):
            value = self.schema["properties"]["@idsConventionVersion"]

            expected = {"type": "string", "const": "v1.0.0"}
            # Check `value` contains at least the same key-value pairs as `expected`
            # It may contain more, like "description"
            if isinstance(value, dict) and value.items() >= expected.items():
                is_tetra_data = True
            else:
                raise ValueError(
                    f"When the field '{CONVENTION_VERSION}' is defined, the value must be {expected}."
                    f" Found {value}."
                )

        return is_tetra_data
