from abc import ABC, abstractmethod


class ElementToWorkWith(ABC):
    """
    The Product interface declares the operations that all concrete products
    must implement.
    """

    @abstractmethod
    def generate_value(
        self, _running_schema_property, input_json, parent_object
    ) -> dict:
        pass
