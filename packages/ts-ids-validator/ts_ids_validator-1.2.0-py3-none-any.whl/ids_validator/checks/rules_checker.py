from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Set, Union

from pydash import get

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
)
from ids_validator.ids_node import Node
from ids_validator.models.validator_parameters import ValidatorParameters


@dataclass
class BackwardCompatibleType:
    """Represents a type with one or more backward-compatible deprecated types.

    If a node's type matches the preferred type, no warnings or errors will be logged.
    If a node's type matches a deprecated type, a warning will be logged. This means
    validation will not fail for these types, but the user will be told that the type
    being used is deprecated.
    """

    preferred: Union[list, str]
    deprecated: Sequence[Union[list, str]]


@dataclass
class PropertyConstraints:
    """Represents the minimum properties which must be present in an object, plus
    extra properties which may or may not be present
    """

    minimum: Set[str]
    allowed_extra: Optional[Set[str]]


def types_match(
    node_type: Union[str, List[str]], expected_type: Union[str, List[str]]
) -> bool:
    """Determine whether two jsonschema types match, accounting for types which are a
    list of types, or a single type
    """
    if type(node_type) != type(expected_type):
        return False

    if isinstance(expected_type, list):
        node_type = sorted(node_type)
        expected_type = sorted(expected_type)

    return node_type == expected_type


class RuleBasedChecker(AbstractChecker):
    # Provide rules dict when subclassing RuleBasedChecker
    rules: ClassVar[Dict[str, Any]]

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        paths = list(cls.rules.keys())

        node_path = str(node.path)

        if node_path in paths:
            checks = cls.rules[node_path]
            if checks:
                logs += cls.enforce_checks(node, checks)

        return logs

    @classmethod
    def enforce_checks(cls, node: Node, checks: dict) -> CheckResults:
        logs: CheckResults = []
        if "type" in checks:
            logs += cls.enforce_type(node, checks.get("type"))
        if "compatible_type" in checks:
            logs += cls.enforce_compatible_type(node, checks.get("compatible_type"))
        if "required" in checks:
            logs += cls.enforce_required(node, checks.get("required"))
        if "min_required" in checks:
            logs += cls.enforce_min_required(node, checks.get("min_required"))
        if "min_properties" in checks:
            minimum = set(checks["min_properties"])
            logs += cls.enforce_min_properties(node, minimum)
        return logs

    @staticmethod
    def enforce_type(node: Node, type_: Union[List[str], str]) -> CheckResults:
        """Enforce that a node has a specific type"""
        logs: CheckResults = []

        # don't allow "null" if "const" is defined
        # schema will be enforced only when const is not
        # defined
        if "const" in node.data:
            is_valid, msg = node._check_const_type()
            if not is_valid:
                logs += [CheckResult.critical(msg)]
                return logs
            return logs

        if not types_match(node.type_, type_):
            logs += [CheckResult.critical(f"'type' must be {type_}")]

        return logs

    @staticmethod
    def enforce_compatible_type(
        node: Node, compatible_type: BackwardCompatibleType
    ) -> CheckResults:
        """Enforces that the node type matches a preferred or deprecated type.

        If the type matches the preferred type: no warnings or errors
        If the type matches a deprecated type: log a warning
        Otherwise the type isn't allowed: log a critical error
        """
        logs: CheckResults = []
        preferred_type = compatible_type.preferred
        deprecated_types = compatible_type.deprecated

        if "const" in node.data:
            is_valid, msg = node._check_const_type()
            if not is_valid:
                logs += [CheckResult.critical(msg)]
                return logs
            return logs

        if types_match(node.type_, preferred_type):
            return logs

        for deprecated_type in deprecated_types:
            if types_match(node.type_, deprecated_type):
                logs += [
                    CheckResult.warning(
                        f"'type' '{node.type_}' is deprecated but allowed for backward "
                        f"compatibility, please use `{preferred_type}` instead."
                    )
                ]
                return logs

        logs += [
            CheckResult.critical(
                f"'type' must be {preferred_type}, "
                f"or one of these deprecated types: {deprecated_types}"
            )
        ]

        return logs

    @staticmethod
    def enforce_required(node: Node, required: list) -> CheckResults:
        """Enforce that a node has specific required properties"""
        logs: CheckResults = []
        node_required: List[str] = node.get("required", [])

        if set(node_required) != set(required):
            logs += [CheckResult.critical(f"'required' must be set to {required}.")]

        return logs

    @staticmethod
    def enforce_min_required(node: Node, required: list) -> CheckResults:
        """The node's `required` contains at least a minimum set of values."""
        logs: CheckResults = []
        min_required = set(required)
        node_required = node.get("required", [])
        if not isinstance(node_required, list):
            logs += [CheckResult.critical(f"'required' must contain {min_required}")]
            return logs

        node_required = set(node_required)
        missing = min_required - node_required
        if missing:
            logs += [CheckResult.critical(f"'required' must contain {missing}")]

        return logs

    @staticmethod
    def enforce_min_properties(node: Node, minimum: Set[str]) -> CheckResults:
        """Enforce that at least a minimum set of properties are present."""
        node_properties = get(node, "properties") or get(node, "items.properties") or {}
        node_properties = set(node_properties.keys())
        logs: CheckResults = []

        missing_properties = minimum - node_properties

        if missing_properties:
            logs.append(
                CheckResult.critical(
                    f"'properties' must contain {sorted(missing_properties)}"
                )
            )

        return logs
