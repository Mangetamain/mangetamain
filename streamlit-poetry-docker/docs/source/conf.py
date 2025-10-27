import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

project = 'MangeTaMain Streamlit'
copyright = '2025, MangeTaMain Team'
author = 'MangeTaMain Team'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
