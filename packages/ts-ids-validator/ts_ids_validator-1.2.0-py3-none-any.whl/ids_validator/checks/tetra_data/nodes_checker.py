from typing import ClassVar, List, Type

from ids_validator.checks.rules_checker import RuleBasedChecker
from ids_validator.checks.tetra_data.rules.related_files import (
    RULES as RELATED_FILES_RULES,
)
from ids_validator.checks.tetra_data.rules.samples import samples_rules
from ids_validator.checks.tetra_data.rules.samples.samples_root import SAMPLES
from ids_validator.checks.tetra_data.rules.systems import systems_rules
from ids_validator.checks.tetra_data.rules.users import USERS, users_rules
from ids_validator.ids_node import NodePath


class SystemNodeChecker(RuleBasedChecker):
    rules = systems_rules


class EnforcedNodeChecker(RuleBasedChecker):
    """
    Inherit from this class and set the class variables when you want to enforce
    that a schema contains a given set of nodes.

    NOTE: Ensure that you add the subclass of this to ENFORCED_NODE_CHECKS in this module
    """

    # If specific nodes must exist in the schema provide a list of the nodes as
    # the string paths (e.g root.properties.foo) when subclassing RuleBasedChecker
    enforced_nodes: ClassVar[List[NodePath]]
    reserved_path_prefix: NodePath


class SampleNodeChecker(EnforcedNodeChecker):
    """The schema must contain the exact definition as samples defined here"""

    rules = samples_rules
    enforced_nodes = list(NodePath.from_str(path) for path in samples_rules)
    reserved_path_prefix = NodePath.from_str(SAMPLES)


class UserNodeChecker(EnforcedNodeChecker):
    """The schema definition must contain at least the defined nodes in users"""

    rules = users_rules
    enforced_nodes = list(NodePath.from_str(path) for path in users_rules)
    reserved_path_prefix = NodePath.from_str(USERS)


class RelatedFilesChecker(RuleBasedChecker):
    """
    Check that the related files schema matches the template from the schema conventions
    """

    rules = RELATED_FILES_RULES


ENFORCED_NODE_CHECKS: List[Type[EnforcedNodeChecker]] = [
    SampleNodeChecker,
    UserNodeChecker,
]
