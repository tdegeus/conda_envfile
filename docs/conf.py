import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "conda_envfile"
copyright = "2022, Tom de Geus"
author = "Tom de Geus"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
    "sphinxarg.ext",
    "sphinx.ext.autosectionlabel",
    "sphinx_mdinclude",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
