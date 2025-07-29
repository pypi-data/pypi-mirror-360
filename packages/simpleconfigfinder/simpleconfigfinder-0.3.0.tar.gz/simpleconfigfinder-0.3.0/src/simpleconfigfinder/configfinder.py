import collections.abc
import json
import tomllib
from pathlib import Path, PurePath
from typing import Any, Callable, Dict, Optional

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


def combine_dictionaries(dict_a, dict_b):
    """combine two dictionaries on a granular level. The entries of dict_a always have priority over entries of dict_b

    !!! important:
        this function modifies the original dicitionaries. If this matters, enter a deepcopy.
    """

    def check_instance(db):
        return isinstance(db, collections.abc.Mapping)

    # dict a not a dictionary -> dict_a over-writes dict_b
    if not check_instance(dict_a):
        return dict_a

    # dict a not a dictionary -> dict_a over-writes dict_b
    if not check_instance(dict_b):
        return dict_a

    # both are dictionaries -> recursively combine
    for k, v in dict_a.items():
        if check_instance(v):
            dict_b[k] = combine_dictionaries(v, dict_b.get(k, {}))
        else:
            dict_b[k] = v

    # add missing keys as they wil not be passed by the loop
    missing_keys = {k: v for k, v in dict_b.items() if k not in dict_a}
    dict_b.update(missing_keys)

    return dict_b


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
    config_fname: str | PurePath,
    sub_config_keys: Optional[list[str]] = None,
    raise_error=True,
    additional_readers: Optional[Dict[str, Callable[[Any], Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """goes upstream from the currently executed file and finds the file config_fname and returns the sub_config_keys

    Starts with the directory of the currently executed file (__main__.__file__) and searches upstream.

    Args:
        config_fname: The name of the configuration file as toml or json.
        sub_config_keys: A list of the keys to identify the sub-configuration. returns the full config if nothing is provided.
        raise_error: if errors will be raised in case any of the files are not found
        additional_readers: dictionary to define for file extensions which readers will be used (e.g. for yaml via  {"yaml": yaml.safe_load}). In general this works for any function that can take a file name as string or PurePath and return a dictionary.
    """

    # cut the leading dot
    extension = Path(config_fname).suffix[1:]

    reader_dictionary = {"toml": tomllib.load, "json": json.load}
    if additional_readers:
        reader_dictionary.update(additional_readers)

    if extension not in reader_dictionary:
        raise NotImplementedError(
            f"config finder not implmeneted for '{extension}'. Use any of '{reader_dictionary.keys()}'"
        )

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


def multi_config_finder(
    config_fname: list[str] | list[PurePath],
    sub_config_keys: Optional[list[str]] = None,
    raise_error=True,
    additional_readers: Optional[Dict[str, Callable[[Any], Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """goes upstream from the currently executed file and finds the file config_fname and returns the sub_config_keys

    Starts with the directory of the currently executed file (__main__.__file__) and searches upstream.

    In case there are multiple configuration files provided and keys are in multiple of them, the first occurence will be returned.
    This function first combines all files and afterwards applies the sub_config_keys

    Args:
        config_fname: List of configuration files. The output will be combined. In case of double definition, input from earlier mentioned files will not be over-written (but additional keys added).
        sub_config_keys: A list of the keys to identify the sub-configuration. returns the full config if nothing is provided.
        raise_error: if errors will be raised in case any of the files are not found
        additional_readers: dictionary to define for file extensions which readers will be used (e.g. for yaml via  {"yaml": yaml.safe_load}). In general this works for any function that can take a file name as string or PurePath and return a dictionary.
    """

    configs_all = [
        config_finder(
            config_fname=file,
            raise_error=raise_error,
            additional_readers=additional_readers,
        )
        for file in config_fname
    ]
    configuration = configs_all.pop()

    for cfg in configs_all:
        configuration = combine_dictionaries(configuration, cfg)

    if sub_config_keys is None:
        return configuration

    return config_walker(configuration, sub_config_keys)
