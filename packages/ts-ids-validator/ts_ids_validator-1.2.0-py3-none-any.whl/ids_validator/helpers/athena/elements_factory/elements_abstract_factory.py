from __future__ import annotations

from abc import ABC

from ids_validator.helpers.athena.elements_factory.elements_factory_interface import (
    ElementsFactory,
)
from ids_validator.helpers.athena.elements_factory.from_schema.elements_from_schema_factory import (
    ElementsFromSchemaFactory,
)


class ElementsAbstractFactory(ABC):
    def pick_factory_from(self, factory_for: str) -> ElementsFactory:
        if factory_for == "schema":
            return ElementsFromSchemaFactory()
        else:
            raise RuntimeError("no factory to select")
