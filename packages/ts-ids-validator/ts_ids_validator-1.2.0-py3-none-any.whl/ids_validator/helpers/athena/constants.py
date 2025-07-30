REQUIRED_KEY = "required"
PRIMITIVE_PROPERTIES = "required_primitive_properties"
PROJECT = "project"
INJECTED_REF = "injected_ref"
ERROR_RESPONSE = "ErrorResponse"
NULL_PARTIAL_ALLOWED = "Partial Allowed"
RAN_QUERY_ID_FIELD_NAME = "ran_query_id"
NOT_FOR_EXPORTING_KEY = "not_for_exporting"
SELECT_QUERY = "select_query"
SQL_WHERE = "WHERE"
SQL_SELECT = "SELECT"
SQL_FROM = "FROM"
ROOT_TABLE_ID_FIELD = "uuid"
MY_PARENT_TABLE = "my_parent_table"
MY_CHILD_TABLES = "my_child_tables"
FULL_LIST_OF_VALUES = "full_list_of_values"
CUSTOM_FIELDS = "custom_fields"
DATACUBE = "datacube"
PARENT_UUID_PARAM_NAME = "parent_uuid"
UUID_PARAM_NAME = "uuid"
EXAMPLE_IDS = "example_ids"
EXAMPLE_VALUE = "example_value"
EXAMPLE_TYPE = "example_type"
FIELD_TYPE_KEY = "field_type"
OBJECT_TYPE_IN_JSON_KEY = "type"
SCHEMA_TYPE_KEY = "type"
FIELD_VALUE_KEY = "field_value"
SYNTHETIC_IDS_PROCESSING = "Athena synthetic IDS processing"
PARTITIONS_KEY = "partitions"
DEFAULT_ELEMENTS_IN_ARRAYS = 1
AUTO_GENERATED = "athena-trace"
JSON_PATH = "json_path"

EXPLICIT_LOGS = False


def get_service_fields_names():
    return (
        "@idsNamespace",
        "@idsType",
        "@idsVersion",
        "@idsConventionVersion",
    )


def get_primitive_types():
    return "string", "float", "number", "boolean", "integer", True, False, "null"


def get_property_to_skip():
    return "custom_fields", "datacubes", JSON_PATH


def is_list_of_primitives_values(param) -> bool:
    if not isinstance(param, list):
        return False
    for x in param:
        if not isinstance(x, (bool, int, str, float)):
            return False
    return True


def is_list_of_objects(object_to_validate) -> bool:
    if is_list_of_primitives_values(object_to_validate):
        return False
    if isinstance(object_to_validate, list):
        for element in object_to_validate:
            if FIELD_TYPE_KEY not in element:
                # not FIELD_TYPE_KEY in the field -> list of objects
                return True
            if not is_list_of_primitives_values(element[FIELD_TYPE_KEY]):
                # list of not primitives -> objects
                return True  # TODO no unit test covers this
    return False


def is_list_of_primitives(object_to_validate) -> bool:
    return is_list_of_primitive_types(
        object_to_validate
    ) or is_list_of_primitives_values(object_to_validate)


def is_list_of_primitive_types(object_to_validate) -> bool:
    if is_list_of_primitives_values(object_to_validate):
        return False
    if isinstance(object_to_validate, list):
        if len(object_to_validate) == 0:
            return False  # TODO no unit test covers this
        for element in object_to_validate:
            if FIELD_TYPE_KEY not in element:
                # not FIELD_TYPE_KEY in the field -> list of objects
                return False
            if not is_list_of_primitives_values(element[FIELD_TYPE_KEY]):
                # list of not primitives -> objects
                return False  # TODO no unit test covers this
    else:
        return False
    return True


def get_service_fields():
    object_to_return = (
        MY_CHILD_TABLES,
        MY_PARENT_TABLE,
        PRIMITIVE_PROPERTIES,
        FULL_LIST_OF_VALUES,
        JSON_PATH,
    )

    return object_to_return


def get_parent_uuid_field():
    return {
        PARENT_UUID_PARAM_NAME: {
            FIELD_TYPE_KEY: ["string"],
            REQUIRED_KEY: False,
            NOT_FOR_EXPORTING_KEY: True,
        }
    }


def get_uuid_field():
    return {
        UUID_PARAM_NAME: {
            FIELD_TYPE_KEY: ["string"],
            REQUIRED_KEY: False,
            NOT_FOR_EXPORTING_KEY: True,
        }
    }


GOOD_SCHEMAS = (
    "agilent-chemstation",
    "air-particle-counter-beckmancoulter-met-one-3400",
    "alex-uat-demo",
    "assay-ddi",
    "assay-logd",
    "assay-protein-binding",
    "assay-solubility",
    "bio-reactor",
    "biochemistry-analyzer",
    "bioreactor-sartorius-ambr250",
    "blood-gas-analyzer-radiometer-america-abl90",
    "blood-gas-analyzer-siemens-rapidlab",
    "cell-counter-v8",
    "chromatography-order",
    "component",
    "ddpcr-biorad-quantasofxtht",
    "dissolution-apparatus-agilent-400ds",
    "dissolution-apparatus-agilent-400ds-usp7",
    "dissolution-tester-pion",
    "dissolution-tester-sotax-at70",
    "dotmatics-register-compound",
    "dsf-nanotemper-prometheus",
    "electromechanical-testing-mts-insight2ok",
    "endotoxin-software-charles-river-endoscan",
    "endotoxin_tester_charles_river_endosafe_nexus",
    "example",
    "filtration",
    "flow-cytometer-intellicyt-ique3",
    "flow-imaging-microscopy-yft-flowcam",
    "gel-imager-bio-rad-gel-doc-xr",
    "generic-assay",
    "generic-log-stream",
    "git-workflow-test",
    "hardness-tester-pharmatron-8m",
    "hardness-tester-sotax-st50",
    "headspace-analyzer-lighthouse-fms-oxygen",
    "ids-publish-test",
    "incubator",
    "iot-simple-instrument",
    "kf-coulometer-metrohm-titrino",
    "laser-diffraction-particle-size-analyzer-malvern-mastersizer-2000",
    "laser-diffraction-particle-size-analyzer-malvern-mastersizer-3000",
    "lc-chromeleon",
    "plate-reader-perkinelmer-labchip",
    "plate-reader-perkinelmer-microbeta2",
    "plate-reader-perkinelmer-topcount",
    "plate-reader-sartorius-octet-analysis-studio",
    "plate-reader-luminex-xponent",
    "plate-reader-bmg-labtech-spectrostar",
    "plate-reader-bmg-labtech-nephelostar-fluostar",
    "plate-reader-bmg-labtech-nephelometry-fluorescence",
    "plate-reader-bmg-labtech-clariostar",
    "plate-reader-bmg-labtech-absorbance",
    "plate-reader-biotek-synergy2",
    "plate-reader-biotek-gen5",
    "pion-rainbow",
    "peptide-synthesizer-intavis-multipep-v4-",
    "pcr-thermofisher-quantstudio",
    "osmometer",
    "nmr-bruker",
    "nimbus-2000",
    "nimbus-2000",
    "nils-dei-tools-test",
    "mst-nanotemper-monolith",
    "microscope-leica-aperio",
    "mettler-toledo-labx-audit-trail",
    "mastersizer-malvern-ms2000",
    "mass-balance",
    "mascot-mgf",
    "liquid-scintillation-counter-perkinelmer-quantulus-tricarb",
    "sem-hitachi-su5000",
    "shallow-ids",
    "spectrometer-perkinelmer-spectrum-10",
    "qpcr-thermofisher-7500",
    "qpcr-thermofisher-viia7",
    "spectrophotometer-thermo-fisher-nanodrop-8000",
)

BAD_SCHEMAS = (
    "azure-gel-imager",  # https://tetrascience.atlassian.net/browse/PMSI-504
    "cell-analyzer",  # https://tetrascience.atlassian.net/browse/PMSI-506
    "capillary-electrophoresis-proteinsimple-maurice",  # https://tetrascience.atlassian.net/browse/PMSI-503
    "blood-gas-analyzer",  # https://tetrascience.atlassian.net/browse/PMSI-510
    "capillary-electrophoresis",  # https://tetrascience.atlassian.net/browse/PMSI-511
    "compaction-simulator-rrdi-cs1",  # https://tetrascience.atlassian.net/browse/PMSI-512
    "conductivity-meter",  # https://tetrascience.atlassian.net/browse/PMSI-515
    "plate-reader-tecan-d300e",  # https://tetrascience.atlassian.net/browse/PMSI-516
    "plate-reader-msd-quickplex",  # https://tetrascience.atlassian.net/browse/PMSI-517
    "plate-reader-msd-sector-s-600",  # https://tetrascience.atlassian.net/browse/PMSI-518
    "xray-diffraction-pananalytical",  # https://tetrascience.atlassian.net/browse/PMSI-533,
    "travis-copy-test",  # https://tetrascience.atlassian.net/browse/PMSI-534
    "raman-spectroscopy",  # https://tetrascience.atlassian.net/browse/PMSI-535
    "plate-reader-thermofisher-fluoroskan",  # https://tetrascience.atlassian.net/browse/PMSI-536
    "plate-reader-biotek-synergy2",  # https://tetrascience.atlassian.net/browse/PMSI-537
    "plate-reader",  # https://tetrascience.atlassian.net/browse/PMSI-538
    "ph-meter",  # https://tetrascience.atlassian.net/browse/PMSI-539
    "ome-confocal-imaging-metadata",
    # https://tetrascience.atlassian.net/browse/PMSI-541 Also elastic search section is broken
    "mass-balance",  # https://tetrascience.atlassian.net/browse/PMSI-555
    "plate-reader-bmg-labtech",  # https://tetrascience.atlassian.net/browse/DL-1138
    "lcuv-chromeleon",  # https://tetrascience.atlassian.net/browse/PMSI-556
    "thermo-cycler-inheco-odtc",  # https://tetrascience.atlassian.net/browse/DL-1147rpa
    "fortebio-octet",  # https://tetrascience.atlassian.net/browse/PMSI-566
)
