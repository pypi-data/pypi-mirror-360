from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import List

from ids_validator.ids_node import Node
from ids_validator.models.validator_parameters import ValidatorParameters


class Log(IntEnum):
    """Log levels enum"""

    INFO = -1
    WARNING = 0
    CRITICAL = 1


@dataclass(frozen=True, order=True)
class CheckResult:
    """The result of a validator check"""

    message: str
    level: Log

    @classmethod
    def info(cls, message: str) -> "CheckResult":
        """Create a CheckResult with a warning level"""
        return cls(message, Log.INFO)

    @classmethod
    def warning(cls, message: str) -> "CheckResult":
        """Create a CheckResult with a warning level"""
        return cls(message, Log.WARNING)

    @classmethod
    def critical(cls, message: str) -> "CheckResult":
        """Create a CheckResult with a critical level"""
        return cls(message, Log.CRITICAL)


CheckResults = List[CheckResult]


class AbstractChecker(metaclass=ABCMeta):
    """The abstract definition of a node checker

    A checker contains a `run` method which runs checks on a node and produces check
    results. A concrete checker class can be made like this:

    ```
    class ConcreteChecker(AbstractChecker):
        @classmethod
        def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
            # check something about the node, given some context
            return []
    ```
    This checker class can then be added to a list of checks to run on a schema.
    """

    bulk_checker: bool = False

    @classmethod
    @abstractmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        """Run this checker's checks on a node with a given context, returning the
        results of those checks
        """
        raise NotImplementedError
