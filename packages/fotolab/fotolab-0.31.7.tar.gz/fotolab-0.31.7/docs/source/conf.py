# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import datetime

import fotolab

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

years = ", ".join([str(y) for y in range(2024, datetime.now().year + 1)])
project = "fotolab"
copyright = f"{years} Kian-Meng Ang"
author = "Kian-Meng Ang"

# The full version, including alpha/beta/rc tags
release = fotolab.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    "logo": "logo.jpg",
    "description": "A console program to manipulates photos.",
    "github_user": "kianmeng",
    "github_repo": "fotolab",
    "github_banner": True,
    "github_button": True,
    "pre_bg": "#eee",
    "page_width": "1080px",
}
