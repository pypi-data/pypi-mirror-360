# Prelude Parser

[![Tests Status](https://github.com/pbs-data-solutions/prelude-parser/actions/workflows/testing.yml/badge.svg?branch=main&event=push)](https://github.com/pbs-data-solutions/prelude-parser/actions?query=workflow%3ATesting+branch%3Amain+event%3Apush)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pbs-data-solutions/prelude-parser/main.svg)](https://results.pre-commit.ci/latest/github/pbs-data-solutions/prelude-parser/main)
[![Coverage](https://codecov.io/github/pbs-data-solutions/prelude-parser/coverage.svg?branch=main)](https://codecov.io/gh/pbs-data-solutions/prelude-parser)
[![PyPI version](https://badge.fury.io/py/prelude-parser.svg)](https://badge.fury.io/py/prelude-parser)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/prelude-parser?color=5cc141)](https://github.com/pbs-data-solutions/prelude-parser)

Parses XML files exported from [Prelude EDC](https://preludeedc.com/) into formats Python can use.

## Installation

```sh
pip install prelude-parser
```

Optionally the `pandas` extra can be installed to parse to a Pandas `DataFrame`

```sh
pip install prelude-parser[pandas]
```

Optionally the `polars` extra can be installed to parse to a Polars `DataFrame`

```sh
pip install prelude-parser[polars]
```

All extras can be install with

```sh
pip install prelude-parser[all]
```

## Usage

Parse a Prelude flat XML file to a Python dictionary.

```py
from prelude_parser import parse_to_dict
data = parse_to_dict("physical_examination.xml")
```

Parse a Prelude flat XML file into a list of Python class. The name of the class is taken from the
form name node in the XML file converted to pascal case. For example a <physical_examination> node
will result in a PhysicalExamination class being created.

```py
from prelude_parser import parse_to_classes
data = parse_to_classes("physical_examination.xml")
```

Parse a Prelude flat XML file into a Pandas DataFrame. This works for Prelude flat XML files that
were exported with the "write tables to seperate files" option. In order to use this option
`prelude-parser` either needs to be installed with the `pandas` extra or the `all` extras.

```py
from prelude_parser.pandas import to_dataframe
df = to_dataframe("physical_examination.xml")
```

Parse a Prelude flat XML file into a Polars DataFrame. This works for Prelude flat XML files that
were exported with the "write tables to seperate files" option. In order to use this option
`prelude-parser` either needs to be installed with the `polars` extra or the `all` extras.

```py
from prelude_parser.polars import to_dataframe
df = to_dataframe("physical_examination.xml")
```

## Contributing

Contributions to this project are welcome. If you are interesting in contributing please see our [contributing guide](CONTRIBUTING.md)
