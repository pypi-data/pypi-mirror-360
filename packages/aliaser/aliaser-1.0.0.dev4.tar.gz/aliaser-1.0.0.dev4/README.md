# aliaser
![Static Badge](https://img.shields.io/badge/Inspyre-Softworks-blue?style=for-the-badge&logo=poetry)
![RTD](https://app.readthedocs.org/projects/aliaser/badge/?version=latest&style=for-the-badge)

![GitHub Release](https://img.shields.io/github/v/release/tayjaybabee/aliaser?include_prereleases&cacheSeconds=10&style=for-the-badge)
![PyPI - Version](https://img.shields.io/pypi/v/aliaser?style=for-the-badge)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Ftayjaybabee%2Faliaser%2Frefs%2Fheads%2Fmaster%2Fpyproject.toml&style=for-the-badge)

![PyPI - Types](https://img.shields.io/pypi/types/aliaser?style=for-the-badge)



aliaser provides a tiny metaclass and mixin that let you expose call-perfect
method aliases without writing boilerplate forwarders.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Declaring aliases with `@alias`](#declaring-aliases-with-alias)
  - [Adding aliases at runtime](#adding-aliases-at-runtime)
  - [Avoiding the built-ins side effect](#avoiding-the-built-ins-side-effect)
- [Development](#development)
- [Supported Python versions](#supported-python-versions)
- [License](#license)

## Features

- `@alias` decorator to expose a method or property under multiple names.
- `Aliases` mixin for runtime helpers, backed by the `AliasMeta` metaclass.
- Property and method aliases share the original descriptor – no wrappers.
- `install()`/`uninstall()` helpers manage registration of `alias` on
  `builtins`. `install()` runs automatically on import for drop-in usage.

## Installation

Install from PyPI:

```bash
pip install aliaser
```

Or add it to a Poetry project:

```bash
poetry add aliaser
```

## Usage

### Declaring aliases with `@alias`

```python
from aliaser import Aliases, alias

class Greeter(Aliases):
    @alias('hi', 'sup')
    def hello(self):
        print("Hello!")

Greeter().hi()  # prints "Hello!"
```

### Adding aliases at runtime

```python
Greeter.add_alias('hello', 'howdy')
Greeter().howdy()  # also prints "Hello!"
```

### Avoiding the built-ins side effect

Importing the top-level package calls `aliaser.install()` which registers
`alias` on `builtins`. This modifies the global namespace. Call
`aliaser.uninstall()` to undo the side effect, or import `alias` from
`aliaser.decorator` and `Aliases` from `aliaser.mixin` directly instead of
importing `aliaser`.

## Development

Clone the repository and install dependencies with Poetry:

```bash
poetry install
```

After making changes you can build the wheel with `poetry build`. Feel free to
open issues or pull requests on GitHub to discuss improvements.

## Supported Python versions

This project requires Python 3.12 or newer.

## License

`aliaser` is distributed under the MIT License.
