"""
Package engines: Moteurs de traitement

Ce package contient les moteurs qui effectuent les tâches métier principales
comme la génération des recommandations.

Classes principales:
    - RecommendationEngine: Moteur de recommandations avec cache Streamlit
"""

from .recommendation_engine import RecommendationEngine

__all__ = ["RecommendationEngine"]