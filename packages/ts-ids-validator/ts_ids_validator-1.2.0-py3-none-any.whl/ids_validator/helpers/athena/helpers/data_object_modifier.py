from __future__ import annotations

import copy
from threading import Thread
from typing import List

from ids_validator.helpers.athena.constants import (
    FIELD_TYPE_KEY,
    get_service_fields,
    is_list_of_objects,
    is_list_of_primitives,
)


class DataObjectModifier:
    def __init__(self):
        self.dataobject = {}
        self.partition_to_inject = {}
        self._breadcrums = ""

    def with_partition(self, partition_json: dict) -> DataObjectModifier:
        self.partition_to_inject = partition_json
        return self

    def with_breadcrums(self, breadcrums: str) -> DataObjectModifier:
        self._breadcrums = f"{self._breadcrums}>{breadcrums}"
        return self

    def with_dataobject(self, dataobject: dict) -> DataObjectModifier:
        self.dataobject = copy.deepcopy(dataobject)
        return self

    def inject_partition(self) -> dict:
        if self.partition_to_inject != {}:
            self.inject_existing_partition()
        return self.dataobject

    def inject_existing_partition(self) -> dict:
        threads: List[Thread] = []
        for field in self.dataobject:
            t = Thread(target=self.inject_partition_to_field(field))
            threads.append(t)

        # Start all threads
        for x in threads:
            x.start()

        # Wait for all of them to finish
        for x in threads:
            x.join()

        # logger.debug(f" exit from inject_existing_partition {self._breadcrums}>{field}")
        return self.dataobject

    def inject_partition_to_field(self, field):
        if field not in get_service_fields():
            if isinstance(self.dataobject[field], list):
                if is_list_of_objects(self.dataobject[field]):
                    for i in range(len(self.dataobject[field])):
                        # running injection for each object in array
                        self.dataobject[field][i] = (
                            DataObjectModifier()
                            .with_partition(self.partition_to_inject)
                            .with_breadcrums(f"{self._breadcrums}>{field}")
                            .with_dataobject(self.dataobject[field][i])
                            .inject_partition()
                        )
                if not is_list_of_primitives(self.dataobject[field]):
                    # injecting partition columns to something that would be table
                    for list_element in self.dataobject[field]:
                        list_element.update(self.partition_to_inject)
            elif FIELD_TYPE_KEY not in self.dataobject[field]:
                self.dataobject[field] = (
                    DataObjectModifier()
                    .with_partition(self.partition_to_inject)
                    .with_dataobject(self.dataobject[field])
                    .with_breadcrums(f"{self._breadcrums}>{field}")
                    .inject_partition()
                )
