# Config Finder
Finds a configuration file (e.g. pyproject.toml) and returns some sub-configuration.

## Algorighm
1) starts from the currently executed file (__main__.__file__)
2) Checks if that folder contains the desired configuration file
3) Goes to the parent directory and repeats at 2
