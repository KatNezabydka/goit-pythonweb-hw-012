# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os

sys.path.insert(0, os.path.abspath('../..'))


project = 'contacts'
copyright = '2025, Kateryna'
author = 'Kateryna'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "nature"
html_static_path = ["_static"]
