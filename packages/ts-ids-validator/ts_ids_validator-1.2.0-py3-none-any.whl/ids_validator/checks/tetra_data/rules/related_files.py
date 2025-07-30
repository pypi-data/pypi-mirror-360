from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional, Union

from ids_validator.checks.rules_checker import BackwardCompatibleType

_RELATED_FILES = "root.properties.related_files"
_RELATED_FILES_ITEMS = "root.properties.related_files.items"
_RELATED_FILES_NAME = f"{_RELATED_FILES_ITEMS}.properties.name"
_RELATED_FILES_PATH = f"{_RELATED_FILES_ITEMS}.properties.path"
_RELATED_FILES_SIZE = f"{_RELATED_FILES_ITEMS}.properties.size"
_CHECKSUM = f"{_RELATED_FILES_ITEMS}.properties.checksum"
_CHECKSUM_VALUE = f"{_CHECKSUM}.properties.value"
_CHECKSUM_ALGORITHM = f"{_CHECKSUM}.properties.algorithm"

_POINTER = f"{_RELATED_FILES_ITEMS}.properties.pointer"
_POINTER_FILE_KEY = f"{_POINTER}.properties.fileKey"
_POINTER_VERSION = f"{_POINTER}.properties.version"
_POINTER_BUCKET = f"{_POINTER}.properties.bucket"
_POINTER_TYPE = f"{_POINTER}.properties.type"
_POINTER_FILE_ID = f"{_POINTER}.properties.fileId"


@dataclass
class Checks:
    type: Union[None, str, List[str]] = None
    compatible_type: Optional[List[BackwardCompatibleType]] = None
    required: Optional[Iterable[str]] = None
    properties: Optional[Iterable[str]] = None
    min_properties: Optional[Iterable[str]] = None
    min_required: Optional[Iterable[str]] = None


_RULES = {
    _RELATED_FILES: Checks(type="array"),
    _RELATED_FILES_ITEMS: Checks(
        type="object",
        min_properties=["name", "path", "size", "checksum", "pointer"],
        min_required=["pointer"],
    ),
    _RELATED_FILES_NAME: Checks(type=["null", "string"]),
    _RELATED_FILES_PATH: Checks(type=["null", "string"]),
    _CHECKSUM: Checks(
        type="object",
        min_properties=["value", "algorithm"],
        min_required=["value", "algorithm"],
    ),
    _CHECKSUM_VALUE: Checks(type="string"),
    _CHECKSUM_ALGORITHM: Checks(type=["string", "null"]),
    _POINTER: Checks(
        type="object",
        min_properties=["fileKey", "version", "bucket", "type", "fileId"],
        min_required=["fileKey", "version", "bucket", "type", "fileId"],
    ),
    _POINTER_FILE_KEY: Checks(type="string"),
    _POINTER_VERSION: Checks(type="string"),
    _POINTER_BUCKET: Checks(type="string"),
    _POINTER_TYPE: Checks(type="string"),
    _POINTER_FILE_ID: Checks(type="string"),
}

RULES = {
    field: {key: value for key, value in asdict(checks).items() if value is not None}
    for field, checks in _RULES.items()
}
