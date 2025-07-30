from collections import UserDict
from dataclasses import dataclass
from typing import Iterable, Tuple

from pydash import get


@dataclass(unsafe_hash=True)
class NodePath:
    parts: Tuple[str, ...] = ("root",)
    # Whether this node is a "properties" node, or a schema metadata node
    in_properties: bool = False

    def __post_init__(self):
        """Set `in_properties` based on the parts of the path."""
        in_properties = False
        for part in self.parts:
            if not in_properties and part == "properties":
                # Entering a "properties" node
                in_properties = True
            else:
                # In a schema metadata node
                in_properties = False
        self.in_properties = in_properties

    def name(self):
        """The name of a node is the last part of its path."""
        return self.parts[-1]

    def join(self, part: str) -> "NodePath":
        """Return a new path with an extra part added to the path."""
        in_properties = False
        if not self.in_properties and part == "properties":
            # A "properties" field at a schema metadata path means we're entering
            # an object's properties. This means that a field named "properties"
            # is correctly treated as a schema metadata node.
            in_properties = True

        return NodePath(parts=(*self.parts, part), in_properties=in_properties)

    def has_prefix(self, other: "NodePath") -> bool:
        """The parts of this path start with the parts of the other path."""
        if len(self.parts) < len(other.parts):
            # If self is shorter than other, other can't be a prefix
            return False
        return all(this == that for this, that in zip(self.parts, other.parts))

    def __str__(self) -> str:
        """Use a `.` separator to represent the path as a single string."""
        return ".".join(self.parts)

    @staticmethod
    def from_str(path: str) -> "NodePath":
        return NodePath(tuple(path.split(".")))


class Node(UserDict):
    """Class that hold methods to work with a Node of the JSON Schema."""

    def __init__(self, schema: dict, path: NodePath = NodePath(parts=("root",))):
        super().__init__()
        self.data = schema
        self.path = path

    @property
    def name(self):
        return self.path.name()

    @property
    def properties_dict(self):
        """Getter for properties as dict."""
        ids = self.data
        if ids.get("type") == "object" and ids.get("properties") is not None:
            return ids.get("properties")
        if ids.get("type") == "array" and get(ids, "items.properties") is not None:
            return get(ids, "items.properties")
        return None

    @property
    def properties_list(self):
        """Getter for node's properties as a list."""
        prop_dict = self.properties_dict
        if prop_dict:
            return prop_dict.keys()
        return []

    @property
    def type_(self):
        """Getter for node's 'type' metadata field."""
        return self.data.get("type")

    @property
    def has_required_list(self):
        """
        Validate that the current node has the 'required' metadata field and is of type list.

        Returns:
            True if node had the 'required' field and is of type list; False otherwise.
        """
        required = self.get("required")
        required_exist = required and isinstance(required, list)
        return bool(required_exist)

    def required_contains_values(self, min_required_values: Iterable) -> bool:
        """
        Check that the current node's `required` metadata array contains a set of provided values.

        Args:
            min_required_values: Iterable containing the set of values expected to be in the node's `required` array.

        Returns:
            False is `required` does not contain passed in values; True otherwise.
        """
        if self.has_required_list:
            required = set(self.get("required"))
            min_required = set(min_required_values)
            return False if min_required - required else True
        return False

    def has_properties(self, prop_list: list) -> bool:
        """
        Validate that the node's fields under the 'properties' metadata field contain a provided set of field names.

        Args:
            prop_list: List of field names to check

        Returns:
            True if all properties from the list exist
            False if any of provided properties do not exist.
        """
        properties = self.properties_list or []
        properties = set(properties)

        req_prop = set(prop_list)

        return False if req_prop - properties else True

    @property
    def missing_properties(self):
        required = set(self.get("required"))
        properties = self.get("properties", {}).keys()
        return required - properties

    @property
    def has_valid_type(self):
        if "const" in self.data:
            return self._check_const_type()
        if self.type_ == "object":
            return self._check_object_type()
        if self.type_ == "array":
            return self._check_array_type()
        if isinstance(self.type_, list):
            return self._check_list_type()
        if isinstance(self.type_, str):
            return self._check_unit_type()
        return True, None

    def _check_const_type(self):
        """If const is defined, then type must
        not be a list
        """
        valid_const_type = [
            "number",
            "string",
            "boolean",
            "integer",
        ]
        if self.type_ not in valid_const_type:
            return (
                False,
                f"'type' must be one of {valid_const_type} when 'const' is defined",
            )
        return True, None

    def _check_object_type(self):
        """Checks if `object` type contains properties

        Returns:
            tuple: A `tuple` with `boolean` that tells whether
            node a valid `object` type or not and a `string` message
            if its invalid `object` type
        """
        return (
            (True, None)
            if self.properties_list
            else (False, "'object' type must  contains non-empty 'properties'")
        )

    def _check_array_type(self):
        """Checks if node is valid `array` type that contains
        child `properties`

        Returns:
            tuple: A `tuple` with `boolean` that tells whether
            node a valid `array` type or not and a `string` message
            if its invalid `array` type
        """
        # Arrays inside datacubes measures and dimensions
        # doesn't need to have children. So, ignore them.
        ignored_paths = [
            "datacubes.items.properties.measures",
            "datacubes.items.properties.dimensions",
        ]

        if ignored_paths[0] in self.path.parts or ignored_paths[1] in self.path.parts:
            return (True, None)

        # Array must contain items: dict
        if "items" not in self:
            return (False, "'array' type must contain 'items: dict'")

        items = get(self, "items")

        if not isinstance(items, dict):
            return (False, "'array' type must contain 'items: dict'")

        # Array must contain items.type
        # if type is invalid, it will picked up by validator
        # when checking items node
        if "type" not in items:
            return (False, "'array' type must contain items.type")

        # All Good, it a valid array time
        return True, None

    def _check_list_type(self):
        valid_nullable_types = {"number", "string", "boolean", "integer", "null"}

        checks = [
            # Length of list type must 2.
            (0 < len(self.type_) <= 2),
            # list must not contain same value
            len(set(self.type_)) == len(self.type_),
            # List must only contain values from
            # valid_nullable types
            ((set(self.type_) - valid_nullable_types) == set()),
            # If list contains two data types
            # make sure one of them is null
            (("null" in self.type_) if len(self.type_) == 2 else True),
            # If list contains one datatypes
            # make sure its not null
            (("null" not in self.type_) if len(self.type_) == 1 else True),
        ]
        result = (True, None) if all(checks) else (False, None)
        return result

    def _check_unit_type(self):
        valid_types = {"number", "string", "boolean", "array", "object", "integer"}
        return (True, None) if self.type_ in valid_types else (False, None)

    def _is_numeric_type(self):
        if isinstance(self.type_, list):
            type_ = sorted(self.type_)
            if type_ not in [sorted(["null", "integer"]), sorted(["null", "number"])]:
                return False

        elif self.type_ not in ["number", "integer"]:
            return False

        return True
