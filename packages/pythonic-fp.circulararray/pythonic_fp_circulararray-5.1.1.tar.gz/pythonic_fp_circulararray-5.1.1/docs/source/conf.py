# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Pythonic FP - Circular Array'
copyright = '2023-2025, Geoffrey R. Scheller'
author = 'Geoffrey R. Scheller'
release = '5.1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/confalways_use_bars_unioniguration.html#general-configuration

extensions = [
    'sphinx_toolbox.more_autodoc',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns: list[str] = []

# -- Options for Sphinx
autoclass_content = 'both'

# -- Options for sphinx_autodoc_typehints
always_use_bars_union = True  # Not working
# simplify_optional_unions = False
# typehints_document_rtype_none = False
# typehints_use_signatures = True
# typehints_use_signatures_return = True

# -- Options for sphinx_toolbox.more_autodoc.typevars
all_typevars = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'piccolo_theme'
html_static_path = ['_static']
