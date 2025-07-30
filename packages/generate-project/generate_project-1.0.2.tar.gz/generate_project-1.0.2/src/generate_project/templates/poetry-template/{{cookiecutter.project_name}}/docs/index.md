# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Overview

This documentation covers the {{ cookiecutter.project_name }} library.

## Installation

```bash
pip install {{ cookiecutter.package_name }}
```

Or, if you use Poetry:

```bash
poetry add {{ cookiecutter.package_name }}
```

## Quick Start

```python
from {{ cookiecutter.package_name }} import Example

# Initialize
example = Example()

# Use the library
result = example.run()
print(result)
```

```{toctree}
:hidden:
:maxdepth: 2
:caption: Contents

Home <self>
Guides <guides/index>
API Reference <api/index>
```

```{toctree}
:hidden:
:maxdepth: 1
:caption: Useful Links

GitHub Repository <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}>
PyPI Package <https://pypi.org/project/{{ cookiecutter.package_name }}/>
Issue Tracker <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/issues>
