import json
import tomllib
from pathlib import Path, PurePath
from typing import Any, Dict, Iterable, Optional

import __main__


class ConfigNotFound(Exception):
    """will be raised when the given keys for the sub-configuration do not exist in the configuration file"""

    pass


def find_file(config_fname: str | PurePath) -> PurePath:
    """finds the configuration file by checking every parent directory.

    Starts with the directory of the currently executed file (__main__.__file__) and searches upstream.

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
    config_fname: str | PurePath | Iterable[str] | Iterable[PurePath],
    sub_config_keys: Optional[list[str]] = None,
    raise_error=True,
) -> Dict[str, Any]:
    """goes upstream from the currently executed file and finds the file config_fname and returns the sub_config_keys

    In case there are multiple configuration files provided and keys are in multiple of them, the last occurence will be returned.
    The function is first executed and afterwards the results are combined

    Starts with the directory of the currently executed file (__main__.__file__) and searches upstream.

    Args:
        config_fname: The name of the configuration file as toml or json. Multiple files can be provided. They will be combined
        sub_config_keys: A list of the keys to identify the sub-configuration. returns the full config if nothing is provided.
        raise_error: if errors will be raised in case any of the files are not found"""

    # iteratively call the function for all individual entries
    if type(config_fname) is list:
        configuration = {}
        [
            configuration.update(
                config_finder(
                    name, sub_config_keys=sub_config_keys, raise_error=raise_error
                )
            )
            for name in config_fname
        ]
        return configuration

    # this path will only happen for single entries
    extension = Path(config_fname).suffix  # type: ignore since list values are handled above

    reader_dictionary = {".toml": tomllib.load, ".json": json.load}

    if extension not in reader_dictionary:
        raise NotImplementedError(f"config finder not implmeneted for '{extension}'")

    reader = reader_dictionary[extension]

    try:
        fname = find_file(config_fname)  # type: ignore since list values are handled above
    except FileNotFoundError as err:
        if raise_error:
            raise err
        else:
            return {}

    with open(fname, "rb") as file:
        configuration = reader(file)

    if sub_config_keys is None:
        return configuration

    return config_walker(configuration, sub_config_keys)
