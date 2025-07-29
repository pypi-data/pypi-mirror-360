# Config Finder
Finds a configuration file (e.g. pyproject.toml) and returns some sub-configuration with only python standard libraries.


Supported formats:

* [TOML](https://en.wikipedia.org/wiki/TOML)
* [JSON](https://en.wikipedia.org/wiki/JSON)


## Use Case
When defining machine learning projects and handling the project configuration by e.g. a [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) (e.g. with [Astral UV](https://docs.astral.sh/uv/) or  [Poetry](https://python-poetry.org/)) you can utilize the configuration files to define and store important variables.

Instead of defining global variables in your code or using [dotenv](https://pypi.org/project/python-dotenv/), a configuration file such as the pyproject.toml can be used for those values.

[Link to Documentation](https://fabfabi.github.io/configfinder/)