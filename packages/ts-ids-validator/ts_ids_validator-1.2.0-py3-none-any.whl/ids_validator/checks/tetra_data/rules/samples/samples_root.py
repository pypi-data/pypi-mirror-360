SAMPLES = "root.properties.samples"
ITEMS = f"{SAMPLES}.items"
ITEMS_PROPERTIES = f"{ITEMS}.properties"
ID = f"{ITEMS_PROPERTIES}.id"
BARCODE = f"{ITEMS_PROPERTIES}.barcode"
NAME = f"{ITEMS_PROPERTIES}.name"

BATCH = f"{ITEMS_PROPERTIES}.batch"
BATCH_PROPERTIES = f"{BATCH}.properties"
BATCH_ID = f"{BATCH_PROPERTIES}.id"
BATCH_NAME = f"{BATCH_PROPERTIES}.name"
BATCH_BARCODE = f"{BATCH_PROPERTIES}.barcode"

SET = f"{ITEMS_PROPERTIES}.set"
SET_PROPERTIES = f"{SET}.properties"
SET_ID = f"{SET_PROPERTIES}.id"
SET_NAME = f"{SET_PROPERTIES}.name"

LOT = f"{ITEMS_PROPERTIES}.lot"
LOT_PROPERTIES = f"{LOT}.properties"
LOT_ID = f"{LOT_PROPERTIES}.id"
LOT_NAME = f"{LOT_PROPERTIES}.name"


path_to_checks = {
    SAMPLES: {
        "type": "array",
    },
    ITEMS: {
        "type": "object",
    },
    ID: {"type": ["string", "null"]},
    BARCODE: {"type": ["string", "null"]},
    NAME: {"type": ["string", "null"]},
    BATCH: {"type": "object"},
    BATCH_ID: {"type": ["string", "null"]},
    BATCH_NAME: {"type": ["string", "null"]},
    BATCH_BARCODE: {"type": ["string", "null"]},
    SET: {"type": "object"},
    SET_ID: {"type": ["string", "null"]},
    SET_NAME: {"type": ["string", "null"]},
    LOT: {"type": "object"},
    LOT_ID: {"type": ["string", "null"]},
    LOT_NAME: {"type": ["string", "null"]},
}
