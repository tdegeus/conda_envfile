import pathlib

import conda_envfile


def test_condaforge_dependencies():
    basedir = pathlib.Path(__file__).parent
    with open(basedir / "condaforge_multioutput.yaml") as file:
        deps = list(map(str, conda_envfile.condaforge_dependencies(file.read())))

    assert deps == [
        "cmake",
        "cxx-compiler",
        "ninja",
        "numpy *",
        "pip",
        "pybind11",
        "python",
        "scikit-build",
        "setuptools_scm",
        "xtensor",
        "xtensor-python",
    ]

    with open(basedir / "condaforge.yaml") as file:
        deps = list(map(str, conda_envfile.condaforge_dependencies(file.read())))

    assert deps == [
        "arxiv",
        "bibtexparser",
        "click",
        "docopt",
        "gitpython",
        "numpy",
        "pip",
        "python >=3",
        "pyyaml",
        "requests",
        "setuptools_scm",
        "tqdm",
    ]
