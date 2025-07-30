# YOLO

Scripts to train and evaluate YOLOv8 models. Read the official documentation of this library at https://dla.pages.teklia.com/yolo/.

It is licensed under the [AGPL-v3 license](./LICENSE).

## Development

For development and tests purpose it may be useful to install the project as a editable package with pip.

* Use a virtualenv (e.g. with virtualenvwrapper `mkvirtualenv -a . yolo`)
* Install yolo as a package (e.g. `pip install -e .`)

### Linter

Code syntax is analyzed before submitting the code.\
To run the linter tools suite you may use pre-commit.
```shell
pip install pre-commit
pre-commit run -a
```

### Run tests

Tests are executed with `tox` using [pytest](https://pytest.org).
To install `tox`,
```shell
pip install tox
tox
```

To reload the test virtual environment you can use `tox -r`

Run a single test module: `tox -- <test_path>`
Run a single test: `tox -- <test_path>::<test_function>`

## Documentation

Add the `docs` extra when installing `teklia-yolo` through, to install the needed dependencies:
```sh
pip install .[docs]
```

Build the documentation using `mkdocs serve -v`. The documentation should be available as <http://localhost:8000>.

### Writing documentation

This documentation uses Sphinx and was generated using mkdocs and mkdocstrings.

### Linting

This documentation is subject to linting using doc8, integrated into pre-commit.

The linting rules that doc8 applies can be found on its documentation.
