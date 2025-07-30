from __future__ import annotations

import copy

from ids_validator.helpers.athena.constants import (
    FIELD_VALUE_KEY,
    get_service_fields,
    is_list_of_primitives_values,
)


class IdsJsonBuilder:
    def __init__(self):
        self.data_object: dict = {}

    def with_data_object(self, data_object: dict) -> IdsJsonBuilder:
        self.data_object = copy.deepcopy(data_object)
        return self

    def build(self) -> dict:
        _running_ids_json = {}
        if FIELD_VALUE_KEY in self.data_object:
            return self.data_object[FIELD_VALUE_KEY]
        for _property in self.data_object:
            it_is_list = isinstance(self.data_object[_property], list)
            it_is_list_of_primitives = is_list_of_primitives_values(
                self.data_object[_property]
            )

            if FIELD_VALUE_KEY in self.data_object[_property]:
                _running_ids_json.update(
                    {_property: self.data_object[_property][FIELD_VALUE_KEY]}
                )
            elif it_is_list_of_primitives:
                _running_ids_json.update({_property: self.data_object[_property]})
            elif it_is_list:
                _running_ids_json.update(
                    {
                        _property: [
                            IdsJsonBuilder().with_data_object(element).build()
                            for element in self.data_object[_property]
                        ]
                    }
                )
            elif _property not in get_service_fields():
                _running_ids_json.update(
                    {
                        _property: IdsJsonBuilder()
                        .with_data_object(self.data_object[_property])
                        .build()
                    }
                )

        return _running_ids_json
