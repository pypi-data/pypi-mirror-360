"""
This module is nearly the same as the schema converter used in ids-to-delta, except:

- There is no logging
- `integer` is considered different to `number` here, to be more conservative
"""

from typing import Dict

import pyarrow as pa
from jsonref import replace_refs

from ids_validator.models.json_schema import JSONSchema, JSONSchemaPrimitive


class SchemaError(ValueError):
    pass


# map of primitive type to pyarrow type function
# see datatype functions: https://arrow.apache.org/docs/python/api/datatypes.html
TYPE_MAP: Dict[JSONSchemaPrimitive, pa.DataType] = {
    "string": pa.string,
    # TetraFlow converts "integer" to `pa.float64` because JSON allows integers which
    # look like '9.0'. Here we use `pa.int64` so that it's not possible to merge
    # number with integer, in case we want to distinguish them in the future.
    "integer": pa.int64,
    "number": pa.float64,
    "boolean": pa.bool_,
    "null": pa.null,
}


def get_pyarrow_schema(json_schema: JSONSchema) -> pa.Schema:
    datatype = get_pyarrow_datatype(replace_refs(json_schema, proxies=False), path="")
    if not isinstance(datatype, pa.StructType):
        raise SchemaError(
            'Top-level schema type is not "object".  Cannot convert to table schema.'
        )
    # turn the top-level struct datatype into a schema
    return pa.schema(list(datatype))


def get_pyarrow_datatype(json_schema: JSONSchema, path="") -> pa.DataType:
    """Get the datatype for the given json schema object"""
    if not isinstance(json_schema, dict):
        raise SchemaError(
            f"Invalid JSON schema detected at {path}.  Expected object, found: {type(json_schema)}"
        )

    obj_type = json_schema.get("type")
    if obj_type is None:
        raise SchemaError(
            f'Invalid JSON schema detected{(" at " + path) if path else ""}.  No "type" property found.'
        )

    # type is a list of possible types.
    # the only valid lists are [PRIMITIVE] or [PRIMITIVE, 'null']
    if isinstance(obj_type, list):
        if len(obj_type) == 1:
            return get_pyarrow_primitive(obj_type[0], path=path)
        if len(obj_type) == 2:
            # must be a list of null and a primitive
            types = set(obj_type)
            if "null" not in types:
                raise SchemaError(
                    f'Unable to convert list of types at {path}: {obj_type}. Must be only "null" and a primitive type'
                )
            primitive = (types - set(["null"])).pop()
            return get_pyarrow_primitive(primitive, path=path)
        raise SchemaError(
            f'Invalid list of types at {path}: {obj_type}. Must be only "null" and a primitive type'
        )

    # type is a primitive
    if obj_type in TYPE_MAP:
        return get_pyarrow_primitive(obj_type, path=path)

    if obj_type == "array":
        if "items" not in json_schema or not isinstance(json_schema["items"], dict):
            raise SchemaError(
                f'Invalid array type at {path}. Arrays must contain an "items" schema'
            )
        return pa.list_(get_pyarrow_datatype(json_schema["items"], path=f"{path}[*]"))
    if obj_type == "object":
        if "properties" not in json_schema:
            raise SchemaError(
                f'Invalid object type at {path}. Objects must contain "properties"'
            )
        fields = [
            (key, get_pyarrow_datatype(value, path=f"{path}{'.' if path else ''}{key}"))
            for key, value in json_schema["properties"].items()
        ]
        return pa.struct(fields)
    expected_types = list(TYPE_MAP) + ["array", "object"]
    error = f"Found unexpected type at {path}: {obj_type}.  Expected one of {expected_types}"

    raise SchemaError(error)


def get_pyarrow_primitive(type_str: JSONSchemaPrimitive, path: str) -> pa.DataType:
    mapped_type = TYPE_MAP.get(type_str)
    if mapped_type is None:
        raise SchemaError(f"Unknown primitive at {path}: {type_str}")
    # types are functions, so we need to call them here
    return mapped_type()
