import uuid

from faker import Faker

from ids_validator.helpers.athena.constants import FIELD_TYPE_KEY

athena_faker = Faker()
athena_faker.seed_instance(4321)


class AthenaHelper:
    def __init__(self):
        # TODO: inherit from test
        self.faker_null_result = None

    # generate null for id fielld so I can't find
    def fake_the_field(self, field, column_name):
        if "enum" in field:
            return athena_faker.random_element(elements=(field["enum"]))
        return self.generate_number(column_name, field)

    def generate_number(self, column_name, field):
        if field[FIELD_TYPE_KEY][0] == "integer":
            # we are returning double/float instead of self._fake.random_number() as per devs do the same
            pydecimal = athena_faker.random_number()
            # pydecimal = self._fake.pyfloat(left_digits=5, right_digits=5)
            return pydecimal
        elif field[FIELD_TYPE_KEY][0] == "number":
            pydecimal = athena_faker.pyfloat(left_digits=5, right_digits=5)
            return pydecimal
        elif field[FIELD_TYPE_KEY][0] == "string":
            # TODO: add more units
            if "unit" in column_name:
                return "".join(
                    athena_faker.random_element(
                        elements=(
                            "Micro Volt",
                            "Micro Volt * Second",
                            "Second",
                        )
                    )
                )
            elif "uuid" == column_name:
                return uuid.uuid4().hex
            else:
                return "".join(athena_faker.random_letters(16))
        elif field[FIELD_TYPE_KEY][0] == "boolean":
            return athena_faker.boolean()
        elif field[FIELD_TYPE_KEY][0] == "null":
            return None

    def get_service_field_value(self, _running_schema_property, schema_prop):
        if _running_schema_property == "@idsNamespace":
            return schema_prop["@idsNamespace"]["const"]
        if _running_schema_property == "@idsType":
            return schema_prop["@idsType"]["const"]
        if _running_schema_property == "@idsVersion":
            return schema_prop["@idsVersion"]["const"]
        if _running_schema_property == "@idsConventionVersion":
            return schema_prop["@idsConventionVersion"]["const"]
