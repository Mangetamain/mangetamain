"""
Package core: Classes principales de l'application MangeTaMain

Ce package contient l'orchestrateur principal (MangeTaMainApp) qui coordonne
tous les autres composants (managers, engines, ui).

Classes principales:
    - MangeTaMainApp: Application principale qui gère le flux de l'app
"""

from .app import MangeTaMainApp

__all__ = ["MangeTaMainApp"]