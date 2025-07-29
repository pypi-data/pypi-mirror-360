"""This is a small package with utility functions to find and handle configuration files that are stored upstream from the code."""

from simpleconfigfinder.configfinder import (
    ConfigNotFound,
    combine_dictionaries,
    config_finder,
    config_walker,
    find_file,
    multi_config_finder,
)
