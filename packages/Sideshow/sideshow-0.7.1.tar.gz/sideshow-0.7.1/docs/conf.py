# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version as get_version

project = 'Sideshow'
copyright = '2025, Lance Edgar'
author = 'Lance Edgar'
release = get_version('Sideshow')

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinxcontrib.programoutput',
    'enum_tools.autoenum',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    'pyramid': ('https://docs.pylonsproject.org/projects/pyramid/en/latest/', None),
    'python': ('https://docs.python.org/3/', None),
    'wuttjamaican': ('https://docs.wuttaproject.org/wuttjamaican/', None),
    'wuttaweb': ('https://docs.wuttaproject.org/wuttaweb/', None),
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
