from typing import Any, Dict, List, Union

from typing_extensions import Literal, TypeAlias, TypedDict

JSONSchemaPrimitive: TypeAlias = Literal[
    "string", "number", "integer", "boolean", "null"
]
JSONSchemaType: TypeAlias = Literal["object", "array", JSONSchemaPrimitive]


class JSONSchema(TypedDict, total=False):
    """A simplified type for JSON Schema dicts

    Catches some basic JSON Schema definition mistakes with type checkers, but
    is not comprehensive.
    """

    type: Union[JSONSchemaType, List[JSONSchemaType]]
    properties: Dict[str, "JSONSchema"]
    items: "JSONSchema"
    const: Any
