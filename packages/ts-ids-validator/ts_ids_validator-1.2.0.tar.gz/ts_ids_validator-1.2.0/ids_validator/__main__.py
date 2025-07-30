import json
import sys
from pathlib import Path
from typing import Optional

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

import typer
from rich.console import Console

from ids_validator import tdp_api
from ids_validator.ids_validator import validate_ids, validate_ids_using_tdp_artifact

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def main(
    ids_dir: Annotated[
        Path,
        typer.Option(
            "-i",
            "--ids_dir",
            "--ids-dir",
            help="Path to the IDS folder",
        ),
    ] = Path("."),
    previous_ids_dir: Annotated[
        Optional[Path],
        typer.Option(
            "-p",
            "--previous_ids_dir",
            "--previous-ids-dir",
            help=(
                "Path to a folder containing another version of the IDS, used to "
                "validate whether two specific versions are compatible. "
                "For full versioning validation, the `--download` or `--git` flag must be "
                "used: this option is only for development purposes."
            ),
        ),
    ] = None,
    download: Annotated[
        bool,
        typer.Option(
            "-d",
            "--download",
            help=(
                "(Boolean flag) Whether to download other IDS versions from TDP. "
                "This is used to validate that the new IDS is compatible with existing "
                "versions of the same IDS retrieved from TDP. "
                "To use this option, you must provide API configuration, either as "
                "environment variables 'TS_API_URL', 'TS_ORG' and 'TS_AUTH_TOKEN' (see the "
                "README for more), or as a JSON config file (see `--config`)."
            ),
        ),
    ] = False,
    git: Annotated[
        bool,
        typer.Option(
            "-g",
            "--git",
            help=(
                "(Boolean flag) Whether to retrieve other IDS versions from git tags. "
                "This is used to validate that the new IDS is compatible with existing "
                "versions of the same IDS as an alternative to the --download flag which "
                "doesn't require configuring TDP credentials. "
                "Git tags must match `vM.m.p[.B]` where `M` (major), `m` (minor), "
                "`p` (patch) and the optional `B` (build) are integers. "
                "This assumes the version in the tag name matches the actual IDS version "
                "in schema.json at that tag - note that it is possible for these to be "
                "out of sync, and it is possible for the local tagged versions to be out "
                "of sync with the artifact available in TDP. "
                "It is recommended to use --download before uploading an IDS to TDP, but "
                "--git may be more convenient for iterative local development or CI/CD "
                "checks if tags are appropriately maintained."
            ),
        ),
    ] = False,
    config: Annotated[
        Optional[Path],
        typer.Option(
            "-c",
            "--config",
            help=(
                "Configuration for using the TDP API in a JSON file containing the keys "
                "'api_url', 'org' and 'auth_token'. Provide either this or the equivalent "
                "environment variables to use the `--download` flag."
            ),
        ),
    ] = None,
):
    """Validate an IDS artifact"""
    try:
        console = Console()
        # Validate mutual exclusivity
        options = [previous_ids_dir is not None, download, git]
        if sum(options) > 1:
            raise ValueError(
                "Only one of `--previous_ids_dir`, `--download` or `--git` can be used."
            )

        if config is not None and not download:
            # Validate `download` is required when `config` is used
            raise ValueError(
                "When the config argument is used, the download flag is required: "
                "Add `-d` to the command."
            )
        if download:
            # Get existing IDSs via API download
            api_config = tdp_api.APIConfig.from_json_or_env(
                json.loads(config.read_text()) if config else None
            )
            result = validate_ids_using_tdp_artifact(
                ids_dir=ids_dir,
                api_config=api_config,
                console=console,
            )
        elif git:
            # Only import git-related modules where git is used, because it can fail
            # if a `git` executable is not installed
            from ids_validator.ids_validator_git import validate_ids_using_git_tags

            # Get existing IDSs from git tags
            result = validate_ids_using_git_tags(
                ids_dir=ids_dir,
                console=console,
            )
        else:
            # Note previous_ids_dir may be `None`
            result = validate_ids(
                ids_dir=ids_dir,
                previous_ids_dir=previous_ids_dir,
                console=console,
            )

        return_code = 0 if result else 1

    except Exception as exc:
        console.print(
            f"[b i red]\nValidation Failed with critical error.[/b i red]\n{exc}"
        )

        return_code = 1

    sys.exit(return_code)
