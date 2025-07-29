import tomllib
from pathlib import Path, PurePath
from typing import Any, Dict, Optional

import __main__


class ConfigNotFound(Exception):
    """will be raised when the given keys for the sub-configuration do not exist in the configuration file"""

    pass


file_finder_logic = (
    """Starts with the directory of the currently executed file (__main__.__file__)"""
)


def find_file(config_fname: str | PurePath) -> PurePath:
    f"""finds the configuration file by checking every parent directory.

    {file_finder_logic}

    Args:
        config_fname: the name of the configuration file"""

    directory = Path(__main__.__file__).parent

    while directory.parent != directory:
        if (directory / config_fname).exists():
            return directory / config_fname

        # go one up
        directory = directory.parent

    raise FileNotFoundError(f"'{config_fname}' was not found")


def config_walker(
    configuration_dictionary: Dict[str, Any], sub_config_keys: list[str]
) -> Dict[str, Any]:
    """goes upstream from the currently executed file and finds the file config_fname and returns the sub_config_keys"""

    for i, key in enumerate(sub_config_keys):
        if key in configuration_dictionary:
            configuration_dictionary = configuration_dictionary[key]
        else:
            raise ConfigNotFound(f"configuration {sub_config_keys[: i + 1]} not found")

    return configuration_dictionary


def config_finder(
    config_fname: str | PurePath, sub_config_keys: Optional[list[str]] = None
) -> Dict[str, Any]:
    f"""goes upstream from the currently executed file and finds the file config_fname and returns the sub_config_keys


    {file_finder_logic}

    Args:
        config_fname: The name of the configuration file
        sub_config_keys: A list of the keys to identify the sub-configuration. returns the full config if nothing is provided."""

    extension = Path(config_fname).suffix

    if extension != ".toml":
        raise NotImplementedError(f"config finder not implmeneted for '{extension}'")

    fname = find_file(config_fname)

    with open(fname, "rb") as file:
        configuration = tomllib.load(file)

    if sub_config_keys is None:
        return configuration

    return config_walker(configuration, sub_config_keys)
