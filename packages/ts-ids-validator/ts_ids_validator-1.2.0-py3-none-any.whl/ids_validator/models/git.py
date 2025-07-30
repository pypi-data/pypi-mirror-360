import json
import re
from itertools import groupby
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from git import GitCommandError, InvalidGitRepositoryError, Repo, Tag
from semver import Version

from ids_validator.models.ids_artifact import IdsArtifact
from ids_validator.utils import get_preceding_version, parse_prefixed_version


def select_repo(repo_path: Path) -> Repo:
    try:
        return Repo(repo_path)
    except InvalidGitRepositoryError as exception:
        raise ValueError(
            "The given path is not a git repository, which is required when "
            "using the git flag to fetch other IDS versions."
        ) from exception


VERSION_PATTERN = re.compile(r"^(v[\d]+\.[\d]+\.[\d]+)(?:\.([\d]+))?$")


def parse_version_with_build(version: str) -> Tuple[Version, int]:
    """
    For git tags of the form `vX.Y.Z.B`, where `.B` is a build number, parse this into
    (Version(X, Y, Z), B), which is sortable.
    """
    custom_version_match = VERSION_PATTERN.match(version)
    if custom_version_match:
        v = parse_prefixed_version(custom_version_match.group(1))
        build_match = custom_version_match.group(2)
        build = int(build_match) if build_match is not None else 0
    else:
        raise ValueError(
            f"Version '{version}' did not match supported pattern {VERSION_PATTERN}"
        )
    return v, build


def get_version_tags(repo: Repo) -> Dict[str, Tag]:
    """Match all tags which look like version strings.

    If multiple of the same version are present, the one with the highest `.B` build
    number is used.

    For example, if version tags (v1.0.0, v1.0.1, v1.0.1.1) are present, then
    (v1.0.0, v1.0.1.1) will be used. v1.0.1 is skipped because it's superseded by
    v1.0.1.1.

    Returns a mapping from IDS version to the corresponding repo tag, e.g.

    ```
    {"v1.0.1": repo.tag("v1.0.1.1")}
    ```
    """
    version_tags = filter(
        lambda tag: VERSION_PATTERN.match(tag.name),
        repo.tags,
    )
    # Group by major/minor/patch version, then keep the one with the largest build
    # number in each group.
    version_map = {}
    for version, group in groupby(
        version_tags, lambda tag: parse_version_with_build(tag.name)[0]
    ):
        version_map[f"v{version}"] = max(
            group, key=lambda tag: parse_version_with_build(tag.name)
        )

    return version_map


def get_ids_artifact_from_tag(tag: Tag) -> IdsArtifact:
    """
    Read all relevant IDS artifact files from a given commit
    """
    # Note `expected.json` and other files are not currently needed
    files = {}
    for key, file_name in {
        "schema": "schema.json",
        "athena": "athena.json",
        "elasticsearch": "elasticsearch.json",
    }.items():
        try:
            result = tag.repo.git.show(f"{tag}:{file_name}")
        except GitCommandError:
            # The file doesn't exist
            raise FileNotFoundError(
                "The following artifact file must exist but was not found in git tag "
                f"{tag}: {file_name}. "
                "Fix the tag to match the actual artifact in TDP, or if the artifact "
                "itself is invalid, bump the IDS major version."
            )
        files[key] = json.loads(result)

    return IdsArtifact(**files, git_tag=tag.name)


def get_matching_major_versions_from_git_tags(
    repo_path: Path, major_version: int
) -> List[IdsArtifact]:
    """
    Get all IDS artifacts with the same major version from a git repo, assuming
    the repo has each version tagged as `vM.m.p(.B)` where `.B` is optional.

    Returns a map from the IDS version to the corresponding IdsArtifact
    """
    repo = select_repo(repo_path)
    version_tags = get_version_tags(repo)
    matching_major_versions = [
        tag
        for version, tag in version_tags.items()
        if version.startswith(f"v{major_version}.")
    ]

    return [get_ids_artifact_from_tag(tag) for tag in matching_major_versions]


def get_previous_artifact_from_git_tags(
    repo_path: Path, current_version: str
) -> Optional[IdsArtifact]:
    repo = select_repo(repo_path)
    version_tags = get_version_tags(repo)
    preceding_version = get_preceding_version(
        current_version, list(version_tags.keys())
    )
    if preceding_version is None:
        return None
    return get_ids_artifact_from_tag(version_tags[preceding_version])
