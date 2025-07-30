import collections.abc
import configparser
import json
from configparser import ConfigParser
from pathlib import Path, PurePath
from typing import Any, Callable, Dict, Optional

import tomllib

import __main__


class ConfigNotFound(Exception):
    """will be raised when the given keys for the sub-configuration do not exist in the configuration file"""

    pass


def find_file(config_fname: str | PurePath) -> PurePath:
    """finds the configuration file by checking every parent directory.

    Starts with the directory of the currently executed file (`__main__.__file__`) and searches upstream.

    Args:
        config_fname: the name of the configuration file"""

    directory = Path(__main__.__file__).parent

    while directory.parent != directory:
        if (directory / config_fname).exists():
            return directory / config_fname

        # go one up
        directory = directory.parent

    raise FileNotFoundError(f"'{config_fname}' was not found")


def configparser_to_dict(configuration: configparser.ConfigParser) -> Dict[str, str]:
    """converts a configparser element (handling ini files) to a dictionary

    Example:

        >>> from configparser import ConfigParser
        >>> cfg = ConfigParser()
        >>> cfg.read_dict({ "a": {"a1": "1", "a2": "2"}})
        >>> configparser_to_dict(cfg)
        {'DEFAULT': {}, 'a': {'a1': '1', 'a2': '2'}}

    Args:
        configuration: configuration object loaded by the configparser

    Returns:
        dictionary of entries"""
    return {
        key: value
        if type(value) is not configparser.SectionProxy
        else {k: v for k, v in value.items()}
        for key, value in configuration.items()
    }


def combine_dictionaries(dict_a: Any, dict_b: Any) -> Any:
    """combine two dictionaries on a granular level. The entries of `dict_a` always have priority over entries of `dict_b`.

    !!! caution
        this function modifies the original dicitionaries. If this matters, use:

            from copy import deepcopy
            combine_dictionaries(dict_a, deepcopy(dict_b))

    Args:
        dict_a: Reference dictionary
        dict_b: Another dictionary from where the key will be added

    Returns:
        Combined dictionary of both dict_a and dict_b.   Values from dict_a have priority over dict_b.        If some values are dictionaries, they will be combined recursively.

    <!--note that the blank line behind Example needs to be there. There are two options.
    Either the examples are rendered properly (with integrated drop-down)
    Or the Doctests are rendered properly-->

    Examples:

        >>> combine_dictionaries({"a" : 1}, {"b" : 2})
        {'b': 2, 'a': 1}

        >>> combine_dictionaries({"a" : {"c" : 3}}, {"a" : {"c" : 4}})
        {'a': {'c': 3}}

        >>> combine_dictionaries({"a" : {"c" : 3}}, {"a" : {"e" : 5}})
        {'a': {'e': 5, 'c': 3}}

        >>> some_dictionary = {"a" : 1} # to show changes
        >>> combine_dictionaries({"b" : 2}, some_dictionary)
        {'a': 1, 'b': 2}
        >>> some_dictionary # ATTENTION: modified
        {'a': 1, 'b': 2}

        >>> from copy import deepcopy
        >>> some_dictionary = {"a" : 1}
        >>> combine_dictionaries({"b" : 2}, deepcopy(some_dictionary))
        {'a': 1, 'b': 2}
        >>> some_dictionary
        {'a': 1}
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
    """goes upstream from the currently executed file and finds the file `config_fname` and returns the `sub_config_keys`

    Args:
        configuration_dictionary: containing the configuration as dictionary of dictionaries
        sub_config_keys: defines the keys of the branches that are supposed to be returned

    Example:

        >>> config_walker({"a": {"b" : {"b1" : 1, "b2" : 2}}}, ["a", "b"])
        {'b1': 1, 'b2': 2}"""

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
    """goes upstream from the currently executed file and finds the file `config_fname` and returns the `sub_config_keys`

    Starts with the directory of the currently executed file (`__main__.__file__`) and searches upstream.

    Examples:

    When configurations to the pyproject.toml like

        [tool.some_tool.default_config]
        some_key = "some_value"

    Then you can get these values via

        >>> config_finder("pyproject.toml", ["tool", "some_tool", "default_config"])
        {'some_key': 'some_value'}

    Args:
        config_fname: The name of the configuration file as toml or json.
        sub_config_keys: A list of the keys to identify the sub-configuration. returns the full config if nothing is provided.
        raise_error: if errors will be raised in case any of the files are not found
        additional_readers: dictionary to define for file extensions which readers will be used (e.g. for yaml via  {"yaml": yaml.safe_load}). In general this works for any function that can take a file name as string or PurePath and return a dictionary. For a code example see [Other Readers](index.md#other-readers)

    Returns:
        "filtered" Dictionary, where teh sub_config_keys where already applied. I.e. config[sub_config_keys[0]][sub_config_keys[1]]...
    """

    # cut the leading dot
    extension = Path(config_fname).suffix[1:].lower()

    def ini_reader(file) -> Dict:
        """small unitility function to read ini files"""
        cfg = ConfigParser()
        cfg.read(file)
        return configparser_to_dict(cfg)

    reader_dictionary = {"toml": tomllib.load, "json": json.load, "ini": ini_reader}
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
    """goes upstream from the currently executed file and finds the file `config_fname` and returns the `sub_config_keys`

    Starts with the directory of the currently executed file (`__main__.__file__`) and searches upstream.

    In case there are multiple configuration files provided and keys are in multiple of them, the first occurence will be returned.
    This function first combines all files and afterwards applies the sub_config_keys

    Args:
        config_fname: List of configuration files. The output will be combined. In case of double definition, input from earlier mentioned files will not be over-written (but additional keys added).
        sub_config_keys: A list of the keys to identify the sub-configuration. returns the full config if nothing is provided.
        raise_error: if errors will be raised in case any of the files are not found
        additional_readers: dictionary to define for file extensions which readers will be used (e.g. for yaml via  {"yaml": yaml.safe_load}). In general this works for any function that can take a file name as string or PurePath and return a dictionary. For a code example see [Other Readers](index.md#other-readers)
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
