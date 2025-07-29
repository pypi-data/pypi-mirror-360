"""Configuration file for the Sphinx documentation builder."""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(".."))

# Import the package to get version and other metadata
import ign

# -- Project information -----------------------------------------------------

project = "ign"
copyright = "2024, Eugene Kim"
author = "Eugene Kim"
version = ign.__version__
release = version

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = []

# -- Options for autodoc ----------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

autodoc_member_order = "bysource"
autodoc_typehints = "description"

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "github": ("https://pygithub.readthedocs.io/en/latest/", None),
}

# -- Options for todo extension ----------------------------------------------

todo_include_todos = True

# -- Options for Napoleon extension ------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True
