# conda_envfile

Provides a Python library, command line tools, and pre-commit tools to manage conda environment files.

## Command line

From the command line:

```bash
conda_envfile_merge -a "extra-library" env1.yml env2.yml > env3.yml
```

merges `env1.yml` and `env2.yml` and adds the package `extra-library` to the merged environment file `env3.yml`.

## pre-commit

In your `.pre-commit-config.yaml`, add:

```yaml
- repo: https://github.com/tdegeus/conda_envfile
  rev: v0.1.0
  hooks:
  - id: conda_envfile_parse
    files: "environment.yaml"
```

to keep your `environment.yaml` file unique, sorted, and legal in terms of version limitations.

## Python

Combine different version restrictions. For example:

```python
import conda_envfile

conda_envfile.unique("foo >1.2.0", "foo =1.2.*")
```

which returns

```python
["foo >1.2.0, <1.3.0"]
```
