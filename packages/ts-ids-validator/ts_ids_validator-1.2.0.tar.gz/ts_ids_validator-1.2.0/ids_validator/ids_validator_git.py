from pathlib import Path

from rich.console import Console

from ids_validator.ids_validator import validate_ids_from_artifacts
from ids_validator.models.git import (
    get_matching_major_versions_from_git_tags,
    get_previous_artifact_from_git_tags,
)
from ids_validator.models.ids_artifact import IdsArtifact
from ids_validator.validator import default_console


def validate_ids_using_git_tags(
    ids_dir: Path,
    console: Console = default_console,
) -> bool:
    """Run IDS validator, grabbing other versions from git tags.

    Args:
        ids_dir (Path): Path to IDS artifact folder
        console (rich.console.Console): Console object to write to

    Returns:
        bool: True if IDS is valid else False
    """
    ids_artifact = IdsArtifact.from_ids_folder(ids_dir)

    previous_ids_artifact = get_previous_artifact_from_git_tags(
        ids_dir, ids_artifact.identity.version
    )

    # For merge compatibility, load all tags with a matching major version
    artifact_range = get_matching_major_versions_from_git_tags(
        ids_dir, ids_artifact.identity.version_parts.major
    )

    return validate_ids_from_artifacts(
        ids_artifact=ids_artifact,
        previous_ids_artifact=previous_ids_artifact,
        console=console,
        artifact_range=artifact_range,
    )
