import re
from collections import Counter

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.ids_node import Node, NodePath

EXCEPTIONS_FIELD_NAMES_WITH_PATH = {
    "@link": "",
    "@idsNamespace": "root",
    "@idsType": "root",
    "@idsVersion": "root",
    "@idsConventionVersion": "root",
}


class AthenaNormalizedFieldNameChecker(AbstractChecker):
    """
    Checks that field names adhere to platform requirements
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        """
        Validate Node properties do not contain invalid characters in field names.

        Args:
            node: current node of the JSON
            context: ValidatorParameters of the current node
        """
        logs: CheckResults = []
        properties = node.properties_dict
        if properties is None:
            return logs

        for key in properties:
            if (key in EXCEPTIONS_FIELD_NAMES_WITH_PATH.keys()) and (
                (EXCEPTIONS_FIELD_NAMES_WITH_PATH.get(key) == str(node.path))
                or EXCEPTIONS_FIELD_NAMES_WITH_PATH.get(key) == ""
            ):
                continue

            logs = cls.special_characters_check(key, logs, node.path)
            logs = cls.several_underscores_check(key, logs, node.path)
            logs = cls.leading_underscore_check(key, logs, node.path)

        return logs

    @staticmethod
    def leading_underscore_check(
        field_name: str, logs: CheckResults, path: NodePath
    ) -> CheckResults:
        """Checking if we have leading underscore in the property name."""
        match_ = re.match("^_", field_name)
        if match_:
            logs += [
                CheckResult.critical(
                    f"'{path}.{field_name}' has leading underscore(_)."
                    f" This is not allowed for Tetra SQL column names"
                )
            ]
        return logs

    @staticmethod
    def several_underscores_check(
        field_name: str, logs: CheckResults, path: NodePath
    ) -> CheckResults:
        """Checking if we have more than one underscore at a time in the property name."""
        several_underscore = re.findall("_{2,}", field_name)
        number_of_several_underscores = len(several_underscore)
        if number_of_several_underscores > 0:
            logs += [
                CheckResult.critical(
                    f"'{path}.{field_name}' has {number_of_several_underscores} "
                    f"instance{('s' if number_of_several_underscores > 1 else '')} of more then 1 consecutive"
                    f" underscores(_)."
                    f" This is not allowed for Tetra SQL column names"
                )
            ]
        return logs

    @staticmethod
    def special_characters_check(
        field_name: str, logs: CheckResults, path: NodePath
    ) -> CheckResults:
        """Checking if we have special characters in the property name."""
        special_char_counts = Counter(re.findall(r"[\W]", field_name))
        if special_char_counts:
            logs += [
                CheckResult.critical(
                    f"'{path}.{field_name}' has {value} instance{('s' if value > 1 else '')} "
                    f"of special character '{key}'{('(space)' if key == ' ' else '')}  in "
                    f"it. -> Using special characters is not allowed"
                )
                for key, value in special_char_counts.items()
            ]
        return logs
