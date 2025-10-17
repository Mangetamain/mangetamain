"""
Moteur de recommandations pour l'application MangeTaMain
"""

import streamlit as st
import pandas as pd
import sys
from typing import List, Optional


class RecommendationEngine:
    """Moteur de recommandations"""

    @staticmethod
    @st.cache_data(ttl=1800, show_spinner=False)
    def get_recommendations(recipes_df: pd.DataFrame,
                            interactions_df: pd.DataFrame,
                            user_ingredients: List[str],
                            time_limit: Optional[int],
                            n_recommendations: int) -> pd.DataFrame:
        """
        Système de recommandation avec cache
        """
        try:
            # Import du système de scoring
            sys.path.append('/preprocessing')
            from reco_score import RecipeScorer

            # Créer le scorer et obtenir les recommandations
            scorer = RecipeScorer(alpha=0.5, beta=0.3, gamma=0.2)

            recommendations = scorer.recommend(
                recipes_df=recipes_df,
                interactions_df=interactions_df,
                user_ingredients=user_ingredients,
                time_limit=time_limit,
                top_n=n_recommendations
            )

            return recommendations

        except Exception as e:
            st.error(f"❌ Erreur recommandation: {e}")
            return pd.DataFrame()