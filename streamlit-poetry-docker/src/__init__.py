"""
MangeTaMain - Système de recommandation de recettes
Architecture modulaire avec séparation en packages

Packages disponibles:
- core: Application principale
- managers: Gestion des ressources (données, etc.)
- engines: Moteurs de traitement (recommandations, etc.)
- ui: Composants interface utilisateur
- utils: Utilitaires et helpers

Exemple d'utilisation:
    from src.core.app import MangeTaMainApp
    from src.managers.data_manager import DataManager
    from src.engines.recommendation_engine import RecommendationEngine
"""

__version__ = "2.0.0"
__author__ = "MangeTaMain Team"
__all__ = [
    "core",
    "managers",
    "engines",
    "ui",
    "utils",
]