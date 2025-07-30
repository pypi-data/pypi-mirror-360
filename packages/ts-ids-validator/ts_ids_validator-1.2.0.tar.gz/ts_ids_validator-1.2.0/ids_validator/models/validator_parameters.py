from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Sequence

from ids_validator.ids_node import Node
from ids_validator.models.ids_artifact import IdsArtifact


class VersioningMode(Enum):
    CSV_ATHENA = auto()
    LAKEHOUSE_SCHEMA_EVOLUTION = auto()


@dataclass
class ValidatorParameters:
    """Class for keeping all parameters that could/would be used by validator"""

    artifact: IdsArtifact = field(default_factory=IdsArtifact)
    previous_artifact: Optional[IdsArtifact] = None
    artifact_range: Optional[Sequence[IdsArtifact]] = None

    @staticmethod
    def from_comparative_schema_paths(
        schema_path: Path, previous_schema_path: Path
    ) -> "ValidatorParameters":
        """
        Create ValidatorParameters instance from the current and previous IDS file paths.

        Args:
            schema_path: File path the current IDS artifact
            previous_schema_path: Fale path to the previous IDS artifact

        Returns:
            Instance of ValidatorParameters
        """
        return ValidatorParameters(
            artifact=IdsArtifact.from_schema_path(schema_path),
            previous_artifact=IdsArtifact.from_schema_path(previous_schema_path),
        )

    def root_node(self) -> Node:
        """Get the entire IDS as a Node instance."""
        return Node(schema=self.artifact.schema)
