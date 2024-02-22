import tomllib

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

[project.scripts]
dependencies = "foo:bar"
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

    conda_envfile.conda_envfile_pyproject(["--pyproject", ftoml, fenv])

    data = tomllib.loads(ftoml.read_text())["project"]
    assert data["dependencies"] == ["click >=1.0.0", "Jinja2 >=3.0.0"]
    assert data["requires-python"] == ">=3.11"

    data = conda_envfile.parse_file(fenv)["dependencies"]
    assert data == ["click >=1.0.0", "jinja2 >=3.0.0", "python >=3.11"]


def test_basic_python(tmp_path):
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
- python >=3.12
""".strip()

    ftoml = tmp_path / "pyproject.toml"
    fenv = tmp_path / "environment.yml"

    ftoml.write_text(contents_toml)
    fenv.write_text(contents_env)

    conda_envfile.conda_envfile_pyproject(["--pyproject", ftoml, fenv])

    data = tomllib.loads(ftoml.read_text())["project"]
    assert data["dependencies"] == ["click >=1.0.0", "Jinja2 >=3.0.0"]
    assert data["requires-python"] == ">=3.12"

    data = conda_envfile.parse_file(fenv)["dependencies"]
    assert data == ["click >=1.0.0", "jinja2 >=3.0.0", "python >=3.12"]


def test_from_pyproject(tmp_path):
    contents_toml = """
[build-system]
requires = ["setuptools>=45", "setuptools_scm[toml]>=6.2"]

[project]
authors = [{name = "Tom de Geus", email = "tom@geus.me"}]
classifiers = ["License :: OSI Approved :: MIT License"]
dependencies = ["click >=1.0.0", "Jinja2 >=3.0.0"]
description = "Inspect/combine conda YAML environment files"
requires-python = ">=3.11"
readme = "README.md"
""".strip()

    contents_env = """
channels:
- conda-forge
dependencies:
- click
- python >=3.12
""".strip()

    ftoml = tmp_path / "pyproject.toml"
    fenv = tmp_path / "environment.yml"

    ftoml.write_text(contents_toml)
    fenv.write_text(contents_env)

    conda_envfile.conda_envfile_pyproject(["--pyproject", ftoml, fenv, "--from-pyproject"])

    data = tomllib.loads(ftoml.read_text())["project"]
    assert data["dependencies"] == ["click >=1.0.0", "Jinja2 >=3.0.0"]
    assert data["requires-python"] == ">=3.12"

    data = conda_envfile.parse_file(fenv)["dependencies"]
    data = sorted(list(map(str, data)))
    assert data == sorted(["click >=1.0.0", "jinja2 >=3.0.0", "python >=3.12"])


def test_from_environment(tmp_path):
    contents_toml = """
[build-system]
requires = ["setuptools>=45", "setuptools_scm[toml]>=6.2"]

[project]
authors = [{name = "Tom de Geus", email = "tom@geus.me"}]
classifiers = ["License :: OSI Approved :: MIT License"]
dependencies = ["Jinja2 >=3.0.0"]
description = "Inspect/combine conda YAML environment files"
requires-python = ">=3.11"
readme = "README.md"
""".strip()

    contents_env = """
channels:
- conda-forge
dependencies:
- click >=1.0.0
- python >=3.12
- jinja2 >=1.0.0
""".strip()

    ftoml = tmp_path / "pyproject.toml"
    fenv = tmp_path / "environment.yml"

    ftoml.write_text(contents_toml)
    fenv.write_text(contents_env)

    conda_envfile.conda_envfile_pyproject(["--pyproject", ftoml, fenv, "--from-environment"])

    data = tomllib.loads(ftoml.read_text())["project"]
    assert sorted(data["dependencies"]) == sorted(["click >=1.0.0", "Jinja2 >=3.0.0"])
    assert data["requires-python"] == ">=3.12"

    data = conda_envfile.parse_file(fenv)["dependencies"]
    data = sorted(list(map(str, data)))
    assert data == sorted(["click >=1.0.0", "jinja2 >=3.0.0", "python >=3.12"])
