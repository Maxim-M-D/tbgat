# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

from sphinx.ext import apidoc

sys.path.insert(0, os.path.abspath("../"))


project = "Tbgat"
html_title = "Tbgat Documentation"
copyright = "2024, Alexander Marquard, Maxim Mironov"
author = "Alexander Marquard, Maxim Mironov"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

html_theme_options = {
    "logo": {
        "text": "TBGAT Documentation",
    }
}


# -- Options for autodoc -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc

autodoc_default_options = {
    "members": True,
    "autoclass_content": "both",
    "show-inheritance": True,
}


def run_apidoc(_):
    base_path = os.path.abspath(os.path.dirname(__file__))
    argv = [
        "-f",
        "-e",
        "-o",
        f"{base_path}/reference/source",
        f"{base_path}/../tbgat",
    ]

    apidoc.main(argv)


def setup(app):
    app.connect("builder-inited", run_apidoc)
