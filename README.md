[![ci](https://github.com/tdegeus/conda_envfile/workflows/CI/badge.svg)](https://github.com/tdegeus/conda_envfile/actions)
[![Documentation Status](https://readthedocs.org/projects/conda_envfile/badge/?version=latest)](https://conda_envfile.readthedocs.io/en/latest/?badge=latest)
[![pre-commit](https://github.com/tdegeus/conda_envfile/workflows/pre-commit/badge.svg)](https://github.com/tdegeus/conda_envfile/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/conda_envfile.svg)](https://anaconda.org/conda-forge/conda_envfile)

**Documentation: [https://conda_envfile.readthedocs.io](conda_envfile.readthedocs.io)**

# conda_envfile

Provides a Python library, command line tools, and pre-commit tools to manage conda environment files.

## Command line

### conda_envfile_merge

Merge different environment files.
For example:

```bash
conda_envfile_merge -a "extra-library" env1.yml env2.yml > env3.yml
```

merges `env1.yml` and `env2.yml` and adds the package `extra-library` to the merged environment file `env3.yml`.

### conda_envfile_diff

Show the difference between two environment files.
For example:

```bash
conda_envfile_diff env1.yml env2.yml
```

## pre-commit

### conda_envfile_parse

Keep your `environment.yaml` file unique, sorted, and legal in terms of version limitations.
In your `.pre-commit-config.yaml`, add:

```yaml
- repo: https://github.com/tdegeus/conda_envfile
  rev: v0.5.0
  hooks:
  - id: conda_envfile_parse
    files: "environment.yaml"
```

### conda_envfile_pyproject

Keep your `pyproject.toml` and `environment.yaml` in sync.
In your `.pre-commit-config.yaml`, add:

```yaml
- repo: https://github.com/tdegeus/conda_envfile
  rev: v0.5.0
  hooks:
  - id: conda_envfile_pyproject
    files: "environment.yaml"
```

## Python

Combine different version restrictions. For example:

```python
import conda_envfile

list(map(str, conda_envfile.unique("foo >1.2.0", "foo =1.2.*")))
```

which returns

```python
["foo >1.2.0, <1.3.0"]
```
