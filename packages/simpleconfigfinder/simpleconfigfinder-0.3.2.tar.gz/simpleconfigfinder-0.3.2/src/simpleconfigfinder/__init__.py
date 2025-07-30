"""This is a small package with utility functions to find and handle configuration files that are stored upstream from the code."""

from simpleconfigfinder.configfinder import (
    ConfigNotFound,
    combine_dictionaries,
    config_finder,
    config_walker,
    configparser_to_dict,
    find_file,
    multi_config_finder,
)
