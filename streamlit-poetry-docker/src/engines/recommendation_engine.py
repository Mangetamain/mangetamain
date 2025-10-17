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
    def _calculate_composite_score(recommendations: pd.DataFrame, 
                                  jaccard_weight: float = 0.6, 
                                  global_weight: float = 0.4) -> pd.DataFrame:
        """
        Calcule un score composite prenant en compte à la fois le score global et l'indice Jaccard
        
        Args:
            recommendations: DataFrame des recommandations
            jaccard_weight: Poids de l'indice Jaccard (0.6 = 60% d'importance)
            global_weight: Poids du score global (0.4 = 40% d'importance)
        """
        if recommendations.empty:
            return recommendations
        
        # Normaliser les scores entre 0 et 1
        if 'jaccard' in recommendations.columns and recommendations['jaccard'].max() > 0:
            jaccard_normalized = recommendations['jaccard'] / recommendations['jaccard'].max()
        else:
            jaccard_normalized = 0
            
        if 'score' in recommendations.columns and recommendations['score'].max() > 0:
            global_normalized = recommendations['score'] / recommendations['score'].max()
        else:
            global_normalized = 0
        
        # Calculer le score composite
        recommendations['composite_score'] = (
            jaccard_weight * jaccard_normalized + 
            global_weight * global_normalized
        )
        
        # Ajouter un bonus pour les recettes avec un Jaccard élevé (>0.3)
        high_jaccard_bonus = (recommendations['jaccard'] > 0.3).astype(float) * 0.1
        recommendations['composite_score'] += high_jaccard_bonus
        
        return recommendations.sort_values('composite_score', ascending=False)
    
    @staticmethod
    @st.cache_data(ttl=1800, show_spinner=False)
    def get_recommendations(recipes_df: pd.DataFrame, 
                          interactions_df: pd.DataFrame, 
                          user_ingredients: List[str], 
                          time_limit: Optional[int], 
                          n_recommendations: int,
                          prioritize_jaccard: bool = True) -> pd.DataFrame:
        """
        Système de recommandation avec cache et tri intelligent
        
        Args:
            prioritize_jaccard: Si True, donne plus d'importance à l'indice Jaccard
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
                top_n=n_recommendations * 2  # Récupérer plus pour mieux trier
            )
            
            if not recommendations.empty and prioritize_jaccard:
                # Appliquer le tri composite intelligent
                recommendations = RecommendationEngine._calculate_composite_score(
                    recommendations, 
                    jaccard_weight=0.6,  # 60% pour Jaccard
                    global_weight=0.4    # 40% pour score global
                )
                
                # Retourner le nombre demandé
                recommendations = recommendations.head(n_recommendations)
            
            return recommendations
            
        except Exception as e:
            st.error(f"❌ Erreur recommandation: {e}")
            return pd.DataFrame()