"""
Package utils: Utilitaires et helpers

Ce package contient les classes et fonctions utilitaires
utilisées par les autres packages.

Classes principales:
    - StyleManager: Gestion centralisée des styles CSS
    - config: Configuration centralisée de l'application

Modules:
    - styles.py: Gestionnaire de styles CSS
    - config.py: Configuration de l'application
"""

from .styles import StyleManager

__all__ = ["StyleManager"]