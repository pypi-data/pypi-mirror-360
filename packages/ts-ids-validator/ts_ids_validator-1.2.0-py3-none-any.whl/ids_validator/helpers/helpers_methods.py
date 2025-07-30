"""Helper methods."""

from re import sub

from ids_validator.helpers.athena.constants import is_list_of_primitives_values
from ids_validator.helpers.athena.exceptions import MergeException
from ids_validator.helpers.config import global_config

SECRET_KEY_FILE = global_config.project_path / "secret.key"

latest_version = "3.3.0"
hm_min_version_required = "3.1.2"


def snake_case(string_to_convert):
    converted_string = sub("_+", "_", sub("[^A-Za-z0-9]+", "_", string_to_convert))
    return converted_string.lower()


def merge(dict_a, dict_b, path=None):
    """
    merge dict a into b
    can be used as reduce(merge, [dict1, dict2, dict3...]) to merge several into b
    https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries
    """
    try:
        if path is None:
            path = []
        for key in dict_b:
            if key in dict_a:
                if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                    merge(dict_a[key], dict_b[key], path + [str(key)])
                elif isinstance(dict_a[key], list) and isinstance(dict_b[key], list):
                    # We are not merging not primitive lists
                    if is_list_of_primitives_values(
                        dict_a[key]
                    ) and is_list_of_primitives_values(dict_b[key]):
                        dict_a[key] = list(set(dict_a[key] + dict_b[key]))
                elif dict_a[key] == dict_b[key]:
                    pass  # same leaf value
                else:
                    raise MergeException(
                        "Two or more schema paths would be normalized to the same Tetra SQL column name. Details: "
                        "Conflict in merge at %s" % ".".join(path + [str(key)]),
                        # Do not include the randomly generated `field_value` in error message
                        {k: v for k, v in dict_a.items() if k != "field_value"},
                        {k: v for k, v in dict_b.items() if k != "field_value"},
                    )
            else:
                dict_a[key] = dict_b[key]
    except MergeException as exp:
        raise exp
    return dict_a
