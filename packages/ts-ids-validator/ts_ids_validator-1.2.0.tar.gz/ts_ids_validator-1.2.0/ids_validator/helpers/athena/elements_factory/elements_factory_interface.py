from abc import ABC, abstractmethod

from ids_validator.helpers.athena.elements_factory.element_interface import (
    ElementToWorkWith,
)


class ElementsFactory(ABC):
    """
    The Product interface declares the operations that all concrete products
    must implement.
    """

    @abstractmethod
    def pick_generator(self, _running_schema_property) -> ElementToWorkWith:
        pass
