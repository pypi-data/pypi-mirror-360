from typing import Any, Dict

import jsonschema

from ids_validator.instance.datacubes import validate_datacubes_measure_dimension_match
from ids_validator.instance.exceptions import InvalidInstance
from ids_validator.models.json_schema import JSONSchema
from ids_validator.utils import get_ids_identity


def validate_instance_against_schema(instance: dict, schema: Dict[str, Any]) -> None:
    """Validate an IDS instance against the schema."""

    validator = jsonschema.Draft7Validator(schema)
    schema_errors = []
    # https://python-jsonschema.readthedocs.io/en/stable/validate/#jsonschema.IValidator.iter_errors
    for error in sorted(validator.iter_errors(instance), key=str):
        schema_errors.append(
            "error: " + error.message + " at path: " + str(list(error.schema_path))
        )
    if schema_errors:
        ids_identity = get_ids_identity(schema)
        raise InvalidInstance(
            f"Failed validation against IDS: {ids_identity.namespace}/{ids_identity.slug}:{ids_identity.version}:\n"
            + "\n".join(schema_errors)
        )


def validate_ids_instance(instance: dict, schema: Dict[str, Any]) -> None:
    """Validate an IDS instance."""
    validate_instance_against_schema(instance, schema)
    validate_datacubes_measure_dimension_match(instance.get("datacubes", []))
