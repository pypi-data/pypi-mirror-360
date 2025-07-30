# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PytCube'
copyright = '2025, Gwenaël CAËR'
author = 'Gwenaël CAËR'
release = '0.0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_design",
    "myst_nb",
    "sphinx.ext.autosummary",
]

myst_enable_extensions = ["colon_fence"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# nbsphinx configurations
# nbsphinx_execute = "never"

nb_execution_mode = "off"
nb_execution_excludepatterns = [
    'examples/*.ipynb',
    '_quick_overview.ipynb'
    ]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']
html_favicon = "_static/favicon.ico"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

# html_sidebars = {"getting-started": [], "contribute": [], "cite": []}

html_theme_options = {
    "logo": {
        "image_light": "_static/logo_pytcube_light.png",
        "image_dark": "_static/logo_pytcube_dark.png",
    },
    "header_links_before_dropdown": 4,
}