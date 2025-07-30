from __future__ import annotations

import copy
from typing import Dict, List

from ids_validator.helpers.athena.athena_helper import AthenaHelper
from ids_validator.helpers.athena.athena_logger import athena_logger
from ids_validator.helpers.athena.constants import (
    FIELD_VALUE_KEY,
    FULL_LIST_OF_VALUES,
    MY_CHILD_TABLES,
    MY_PARENT_TABLE,
    PARENT_UUID_PARAM_NAME,
    UUID_PARAM_NAME,
    get_parent_uuid_field,
    get_property_to_skip,
    get_service_fields,
    get_uuid_field,
    is_list_of_objects,
    is_list_of_primitive_types,
)
from ids_validator.helpers.athena.exceptions import InvalidColumn
from ids_validator.helpers.helpers_methods import merge

MERGE = "merge"

DEEP_COPY = "deep_copy"

# Athena and many other DBs restrict the column length to <=255 characters
MAXIMUM_COLUMN_LENGTH = 255


class TablesStructureBuilder:
    def __init__(self):
        self.partition: Dict = {}
        self.in_root_table = False
        self.level = 0
        self.full_list_of_values = []
        self.table_prefix = None
        self.called_from = ""
        self.parent_table_name_to_pass = ""
        self.tmp_uuid_value = None
        self.table_object: dict = None
        self.parent_uuid = None
        self.table_name_to_create = None
        self._with_another_root = False
        self.parent_table_name = None
        self.parent_column_name = None
        self.root_table = None
        self.data_object: dict = {}
        self.logger = athena_logger("IdsJsonBuilder")

    def with_data_object(self, data_object: dict) -> TablesStructureBuilder:
        self.data_object = copy.deepcopy(data_object)
        return self

    def with_root_table(self, root_table: str) -> TablesStructureBuilder:
        self.root_table = root_table
        return self

    def with_parent_column_name(
        self, parent_column_name: str
    ) -> TablesStructureBuilder:
        self.parent_column_name = parent_column_name
        return self

    def with_parent_table_name(self, parent_table_name: str) -> TablesStructureBuilder:
        if self.root_table is None:
            raise RuntimeError("should set root table before parent table")
        self.parent_table_name = parent_table_name
        self._with_another_root = parent_table_name == self.root_table
        return self

    def with_table_name_to_ceate(
        self, table_name_to_ceate: str
    ) -> TablesStructureBuilder:
        self.table_name_to_create = table_name_to_ceate
        return self

    def with_parent_uuid(self, parent_uuid: str) -> TablesStructureBuilder:
        self.parent_uuid = parent_uuid
        return self

    def with_tables_object(self, tables_object: dict) -> TablesStructureBuilder:
        self.table_object = copy.deepcopy(tables_object)
        return self

    def with_new_table(self, need_to_init=True) -> TablesStructureBuilder:
        if need_to_init:
            self.table_object, self.tmp_uuid_value = self.init_table()
        return self

    def with_called_from(self, called_from: str) -> TablesStructureBuilder:
        self.called_from = called_from
        return self

    def with_level(self, level: int) -> TablesStructureBuilder:
        self.level = level + 1
        return self

    def with_partition(self, partition: dict) -> TablesStructureBuilder:
        self.partition = partition

        return self

    def with_in_root_table(self, in_root_table: bool) -> TablesStructureBuilder:
        """this property intent to work in case when root table is not == to "root" but is a table across others in
        this case arrays in this table should be named differently by adding root_table_name into the table name,
        and objects on the 1rst level to be opposite named without table name that they belong to.

        it is calculated based on the current level of recurrence and table and current property name correlation
        self.root_table==_property and self.level==0
        should be False by default
        """

        self.in_root_table = in_root_table
        return self

    def with_full_list_of_values(
        self, full_list_of_values: List[dict]
    ) -> TablesStructureBuilder:
        for _value in full_list_of_values:
            running_dict = {}
            for key in _value:
                if key not in get_service_fields():
                    running_dict.update({key: _value[key]})
            self.full_list_of_values.append(running_dict)
        return self

    def build(self) -> dict:
        # search thought the properties
        if self.called_from == "list":
            parent_name_to_set = self.table_name_to_create
            table_name_for_update = self.table_name_to_create
        elif self.called_from == "object":
            parent_name_to_set = self.parent_table_name
            table_name_for_update = self.parent_table_name

        for _property in self.data_object:
            if _property in get_property_to_skip():
                continue
            else:
                self.update_table(_property, parent_name_to_set, table_name_for_update)

        return self.table_object

    def clean(self):
        self.full_list_of_values = []

    def update_table(self, _property, parent_name_to_set, table_name_for_update):
        column_name_to_add = self.get_column_name(_property)
        table_name_to_create = self.get_table_name_to_create(_property)

        self.add_parent_table_to_result()

        if is_list_of_primitive_types(self.data_object[_property]):
            if (
                self.parent_table_name == self.root_table
                and self.called_from == "object"
            ):
                self.table_object[self.root_table].update(
                    {column_name_to_add: self.data_object[_property]}
                )
            elif (
                self.parent_table_name == self.root_table and self.called_from == "list"
            ):
                # if we come from first level table, we need to create new tale and seed this list of primitive
                # types to it
                self.table_object[self.table_name_to_create].update(
                    {column_name_to_add: self.data_object[_property]}
                )
            else:
                self.table_object[table_name_for_update].update(
                    {column_name_to_add: self.data_object[_property]}
                )
        elif is_list_of_objects(self.data_object[_property]):

            _value = []
            for idx, list_element in enumerate(self.data_object[_property]):
                _build = (
                    TablesStructureBuilder()
                    .with_root_table(self.root_table)
                    .with_called_from("list")
                    .with_table_name_to_ceate(table_name_to_create)
                    .with_data_object(list_element)
                    .with_parent_uuid(self.tmp_uuid_value)
                    .with_parent_column_name("")
                    .with_parent_table_name(parent_name_to_set)
                    .with_new_table()
                    .with_in_root_table(
                        self.root_table == _property and self.level == 0
                    )
                    .with_level(self.level)
                    .build()
                )

                _value.append(copy.deepcopy(_build))

                if idx == 0:
                    # add to the column structure to the table_object
                    deepcopy = copy.deepcopy(self.table_object)

                    self.table_object = merge(deepcopy, _value[0])

            self.with_full_list_of_values([_v[table_name_to_create] for _v in _value])
            self.table_object[table_name_to_create][FULL_LIST_OF_VALUES].extend(
                self.full_list_of_values
            )

            self.clean()

        else:
            if FIELD_VALUE_KEY in self.data_object[_property]:
                self.calculate_field_with_value(
                    _property,
                    column_name_to_add,
                    table_name_for_update,
                )
            else:
                _value = (
                    TablesStructureBuilder()
                    .with_root_table(self.root_table)
                    .with_called_from("object")
                    .with_parent_table_name(parent_name_to_set)
                    .with_table_name_to_ceate(table_name_to_create)
                    .with_data_object(self.data_object[_property])
                    .with_parent_uuid(self.tmp_uuid_value)
                    .with_parent_column_name(column_name_to_add)
                    .with_tables_object(self.table_object)
                    .with_in_root_table(
                        self.root_table == _property and self.level == 0
                    )
                    .with_level(self.level)
                    .build()
                )
                self.table_object = merge(self.table_object, _value)

    def calculate_field_with_value(
        self, _property, column_name_to_add, table_name_for_update
    ):
        self.table_object[table_name_for_update].update(
            {column_name_to_add: self.data_object[_property]}
        )

    def add_parent_table_to_result(self):
        if self.parent_table_name not in self.table_object:
            self.table_object.update({self.parent_table_name: {}})

    def get_column_name(self, _property) -> str:
        if self.parent_column_name == "" or (
            self.table_name_to_create == self.root_table and self.in_root_table
        ):
            _column_name_to_add = _property.replace("@", "")
        else:
            _column_name_to_add = (
                self.parent_column_name + "_" + _property.replace("@", "")
            )

        if len(_column_name_to_add) > MAXIMUM_COLUMN_LENGTH:
            raise InvalidColumn(
                f"Resolved column length exceeds the maximum column character count of {MAXIMUM_COLUMN_LENGTH}."
                f" The IDS path '{self.data_object.get(_property).get('json_path')}' results in the resolved column,"
                f" '{_column_name_to_add}'"
            )

        return _column_name_to_add.lower()

    def get_table_name_to_create(self, _property):
        if self.table_name_to_create == self.root_table and not self.in_root_table:
            create = _property
        else:
            create = self.table_name_to_create + "_" + _property
        return create

    def init_table(self):
        """Injecting service fields: UUID, PARENT_UUID, PROJECT and partitions"""

        tables_columns3: Dict = {
            MY_CHILD_TABLES: [],
            MY_PARENT_TABLE: "",
            FULL_LIST_OF_VALUES: [],
        }
        tables_columns = {
            self.table_name_to_create: {**tables_columns3, **self.partition}
        }

        tmp_uuid = get_uuid_field()
        tmp_uuid_value = AthenaHelper().fake_the_field(
            get_uuid_field()[UUID_PARAM_NAME], UUID_PARAM_NAME
        )
        tmp_uuid[UUID_PARAM_NAME].update({FIELD_VALUE_KEY: tmp_uuid_value})
        tables_columns[self.table_name_to_create].update(tmp_uuid)

        if self.table_name_to_create != self.parent_table_name:
            tables_columns[self.table_name_to_create].update(get_parent_uuid_field())
            tables_columns[self.table_name_to_create][PARENT_UUID_PARAM_NAME][
                FIELD_VALUE_KEY
            ] = self.parent_uuid
            tables_columns[self.table_name_to_create][
                MY_PARENT_TABLE
            ] = self.parent_table_name

        return tables_columns, tmp_uuid_value
