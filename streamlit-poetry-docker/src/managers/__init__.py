"""
Package managers: Gestionnaires de ressources

Ce package contient les classes responsables de la gestion des données
et des ressources de l'application.

Classes principales:
    - DataManager: Gestion du chargement et du cache des données preprocessées
"""

from .data_manager import DataManager

__all__ = ["DataManager"]