from copy import deepcopy
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from pydash import get as nested_get
from typing_extensions import TypedDict

from ids_validator.checks.abstract_checker import CheckResult
from ids_validator.models.validator_parameters import ValidatorParameters

# TDP only allows up to 50 nested fields in a given IDS
MAXIMUM_NESTED_FIELDS = 50

ESMappingProperties = Dict[str, Union[dict, str]]


class ESMapping(TypedDict):
    """Type expected in elasticsearch.json at path `mapping`"""

    properties: ESMappingProperties
    dynamic_tempaltes: List[str]


class ElasticSearchDocument(TypedDict):
    """Type expected for elasticsearch.json document."""

    mapping: ESMapping
    nonSearchableFields: List[str]


class ESKeys(str, Enum):
    """JSON keys found in elasticsearch.json"""

    DATACUBES_KEY = "datacubes"
    ES_MAPPING_KEY = "mapping"
    PROPERTIES_KEY = "properties"
    NESTED = "nested"
    TYPE = "type"
    NON_SEARCHABLE = "nonSearchableFields"
    ITEMS = "items"


class JSONTypes(str, Enum):
    ARRAY = "array"
    OBJECT = "object"


def _find_nested_field(
    path: Tuple[str, ...], value: ESMappingProperties
) -> Generator[Union[Tuple[str, ...], CheckResult], None, None]:
    """
    Find all nested fields in the elastic search mapping properties object.
    This function assumes it is passed the object from an artifact's
    elasticsearch.json field `mapping.properties`.

    This should only be called by `get_nested_fields`.

    Args:
        path: Collection of json keys which describe the path to a value in the
              elasticsearch json file
        value: Value in the elasticsearch json which the path points to
    Returns:
        Generator of found nested fields or CheckResult instances once a malformed object is found.
        Each string returned by the generator should be the IDS path to the nested field.
    """
    if isinstance(value, dict):
        if (
            ESKeys.TYPE.value in value
            and value.get(ESKeys.TYPE.value) == ESKeys.NESTED.value
        ):
            yield path
            value.pop(ESKeys.TYPE.value)
            if value:
                # Reaching this code means we found a nested field with additional properties
                # The IDS path will have "items" as a key before reaching the nested properties key
                path = (*path, ESKeys.ITEMS.value)
        for key, val in value.items():
            if not isinstance(key, str):
                yield CheckResult.critical(
                    "Unexpected key type found when traversing elastic search document."
                    f" Expected type string, found {key} of type {type(key).__name__} at location {'.'.join(path)}."
                )
            else:
                yield from _find_nested_field((*path, key), val)
    else:
        yield CheckResult.critical(
            f"Unexpected type found when traversing elasticsearch.json document."
            f" Expected type dict, found {value} of type"
            f" {type(value).__name__} at location {'.'.join(path)}"
        )


def get_nested_fields(
    es_document: ElasticSearchDocument,
) -> Union[Tuple[List[str], List[CheckResult]]]:
    """
    Get json paths to all nested fields defined in an artifact's elasticsearch document.

    Args:
        es_document: Diction of the artifact's elasticsearch.json

    Returns:
        Paths to all nested fields in the elasticsearch document along
        with the CheckResult instances if a malformed object was found
    """

    es_document = nested_get(
        es_document, f"{ESKeys.ES_MAPPING_KEY.value}.{ESKeys.PROPERTIES_KEY.value}"
    )

    errors: List[CheckResult] = []
    paths: List[str] = []

    if es_document:
        for path in _find_nested_field((ESKeys.PROPERTIES_KEY.value,), es_document):
            if isinstance(path, CheckResult):
                errors.append(path)
            else:
                paths.append(".".join(path))

    return paths, errors


def validate_path_exists_as_array_of_objects(
    field_path: str, ids: Dict[str, Any]
) -> Optional[CheckResult]:
    """
    Validate that a elasticsearch nested field path exists in an IDS
    and is defined as array of objects.

    Args:
        field_path: path to nested field found in elasticsearch.json file
        ids: IDS present in artifact repo

    Returns:
        CheckResult instance if path is not found or is not an array of objects,
        otherwise None
    """
    schema_object = nested_get(ids, field_path)
    if schema_object is None:
        return CheckResult.critical(
            f"elasticsearch.json nested field, {field_path},"
            " not found in the IDS. Each nested field defined"
            " in elasticsearch.json must exist in the IDS."
        )

    if not isinstance(schema_object, dict) or schema_object.get("type") != "array":
        return CheckResult.critical(
            message=f"elasticsearch.json nested field, {field_path},"
            f" must be a JSON primitive of type '{JSONTypes.ARRAY.value}' in the IDS."
            f" Found {schema_object} of type {type(schema_object).__name__}"
        )

    if nested_get(schema_object, "items.type") != JSONTypes.OBJECT.value:
        return CheckResult.critical(
            message=f"elasticsearch.json nested field, {field_path}.items,"
            f" items must be of type '{JSONTypes.OBJECT.value}'."
        )


class IDSPathError(Exception):
    """Error to raise when a malformed value is found when searching for a path in an IDS."""

    def __init__(self, field: str, path: str, msg: str = None):
        """
        Args:
            field: Field whose value is malformed
            path: Full schema path that was being search
            msg: Message to append to standard message
        """
        super().__init__(
            f"Malformed IDS object found at field, '{field}', when searching for field {path}.{f' {msg}' if msg else ''}"
        )


def _get_properties(schema_object: dict, field: str, path: str) -> Dict[str, Any]:
    """
    Validate schema object contains `properties` and it has a valid value

    Args:
        schema_object: object that contains `properties` keyword
        field: Field in the schema at which the schema_object exists
        path: Full schema path being searched

    Returns:
        Return `properties` respective value
    """
    if ESKeys.PROPERTIES_KEY.value not in schema_object:
        raise IDSPathError(
            field,
            path,
            f"Expected object type to contain '{ESKeys.PROPERTIES_KEY.value}'.",
        )

    properties = schema_object.get(ESKeys.PROPERTIES_KEY.value)

    if not isinstance(properties, dict):
        raise IDSPathError(
            field,
            path,
            f"A '{ESKeys.PROPERTIES_KEY.value}' value must be a JSON primitive of type 'object'.",
        )

    return properties


def validate_instance_path_exists_in_schema(path: str, ids: Dict[str, Any]) -> bool:
    """
    Validate that a schema path exists in an IDS using an IDS instance pointer.

    Example:
        path = "field_a.field_b"

        ids = {
            "properties": {
                "field_a": {
                    "type": "object",
                    "properties": {"field_b": {"type": "string"}},
                }
            }
        }

        Will return true as the IDS instance with the pointer field_a.field_b
        can be validated against the IDS.

    Args:
        path: IDS instance path to find in schema
        ids: Schema to search

    Returns:
        True if path exists in schema, otherwise False
    """
    if not isinstance(path, str):
        raise ValueError(
            f"IDS instance paths must be of type string and delimited with a dot"
            f" (e.g. field_a.field_b). Received {path}."
        )

    path_parts = path.split(".")

    schema_obj = _get_properties(
        ids, ESKeys.PROPERTIES_KEY.value, f"{ESKeys.PROPERTIES_KEY.value}.{path}"
    )

    while path_parts:
        field, *path_parts = path_parts
        schema_obj = schema_obj.get(field)
        if schema_obj is None:
            return False

        if isinstance(schema_obj, dict):
            obj_type = schema_obj.get(ESKeys.TYPE.value)

            # If we are on the last path and the type exists then
            # we can say the path exists in the schema
            if obj_type is not None and len(path_parts) == 0:
                return True

            if obj_type == JSONTypes.OBJECT.value:
                schema_obj = _get_properties(schema_obj, field, path)
                continue

            if obj_type == JSONTypes.ARRAY.value:
                items = schema_obj.get(ESKeys.ITEMS.value)
                if not isinstance(items, dict):
                    raise IDSPathError(
                        field,
                        path,
                        f"Array object must contain the '{ESKeys.ITEMS.value}'"
                        f" keyword whose value is an object.",
                    )

                items_type = items.get(ESKeys.TYPE.value)

                if items_type == JSONTypes.OBJECT.value:
                    schema_obj = _get_properties(items, field, path)
                    continue

        raise IDSPathError(
            field,
            path,
            f" Object must contain the key '{ESKeys.TYPE.value}' whose value"
            f" describes the field's JSON type.",
        )


def validate_nonsearchable_fields(
    es_document: ElasticSearchDocument, ids: Dict[str, Any]
) -> List[CheckResult]:
    """
    Validate that nonSearchableFields in the elasticsearch document follow:
    1. It's value is a list of strings
    2. Each value in nonSearchableFields is a path pointing to a field in the IDS
    3. If 'datacubes' exists in the IDS, it also exists in nonSearchableFields

    Args:
        es_document: The IDS artifact's elasticsearch.json document as a dictionary
        ids: The artifact's schema.json as a dictionary

    Returns:
        List of CheckResult or empty list
    """
    if ESKeys.NON_SEARCHABLE.value not in es_document:
        return []

    non_searchable_fields = es_document.get(ESKeys.NON_SEARCHABLE.value)

    if not isinstance(non_searchable_fields, list):
        return [
            CheckResult.critical(
                message="elasticsearch.json nonSearchableFields must be defined as a list"
                f" of strings. Found, {non_searchable_fields}."
            )
        ]

    errors = []
    has_datacubes = False
    for field in non_searchable_fields:
        if not isinstance(field, str):
            errors.append(
                CheckResult.critical(
                    message="elasticsearch.json nonSearchableFields can only contain string values."
                    f" Found, {field} of type {type(field).__name__}"
                )
            )
            continue
        if field == ESKeys.DATACUBES_KEY.value:
            has_datacubes = True
        if not validate_instance_path_exists_in_schema(field, ids):
            errors.append(
                CheckResult.critical(
                    message=f"elasticsearch.json nonSearchableField, {field}, not found in schema."
                    f" All nonSearchableFields must exist within the IDS."
                )
            )

    if not has_datacubes and validate_instance_path_exists_in_schema(
        ESKeys.DATACUBES_KEY.value, ids
    ):
        errors.append(
            CheckResult.critical(
                message=f"'{ESKeys.DATACUBES_KEY.value}' exists in the IDS but is not denoted as a nonSearchableField"
                f" in elasticsearch.json. '{ESKeys.DATACUBES_KEY.value}' must be a nonSearchableField"
                f" if used in the IDS."
            )
        )

    return errors


def validate_elasticsearch_json(
    validator_parameters: ValidatorParameters,
) -> List[CheckResult]:
    """
    Validate elasticsearch.json and it's respective schema are platform comppatible

    Args:
        validator_parameters: Instance of ValidatorParameters which contains an IDS
                              artifact's elasticsearh.json and schema.json as dictionaries

    Returns:
        list of CheckResult instances containing errors found
    """
    es_document = deepcopy(validator_parameters.artifact.elasticsearch)
    if not es_document:
        return [
            CheckResult.critical(
                message="elasticsearch.json file is empty. Each IDS must have a respective elasticsearch.json"
                " file to be compatible with the platform."
            )
        ]

    nested_fields, errors = get_nested_fields(
        validator_parameters.artifact.elasticsearch
    )

    if len(nested_fields) > MAXIMUM_NESTED_FIELDS:
        errors.append(
            CheckResult.critical(
                message=f"elasticsearch.json contains {len(nested_fields)} nested fields which exceeds"
                f" the maximum allowed of {MAXIMUM_NESTED_FIELDS}."
            )
        )

    if nested_fields:
        errors += list(
            filter(
                lambda x: x is not None,
                [
                    validate_path_exists_as_array_of_objects(
                        path, validator_parameters.artifact.schema
                    )
                    for path in nested_fields
                ],
            )
        )

    errors += validate_nonsearchable_fields(
        validator_parameters.artifact.elasticsearch,
        validator_parameters.artifact.schema,
    )

    return errors
