import os
import sys

# Configuration des chemins
project_root = os.path.abspath('../..')
src_path = os.path.join(project_root, 'src')

sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

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

# Mock des imports pour éviter les erreurs de dépendances
autodoc_mock_imports = [
    'streamlit',
    'pandas',
    'numpy',
    'plotly',
    'scikit-learn',
    'scipy',
]

# Ignorer les warnings pour les modules non trouvés
suppress_warnings = ['autodoc.import_object']
