from ids_validator.checks.tetra_data.rules.samples.samples_root import ITEMS_PROPERTIES

LOCATION = f"{ITEMS_PROPERTIES}.location"
LOCATION_PROPERTIES = f"{LOCATION}.properties"

POSITION = f"{LOCATION_PROPERTIES}.position"
ROW = f"{LOCATION_PROPERTIES}.row"
COLUMN = f"{LOCATION_PROPERTIES}.column"
INDEX = f"{LOCATION_PROPERTIES}.index"

HOLDER = f"{LOCATION_PROPERTIES}.holder"
HOLDER_PROPERTIES = f"{HOLDER}.properties"
HOLDER_NAME = f"{HOLDER_PROPERTIES}.name"
HOLDER_TYPE = f"{HOLDER_PROPERTIES}.type"
HOLDER_BARCODE = f"{HOLDER_PROPERTIES}.barcode"


path_to_checks = {
    LOCATION: {
        "type": "object",
    },
    POSITION: {"type": ["string", "null"]},
    ROW: {"type": ["number", "null"]},
    COLUMN: {"type": ["number", "null"]},
    INDEX: {"type": ["number", "null"]},
    HOLDER: {"type": "object"},
    HOLDER_NAME: {"type": ["string", "null"]},
    HOLDER_TYPE: {"type": ["string", "null"]},
    HOLDER_BARCODE: {"type": ["string", "null"]},
}
