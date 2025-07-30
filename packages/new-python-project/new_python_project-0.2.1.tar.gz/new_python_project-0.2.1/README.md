# Python project maker

https://github.com/rrthomas/new-python-project  
© Reuben Thomas <rrt@sc3d.org>  

This is a simple program which you can use to create a new Python project
from a built-in template. It uses the
[Nancy](https://github.com/rrthomas/nancy/) templating system.


## Installation

```
pip install new-python-project
```


## Creating a new project

Run `new-python-project DIRECTORY`. The program will prompt you for basic
information about the project, attempting to give sensible default values,
and then create the project in the given directory.

You can add the `--github` option to automatically create a GitHub project.

You can also store project information in a TOML file; see
[`sample.toml`](sample.toml) for a commented example.

See `new-python-project --help` for more information.

You can run your new program:

```
cd /path/to/new-project
make build
PYTHONPATH=. python -m project_name
```

The project is set up in a new git repository with a `pyproject.toml` and
Makefile to build, test and publish it, and basic command-line handling.


## Copyright and Disclaimer

new-python-project is copyright Reuben Thomas, and is free software,
licensed under the GNU Public License version 3, or, at your option, any
later version. See the file COPYING.
