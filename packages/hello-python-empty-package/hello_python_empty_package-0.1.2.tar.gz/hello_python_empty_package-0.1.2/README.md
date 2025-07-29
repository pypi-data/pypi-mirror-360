# Python empty package template

Ready to be published as a library so any project can install it with pip.

## Setup

```
python -m venv .venv

# for Windows Git Bash
source .venv/Scripts/activate
# or Windows PowerShell
.venv\Scripts\Activate.ps1
# or for Linux:
source .venv/bin/activate

# pip install --upgrade pip
pip install -r requirements.txt
```

Update requirements.txt while developing:

```
pip list --not-required --format=freeze > requirements.txt
```

## Run Tests

```
export PYTHONPATH=src/hello_python_empty_package
python -m unittest -v src/hello_python_empty_package/daominahmath_test.py
```

## Build Package

```
# for the first time if not installed
# pip install build

python -m build
# Output will be in the `dist` directory
```

## Publish Package

[Python Package Index (PyPI)](https://pypi.org/manage/account/token/):

- username: daominah
- email: tung.daothanhtung@gmail.com

The following command will require your API token,
the token can only be view right after you create it, create a new token if needed.
I store the token in [.pypi_api_token](.pypi_api_token), which is gitignored.

```
# for the first time if not installed
# pip install twine

twine upload dist/*
# Output is on:
# https://pypi.org/project/hello-python-empty-package

# the 2nd time you run the upload command,
# it will return error "File already exists" if
# you have not changed the version in pyproject.toml.
```
