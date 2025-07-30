from pathlib import Path
from typing import Optional, Sequence

from rich.console import Console

from ids_validator import tdp_api
from ids_validator.models.ids_artifact import IdsArtifact
from ids_validator.models.validator_parameters import ValidatorParameters
from ids_validator.validator import Validator, default_console


def validate_ids_from_artifacts(
    ids_artifact: IdsArtifact,
    previous_ids_artifact: Optional[IdsArtifact] = None,
    console: Console = default_console,
    artifact_range: Optional[Sequence[IdsArtifact]] = None,
) -> bool:
    """Run IDS validator and print warnings / failures to console

    Args:
        previous_ids_artifact: (IdsArtifact): Previous version of IDS artifact
        ids_artifact (IdsArtifact): Current IDS artifact to validate
        console (rich.console.Console): Console object to write to

    Returns:
        bool: True if IDS is valid else False
    """

    parameters = ValidatorParameters(
        artifact=ids_artifact,
        previous_artifact=previous_ids_artifact,
        artifact_range=artifact_range,
    )

    validator = Validator(parameters, console=console)
    validator.validate_ids()

    if validator.has_critical_failures:
        validator.console.print(
            "[b i red]\nValidation Failed with critical error.[/b i red]"
        )
        return False

    validator.console.print(
        "[b i green]Validation Complete. No error found.[/b i green]"
    )

    return True


def validate_ids(
    ids_dir: Path,
    previous_ids_dir: Optional[Path] = None,
    console: Console = default_console,
    artifact_range: Optional[Sequence[IdsArtifact]] = None,
) -> bool:
    """Run IDS validator and print warnings / failures to console

    Args:
        previous_ids_dir: (Path): Path to folder with previous version of IDS artifact
        ids_dir (Path): Path to IDS folder
        console (rich.console.Console): Console object to write to

    Returns:
        bool: True if IDS is valid else False
    """
    ids_artifact = IdsArtifact.from_ids_folder(ids_dir)

    previous_artifact = None
    if previous_ids_dir is not None:
        previous_artifact = IdsArtifact.from_ids_folder(previous_ids_dir)

    return validate_ids_from_artifacts(
        ids_artifact=ids_artifact,
        previous_ids_artifact=previous_artifact,
        console=console,
        artifact_range=artifact_range,
    )


def validate_ids_using_tdp_artifact(
    ids_dir: Path,
    api_config: tdp_api.APIConfig,
    console: Console = default_console,
) -> bool:
    """Run IDS validator and print warnings / failures to console

    This function will attempt to load the previous IDS artifact using the TDP API.
    See the Readme for configuring the API.

    Args:
        ids_dir (Path): Path to IDS artifact folder
        api_config (APIConfig): API configuration for accessing the TDP API
        console (rich.console.Console): Console object to write to

    Returns:
        bool: True if IDS is valid else False
    """
    ids_artifact = IdsArtifact.from_ids_folder(ids_dir)

    # Get previous IDS from API download
    previous_ids_artifact = tdp_api.get_preceding_ids_artifact(
        config=api_config,
        namespace=ids_artifact.identity.namespace,
        slug=ids_artifact.identity.slug,
        target_version=ids_artifact.identity.version,
    )

    # For merge compatibility, use all versions from the same major version
    artifact_range = tdp_api.get_artifacts_range(
        config=api_config,
        namespace=ids_artifact.identity.namespace,
        slug=ids_artifact.identity.slug,
        major_version=ids_artifact.identity.version_parts.major,
    )

    return validate_ids_from_artifacts(
        ids_artifact=ids_artifact,
        previous_ids_artifact=previous_ids_artifact,
        console=console,
        artifact_range=artifact_range,
    )
