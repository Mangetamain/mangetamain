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
    def _calculate_composite_score(recommendations: pd.DataFrame) -> pd.DataFrame:
        """Calculate composite score combining similarity score and Jaccard index."""
        if recommendations.empty:
            return recommendations
            
        # Calculate normalized score (0-1)
        recommendations = recommendations.copy()
        
        # Handle missing score column
        if 'score' not in recommendations.columns:
            # If no score column, use jaccard if available, otherwise set to 0.5
            if 'jaccard' in recommendations.columns:
                recommendations['score'] = recommendations['jaccard']
            else:
                recommendations['score'] = 0.5
        
        score_min = recommendations['score'].min()
        score_max = recommendations['score'].max()
        score_range = score_max - score_min
        
        if score_range > 0:
            recommendations['normalized_score'] = (recommendations['score'] - score_min) / score_range
        else:
            recommendations['normalized_score'] = 1.0
        
        # Calculate Jaccard bonus if jaccard column exists
        jaccard_bonus = 0.0
        if 'jaccard' in recommendations.columns:
            high_jaccard_bonus = (recommendations['jaccard'] > 0.3).astype(float) * 0.1
            jaccard_weight = recommendations['jaccard'] * 0.3
            jaccard_bonus = high_jaccard_bonus + jaccard_weight
        
        # Calculate Cosine bonus if cosine column exists
        cosine_bonus = 0.0
        if 'cosine' in recommendations.columns:
            high_cosine_bonus = (recommendations['cosine'] > 0.3).astype(float) * 0.05
            cosine_weight = recommendations['cosine'] * 0.2
            cosine_bonus = high_cosine_bonus + cosine_weight
        
        # Composite score: 0.6 * normalized similarity + 0.25 * jaccard + 0.15 * cosine
        recommendations['composite_score'] = (
            0.6 * recommendations['normalized_score'] + 
            0.25 * jaccard_bonus +
            0.15 * cosine_bonus
        )
        
        return recommendations
    
    @staticmethod
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
            # 🆕 Paramètres optimisés pour système hybride Jaccard+Cosine
            scorer = RecipeScorer(
                alpha=0.4,  # Jaccard similarity  
                beta=0.3,   # Rating moyen
                gamma=0.2,  # Popularité
                delta=0.1   # Cosine similarity (TF-IDF)
            )

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
                    recommendations
                )
                
                # Trier par score composite et retourner le nombre demandé
                recommendations = recommendations.sort_values('composite_score', ascending=False).head(n_recommendations)
            
            return recommendations
            
        except Exception as e:
            st.error(f"❌ Erreur recommandation: {e}")
            return pd.DataFrame()