import pathlib
import unittest

import conda_envfile

basedir = pathlib.Path(__file__).parent


class Test(unittest.TestCase):
    """ """

    def test_condaforge_dependencies(self):

        with open(basedir / "condaforge_multioutput.yaml") as file:
            deps = list(map(str, conda_envfile.condaforge_dependencies(file.read())))

        self.assertEqual(
            deps,
            [
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
            ],
        )

        with open(basedir / "condaforge.yaml") as file:
            deps = list(map(str, conda_envfile.condaforge_dependencies(file.read())))

        self.assertEqual(
            deps,
            [
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
            ],
        )


if __name__ == "__main__":

    unittest.main(verbosity=2)
