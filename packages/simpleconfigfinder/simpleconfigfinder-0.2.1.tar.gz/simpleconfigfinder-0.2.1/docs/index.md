# Config Finder
Finds a configuration file (e.g. pyproject.toml) and returns some sub-configuration with only python standard libraries.


!!! note
    Supported formats:

    * [TOML](https://en.wikipedia.org/wiki/TOML)
    * [JSON](https://en.wikipedia.org/wiki/JSON)

## Algorighm

1. starts from the currently executed file (\_\_main\_\_.\_\_file\_\_)
2. Checks if that folder contains the desired configuration file
3. Goes to the parent directory and repeats at 2


## Use Case
When defining machine learning projects and handling the project configuration by e.g. a [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) (e.g. with [Astral UV](https://docs.astral.sh/uv/) or  [Poetry](https://python-poetry.org/)) you can utilize the configuration files to define and store important variables.

    [tool.some_tool]
    key1 = "some_value_1"
    key2 = "some_value_2"

    [tool.some_tool.default_config]
    important_key = "some_value"

    [tool.some_tool.special_config]
    important_key = "another_value"

!!! tip
    Instead of defining global variables in your code or using [dotenv](https://pypi.org/project/python-dotenv/), a configuration file such as the pyproject.toml can be used to store configurations.

Access works via

    ```python 
    find_configuration("pyproject.toml", ["tool", "some_tool", "default_config"])
    ```
    ```
    {"important_key" : "some_value"}    
    ```

This function can also be used to handle credentials.

!!! caution
    Do not write your credentials into the pyproject.toml and ensure that you do not check your credentials into the source control.