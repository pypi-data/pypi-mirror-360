# uv-sort

[![PyPI version](https://badge.fury.io/py/uv-sort.svg)](https://badge.fury.io/py/uv-sort)

Sort uv's dependencies alphabetically.

The following sections are supported:

- `dependency-groups`
- `project.dependencies`
- `project.optional-dependencies`
- `tool.uv.dev-dependencies`
- `tool.uv.sources`

## Installation

```bash
pip install uv-sort
# or
uv add uv-sort
```

## Usage

```bash
# sort dependencies in pyproject.toml in the current working directory
$ uv-sort
# or you can specify the path
$ uv-sort /path/to/pyproject.toml
```

### Options

- `--check`: Check if dependencies are sorted and exit with a non-zero status code when they are not.
- `--dry-run`: Output the modified file to stdout without modifying the file.

## With [pre-commit](https://pre-commit.com/)

```yaml
repos:
  - repo: https://github.com/ninoseki/uv-sort
    rev: "" # Use the sha / tag you want to point at
    hooks:
      - id: uv-sort
```

## With [Lefthook](https://lefthook.dev/)

```yaml
pre-commit:
  commands:
    uv-sort:
      run: uv-sort {staged_files}
      glob: "pyproject.toml"
```
