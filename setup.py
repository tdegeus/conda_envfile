from pathlib import Path

from setuptools import find_packages
from setuptools import setup

project_name = "conda_envfile"

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name=project_name,
    license="MIT",
    author="Tom de Geus",
    author_email="tom@geus.me",
    description="Inspect/combine conda YAML environment files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="conda, YAML",
    url=f"https://github.com/tdegeus/{project_name:s}",
    packages=find_packages(exclude=["tests"]),
    use_scm_version={"write_to": f"{project_name}/_version.py"},
    setup_requires=["setuptools_scm"],
    install_requires=["click", "Jinja2", "packaging", "prettytable", "pyyaml"],
    entry_points={
        "console_scripts": [
            f"conda_envfile_merge = {project_name}:_conda_envfile_merge_cli",
            f"conda_envfile_parse = {project_name}:_conda_envfile_parse_cli",
            f"conda_envfile_restrict = {project_name}:_conda_envfile_restrict_cli",
            f"conda_envfile_diff = {project_name}:_conda_envfile_diff_cli",
        ]
    },
)
