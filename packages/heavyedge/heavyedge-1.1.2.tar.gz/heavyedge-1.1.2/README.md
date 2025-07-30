# HeavyEdge

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/heavyedge.svg)](https://pypi.python.org/pypi/heavyedge/)
[![PyPI Version](https://img.shields.io/pypi/v/heavyedge.svg)](https://pypi.python.org/pypi/heavyedge/)
[![License](https://img.shields.io/github/license/heavyedge/heavyedge)](https://github.com/heavyedge/heavyedge/blob/master/LICENSE)
[![CI](https://github.com/heavyedge/heavyedge/actions/workflows/ci.yml/badge.svg)](https://github.com/heavyedge/heavyedge/actions/workflows/ci.yml)
[![CD](https://github.com/heavyedge/heavyedge/actions/workflows/cd.yml/badge.svg)](https://github.com/heavyedge/heavyedge/actions/workflows/cd.yml)
[![Docs](https://readthedocs.org/projects/heavyedge/badge/?version=latest)](https://heavyedge.readthedocs.io/en/latest/?badge=latest)

![title](https://heavyedge.readthedocs.io/en/latest/_images/plot-header.png)

Basic package for heavy edge coating profile analysis.

Provides:

- Profile preprocessing and averaging.
- Landmark detection.
- File I/O and command line API.

## Documentation

The manual can be found online:

> https://heavyedge.readthedocs.io

If you want to build the document yourself, get the source code and install with `[doc]` dependency.
Then, go to `doc` directory and build the document:

```
$ pip install .[doc]
$ cd doc
$ make html
```

Document will be generated in `build/html` directory. Open `index.html` to see the central page.

## Developing

### Installation

For development features, you must install the package by `pip install -e .[dev]`.

### Testing

Run `pytest` command to perform unit test.

When doctest is run, buildable sample data are rebuilt by default.
To disable this, set `HEAVYEDGE_TEST_REBUILD` environment variable to zero.
For example,
```
HEAVYEDGE_TEST_REBUILD=0 pytest
```
