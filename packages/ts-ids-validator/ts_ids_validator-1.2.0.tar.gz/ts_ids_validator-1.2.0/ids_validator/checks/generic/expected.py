import jsonschema

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
)
from ids_validator.ids_node import Node, NodePath
from ids_validator.models.validator_parameters import ValidatorParameters


def clean_jsonschema_validation_error(error: jsonschema.ValidationError) -> str:
    """Create a clean error from jsonschema.ValidationError parameters

    jsonschema.ValidationError can be long and difficult to read, e.g.
    ```
    7 is not of type 'string'

    Failed validating 'type' in schema['properties']['@idsVersion']:
        {'const': 'v7.0.1', 'type': 'string'}

    On instance['@idsVersion']:
        7
    ```

    This function will clean it up to be more readable, e.g.
    ```
    Failed validating 'type' of schema['properties']['@idsVersion'] on instance['@idsVersion']:
    7 is not of type 'string'
    ```

    Args:
        message: The error message.
        validator: The validator that failed.
        schema_path: The path in the schema where the error occurred.
        instance_path: The path in the instance where the error occurred.

    Returns:
        A cleaned error message.
    """

    schema_path_string = (
        f"schema[{']['.join(repr(index) for index in list(error.schema_path)[:-1])}]"
    )
    instance_path_string = (
        f"instance[{']['.join(repr(index) for index in list(error.path))}]"
    )
    message = f"Failed validating {error.validator!r} of {schema_path_string} on {instance_path_string}:\n{error.message}"
    return message


class ExpectedChecker(AbstractChecker):
    """
    expected.json must be valid against schema.json when validated with a JSON Schema
    validator.
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:

        if node.path != NodePath(("root",)):
            # This check will only run for the root node of the schema.
            return []

        validator = jsonschema.Draft7Validator(context.artifact.schema)
        try:
            validator.validate(context.artifact.expected)
        except jsonschema.ValidationError as exception:
            return [
                CheckResult.critical(
                    "expected.json is not valid against schema.json. "
                    f"JSON Schema validation failed:\n{clean_jsonschema_validation_error(exception)}"
                )
            ]

        return []
