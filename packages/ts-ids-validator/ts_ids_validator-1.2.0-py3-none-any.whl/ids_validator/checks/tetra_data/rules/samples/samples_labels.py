from ids_validator.checks.rules_checker import BackwardCompatibleType
from ids_validator.checks.tetra_data.rules.samples.samples_root import ITEMS_PROPERTIES

LABELS = f"{ITEMS_PROPERTIES}.labels"
ITEMS = f"{LABELS}.items"
PROPERTIES = f"{ITEMS}.properties"
SOURCE = f"{PROPERTIES}.source"
SOURCE_PROPERTIES = f"{SOURCE}.properties"
SOURCE_NAME = f"{SOURCE_PROPERTIES}.name"
SOURCE_TYPE = f"{SOURCE_PROPERTIES}.type"
NAME = f"{PROPERTIES}.name"
VALUE = f"{PROPERTIES}.value"

TIME = f"{PROPERTIES}.time"
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
        SOURCE_TYPE,
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
    LABELS: {
        "type": "array",
    },
    ITEMS: {
        "type": "object",
        "required": ["source", "name", "value", "time"],
    },
    SOURCE: {
        "type": "object",
        "required": ["name", "type"],
    },
    SOURCE_NAME: {  # root.properties.labels.items.properties.source.properties.name
        "compatible_type": BackwardCompatibleType(
            preferred=["string", "null"], deprecated=("string",)
        )
    },
    NAME: {"type": "string"},
    VALUE: {"type": "string"},
    TIME: {"type": "object", "required": ["lookup"]},
    TIME_RAW: {"type": "object", "required": ["lookup"]},
}
