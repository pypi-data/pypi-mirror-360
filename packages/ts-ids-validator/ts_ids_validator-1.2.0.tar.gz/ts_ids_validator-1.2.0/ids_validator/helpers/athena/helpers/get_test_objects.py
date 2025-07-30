import copy
from typing import Dict, List

from ids_validator.helpers.athena.athena_logger import athena_logger
from ids_validator.helpers.athena.builders.data_object_builder import (
    DataObjectFromSchemaBuilder,
)
from ids_validator.helpers.athena.builders.ids_json_builder import IdsJsonBuilder
from ids_validator.helpers.athena.builders.tables_structure_builder import (
    TablesStructureBuilder,
)
from ids_validator.helpers.athena.constants import (
    FIELD_TYPE_KEY,
    FIELD_VALUE_KEY,
    FULL_LIST_OF_VALUES,
    PARTITIONS_KEY,
    REQUIRED_KEY,
    get_service_fields,
)
from ids_validator.helpers.athena.dto.athena_data_object import TestObject
from ids_validator.helpers.athena.helpers.data_object_modifier import DataObjectModifier


def get_test_objects(source_json: dict) -> TestObject:
    logger = athena_logger("get_test_objects")
    schema_json = source_json["schema"]
    athena_json = source_json["athena"]
    try:
        _root_table_name = athena_json["root"]
    except KeyError:
        raise KeyError(
            "'root' is not defined in athena.json. All IDS artifacts must have a root table defined."
        )
    tables_prefix = source_json["table_prefix"]

    object_to_return = TestObject()
    logger.debug("creating data_object")

    object_to_return.data_object = (
        DataObjectFromSchemaBuilder(schema_json)
        .with_table_prefix(tables_prefix)
        .with_schema(schema_json)
        .with_parent_table_name(_root_table_name)
        .with_material(schema_json)
        .with_root_table(_root_table_name)
        .build()
    )

    object_to_return.ids_json = (
        IdsJsonBuilder().with_data_object(object_to_return.data_object).build()
    )
    # this is a first "easy place to get values for partition columns. before this they are hidden in data object

    partition_json = get_partitions_columns(athena_json, object_to_return.ids_json)

    # so if there are partitions columns we need to look thought data object, inject_existing_partition those to each array that would
    # be table (ex. not primitives) at the same time ids should be not regenerated, as partitions would be added by
    # Athena engine.

    logger.debug("injecting partition")
    object_to_return.data_object = (
        DataObjectModifier()
        .with_partition(partition_json)
        .with_dataobject(object_to_return.data_object)
        .inject_partition()
    )
    logger.debug("creating table structure")
    object_to_return.table_structure = (
        TablesStructureBuilder()
        .with_data_object(object_to_return.data_object)
        .with_called_from("object")
        .with_root_table(_root_table_name)
        .with_parent_table_name(_root_table_name)
        .with_table_name_to_ceate(_root_table_name)
        .with_partition(partition_json)
        .with_parent_column_name("")
        .with_parent_uuid("")
        .with_new_table()
        .build()
    )

    logger.debug("creating update_full_list_of_values")
    object_to_return.table_structure = update_full_list_of_values(
        object_to_return.table_structure
    )

    return object_to_return


def get_value_from_json_by_path(schema_json, path: str):
    path_finder: dict = copy.deepcopy(schema_json)
    for node in path.split("."):
        path_finder = path_finder.get(node)
    return path_finder


def get_partitions_columns(athena_json: List[Dict[str, str]], schema_json):
    to_return = {}
    if PARTITIONS_KEY in athena_json:
        for x in athena_json[PARTITIONS_KEY]:
            to_return.update(
                {
                    x["name"]: {
                        FIELD_VALUE_KEY: get_value_from_json_by_path(
                            schema_json, x["path"]
                        ),
                        FIELD_TYPE_KEY: ["string"],
                        REQUIRED_KEY: False,
                    }
                }
            )

    return to_return


def update_full_list_of_values(income_table_structure):
    table_structure = copy.deepcopy(income_table_structure)
    for table in table_structure:
        if len(table_structure[table][FULL_LIST_OF_VALUES]) == 0:
            full_list_of_values = {}
            for _field in table_structure[table]:
                if _field not in get_service_fields():
                    full_list_of_values.update({_field: table_structure[table][_field]})
            table_structure[table][FULL_LIST_OF_VALUES] = [full_list_of_values]
    return table_structure
