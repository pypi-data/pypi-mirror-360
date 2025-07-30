from ids_validator.helpers.athena.athena_logger import athena_logger

FILE_ID_PLACEHOLDER = "File_ID_to_be_injected_here"


class TestObject:
    def __init__(self):
        self.table_structure: dict = {}
        self.data_object: dict = {}
        self.sql_queries: dict = {}
        self.ids_json: dict = {}
        self.logger = athena_logger("TestObject")
