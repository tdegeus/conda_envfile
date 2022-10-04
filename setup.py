from pathlib import Path

from setuptools import find_packages
from setuptools import setup

project_name = "conda_merge_envfile"

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
    packages=find_packages(),
    use_scm_version={"write_to": f"{project_name}/_version.py"},
    setup_requires=["setuptools_scm"],
    install_requires=["click", "pyyaml"],
    entry_points={
        "console_scripts": [
            f"conda_merge_envfile = {project_name}:_conda_merge_envfile_cli",
        ]
    },
)
