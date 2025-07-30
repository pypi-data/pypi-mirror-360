from typing import Any, Dict, List, Tuple, Union

from ids_validator.instance.exceptions import InvalidDatacube


def multidimensional_shape(value: Union[List, Tuple]) -> Tuple[int, ...]:
    """
    Return the shape of a multidimensional array, raising an error if it is ragged.

    For example, ``[[[0], [1]]]`` has a shape of ``(1, 2, 1)``: it is 3 layers of nested
    lists (3 elements in the output tuple), and each element of the tuple is the number
    of elements at that nesting level.

    A ragged list like ``[[1], [2, 2]]`` will raise a ``ValueError`` exception. This
    list contains lists of lengths 1 and 2 at the same level, meaning it is not a
    multi-dimensional array.
    """
    # Base case
    if not value or not isinstance(value, list):
        return (0,)

    # If the first item is a list, expect all items to be lists
    if isinstance(value[0], list):
        # Check there is only one unique shape of items in the list
        sub_shapes = {multidimensional_shape(x) for x in value}
        if len(sub_shapes) > 1:
            raise ValueError("Ragged list detected")
        return (len(value), *sub_shapes.pop())

    # If the first item is not a list, check none of the others are lists
    if any(isinstance(sub_value, list) for sub_value in value):
        raise ValueError("Ragged list detected")
    # If we reach here, all items are not lists
    return (len(value),)


def validate_datacubes_measure_dimension_match(datacubes: List[Dict[str, Any]]) -> None:
    """Check that all datacubes are structurally valid.

    A datacube is structurally valid if all its measures have a homogenous shape which
    matches the shape of the dimensions, or it meets one of the supported edge cases
    for Athena transformation:

    - All dimensions have length 0, and the measure does not contain any values
    - The dimensions contain values, and the measure shape is valid but does not
    contain any values

    If none of the above criteria are met, an `InvalidDatacube` exception is raised.
    """
    if not datacubes or len(datacubes) == 0:
        return

    for datacube_index, datacube in enumerate(datacubes):
        dimensions: List[Dict[str, Any]] = datacube.get("dimensions", [])

        dimension_shape = tuple(
            len(dimension.get("scale", [])) for dimension in dimensions
        )
        all_dimensions_empty = all(v == 0 for v in dimension_shape)

        for measure_index, measure in enumerate(datacube.get("measures", [])):
            try:
                measure_shape = multidimensional_shape(measure.get("value", []))
            except ValueError as exc:
                raise InvalidDatacube(
                    f"Mismatch found in datacube at index {datacube_index}, name: \"{datacube.get('name')}\","
                    f"measure at index {measure_index}, name: \"{measure.get('name')}\".\n"
                    f"The measure values are ragged instead of being an n-dimensional array: "
                    f"the values contain arrays of different lengths at the same dimension level."
                ) from exc

            # Supported edge case in Athena transformation:
            # If all dimensions are empty, the last dimension in the measure shape should be 0
            if (
                all_dimensions_empty
                and measure_shape[-1] == 0
                and len(measure_shape) <= len(dimension_shape)
            ):
                continue

            # Supported edge case in Athena transformation:
            # Empty measures are allowed
            if measure_shape[-1] == 0 and (
                len(measure_shape) == 1 or measure_shape[:-1] == dimension_shape[:-1]
            ):
                continue

            if measure_shape != dimension_shape:
                raise InvalidDatacube(
                    f"Mismatch found in datacube at index {datacube_index}, name: \"{datacube.get('name')}\","
                    f"measure at index {measure_index}, name: \"{measure.get('name')}\".\n"
                    + f"Measure shape:{measure_shape}, dimension shape:{dimension_shape}"
                )
