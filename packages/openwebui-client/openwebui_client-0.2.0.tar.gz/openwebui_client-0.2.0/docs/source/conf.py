# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
import datetime

# Add the project root directory to the path so autodoc can find the modules
sys.path.insert(0, os.path.abspath('../..'))

project = 'openwebui-client'
copyright = f'{datetime.datetime.now().year}, Marc Durepos'
author = 'Marc Durepos'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # Automatically generate API documentation
    'sphinx.ext.napoleon',  # Support for Google or NumPy style docstrings
    'sphinx.ext.viewcode',  # Add links to view the source code
    'sphinx.ext.intersphinx',  # Link to other projects' documentation
    'sphinx.ext.coverage',  # Check documentation coverage
    'sphinx.ext.autosummary',  # Generate summary tables for API docs
    'sphinx_autodoc_typehints',  # Better support for type annotations
    'sphinx_copybutton',  # Add a copy button to code blocks
    'myst_parser',  # Support for Markdown files
]

# Add mock imports to avoid import errors during documentation building
autodoc_mock_imports = ['openai']

# Configure MyST-Parser for markdown support
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True

# Setup intersphinx mapping to link to Python and OpenAI docs
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'openai': ('https://platform.openai.com/docs', None),
}

# Autosummary settings
autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'  # Use Read the Docs theme
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'style_external_links': True,
}

# HTML settings
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

# Add any paths that contain custom static files here
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
# Autodoc settings
autodoc_member_order = 'groupwise'  # Sort members by group (classes, functions, etc.)
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
