from ids_validator.checks.tetra_data.rules.samples.samples_root import ITEMS_PROPERTIES

PROPERTIES = f"{ITEMS_PROPERTIES}.properties"
ITEMS = f"{PROPERTIES}.items"
PROPERTIES_ITEMS_PROPERTIES = f"{ITEMS}.properties"

SOURCE = f"{PROPERTIES_ITEMS_PROPERTIES}.source"
SOURCE_PROPERTIES = f"{SOURCE}.properties"
SOURCE_NAME = f"{SOURCE_PROPERTIES}.name"
SOURCE_TYPE = f"{SOURCE_PROPERTIES}.type"

NAME = f"{PROPERTIES_ITEMS_PROPERTIES}.name"
VALUE = f"{PROPERTIES_ITEMS_PROPERTIES}.value"
VALUE_DATA_TYPE = f"{PROPERTIES_ITEMS_PROPERTIES}.value_data_type"
STRING_VALUE = f"{PROPERTIES_ITEMS_PROPERTIES}.string_value"
NUMERICAL_VALUE = f"{PROPERTIES_ITEMS_PROPERTIES}.numerical_value"
NUMERICAL_VALUE_UNIT = f"{PROPERTIES_ITEMS_PROPERTIES}.numerical_value_unit"
BOOLEAN_VALUE = f"{PROPERTIES_ITEMS_PROPERTIES}.boolean_value"

TIME = f"{PROPERTIES_ITEMS_PROPERTIES}.time"
TIME_PROPERTIES = f"{TIME}.properties"
TIME_START = f"{TIME_PROPERTIES}.start"
TIME_CREATED = f"{TIME_PROPERTIES}.created"
TIME_STOP = f"{TIME_PROPERTIES}.stop"
TIME_DURATION = f"{TIME_PROPERTIES}.duration"
TIME_LAST_UPDATED = f"{TIME_PROPERTIES}.last_updated"
TIME_ACQUIRED = f"{TIME_PROPERTIES}.acquired"
TIME_MODIFIED = f"{TIME_PROPERTIES}.modified"
TIME_LOOKUP = f"{TIME_PROPERTIES}.lookup"

TIME_RAW = f"{TIME_PROPERTIES}.raw"
TIME_RAW_PROPERTIES = f"{TIME_RAW}.properties"
TIME_RAW_START = f"{TIME_RAW_PROPERTIES}.start"
TIME_RAW_CREATED = f"{TIME_RAW_PROPERTIES}.created"
TIME_RAW_STOP = f"{TIME_RAW_PROPERTIES}.stop"
TIME_RAW_DURATION = f"{TIME_RAW_PROPERTIES}.duration"
TIME_RAW_LAST_UPDATED = f"{TIME_RAW_PROPERTIES}.last_updated"
TIME_RAW_ACQUIRED = f"{TIME_RAW_PROPERTIES}.acquired"
TIME_RAW_MODIFIED = f"{TIME_RAW_PROPERTIES}.modified"
TIME_RAW_LOOKUP = f"{TIME_RAW_PROPERTIES}.lookup"

# Leafs that all share the same nullable string type
nullabe_string_leafs = dict.fromkeys(
    [
        SOURCE_NAME,
        SOURCE_TYPE,
        STRING_VALUE,
        TIME_START,
        TIME_CREATED,
        TIME_STOP,
        TIME_DURATION,
        TIME_LAST_UPDATED,
        TIME_ACQUIRED,
        TIME_MODIFIED,
        TIME_LOOKUP,
        TIME_RAW_START,
        TIME_RAW_CREATED,
        TIME_RAW_STOP,
        TIME_RAW_DURATION,
        TIME_RAW_LAST_UPDATED,
        TIME_RAW_ACQUIRED,
        TIME_RAW_MODIFIED,
        TIME_RAW_LOOKUP,
    ],
    {"type": ["string", "null"]},
)


path_to_checks = {
    **nullabe_string_leafs,
    PROPERTIES: {"type": "array"},
    ITEMS: {"type": "object"},
    SOURCE: {
        "type": "object",
        "required": ["name", "type"],
    },
    NAME: {"type": "string"},
    VALUE: {"type": "string"},
    VALUE_DATA_TYPE: {"type": "string"},
    NUMERICAL_VALUE: {"type": ["number", "null"]},
    NUMERICAL_VALUE_UNIT: {
        "type": ["string", "null"],
    },
    BOOLEAN_VALUE: {"type": ["boolean", "null"]},
    TIME: {"type": "object", "required": ["lookup"]},
    TIME_RAW: {"type": "object", "required": ["lookup"]},
}
