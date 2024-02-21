import toml

import conda_envfile


def test_basic(tmp_path):
    contents_toml = """
[build-system]
requires = ["setuptools>=45", "setuptools_scm[toml]>=6.2"]

[project]
authors = [{name = "Tom de Geus", email = "tom@geus.me"}]
classifiers = ["License :: OSI Approved :: MIT License"]
dependencies = ["click >=1.0.0", "Jinja2"]
description = "Inspect/combine conda YAML environment files"
requires-python = ">=3.11"
readme = "README.md"
""".strip()

    contents_env = """
channels:
- conda-forge
dependencies:
- click
- jinja2 >=3.0.0
- python
""".strip()

    ftoml = tmp_path / "pyproject.toml"
    fenv = tmp_path / "environment.yml"

    ftoml.write_text(contents_toml)
    fenv.write_text(contents_env)

    conda_envfile.conda_envfile_pyproject([ftoml, fenv])

    data = toml.loads(ftoml.read_text())["project"]
    assert data["dependencies"] == ["click >=1.0.0", "Jinja2 >=3.0.0"]
    assert data["requires-python"] == ">=3.11"

    data = conda_envfile.parse_file(fenv)["dependencies"]
    assert data == ["click >=1.0.0", "jinja2 >=3.0.0", "python >=3.11"]
