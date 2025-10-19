"""
Application principale MangeTaMain
"""

import streamlit as st
from typing import List

from ..managers.data_manager import DataManager
from ..engines.recommendation_engine import RecommendationEngine
from ..ui.components import UIComponents
from ..utils.styles import StyleManager


class MangeTaMainApp:
    """Application principale de MangeTaMain"""
    
    def __init__(self):
        """Initialise l'application avec ses composants"""
        self.data_manager = DataManager()
        self.recommendation_engine = RecommendationEngine()
        self.ui_components = UIComponents()
    
    def _parse_user_ingredients(self, user_input: str) -> List[str]:
        """Parse les ingrédients saisis par l'utilisateur"""
        return [ing.strip().lower() for ing in user_input.split(",") if ing.strip()]
    
    def _display_recommendations_stats(self, recommendations, user_ingredients, sort_mode="score"):
        """Affiche les statistiques des recommandations avec info sur le tri"""
        if not recommendations.empty:
            # Statistiques rapides
            avg_jaccard = recommendations['jaccard'].mean()
            max_jaccard = recommendations['jaccard'].max()
            matches_count = (recommendations['jaccard'] > 0).sum()
            
            # Statistiques cosine si disponibles
            cosine_info = ""
            if 'cosine' in recommendations.columns:
                avg_cosine = recommendations['cosine'].mean()
                max_cosine = recommendations['cosine'].max()
                cosine_info = f" | Cosine moyen: {avg_cosine:.3f}"
            
            # Info sur le score utilisé pour le tri
            sort_info = ""
            if sort_mode == "intelligent" and 'composite_score' in recommendations.columns:
                avg_composite = recommendations['composite_score'].mean()
                sort_info = f" | Score composite moyen: {avg_composite:.3f}"
            elif sort_mode == "jaccard":
                sort_info = f" | Tri par Jaccard (max: {max_jaccard:.3f})"
            elif sort_mode == "cosine" and 'cosine' in recommendations.columns:
                sort_info = f" | Tri par Cosine TF-IDF (max: {max_cosine:.3f})"
            elif sort_mode == "score":
                avg_score = recommendations['score'].mean()
                sort_info = f" | Tri par score global (moyen: {avg_score:.3f})"
            
            st.success(f"🎉 **{len(recommendations)} recommandations générées** | "
                      f"Jaccard moyen: {avg_jaccard:.3f}"
                      f"{cosine_info} | "
                      f"Recettes avec correspondances: {matches_count}/{len(recommendations)}"
                      f"{sort_info}")
            
            # Afficher les recommandations
            for i, (_, recipe) in enumerate(recommendations.iterrows(), 1):
                self.ui_components.display_recipe_card(recipe, i, user_ingredients)
        else:
            st.warning("❌ Aucune recommandation trouvée avec ces critères")
            st.info("💡 Essayez avec des ingrédients plus communs ou supprimez la limite de temps")
    
    def _handle_user_input_section(self):
        """Gère la section de saisie utilisateur et retourne les paramètres"""
        st.header("🥄 Vos Ingrédients Disponibles")
        
        # Zone de saisie des ingrédients
        col_input, col_time = st.columns([3, 1])
        
        with col_input:
            user_input = st.text_input(
                "Entrez vos ingrédients (séparés par des virgules):",
                placeholder="chicken, onion, garlic, tomato, basil, olive oil, salt, pepper",
                help="Tapez les ingrédients que vous avez dans votre frigo, séparés par des virgules"
            )
        
        with col_time:
            time_options = [None, 15, 30, 45, 60, 90, 120, 180]
            time_limit = st.selectbox(
                "⏱️ Temps max (min):",
                time_options,
                format_func=lambda x: "Illimité" if x is None else f"{x} min"
            )
        
        # Paramètres additionnels - Mode de tri avec plus d'espace
        col_sort, col_button = st.columns([2, 1])
        
        with col_sort:
            sort_mode = st.selectbox(
                "📊 Mode de tri:",
                options=["intelligent", "jaccard", "cosine", "score"],
                format_func=lambda x: {
                    "intelligent": "🎯 Intelligent (Jaccard + Cosine + Score)",
                    "jaccard": "🥄 Priorité Jaccard (correspondances exactes)",
                    "cosine": "🧠 Priorité Cosine (similarité sémantique TF-IDF)",
                    "score": "⭐ Score global uniquement"
                }[x],
                index=0,
                help="Choisissez comment prioriser les recommandations"
            )
        
        with col_button:
            st.write("")  # Spacer
            recommend_button = st.button(
                "🔍 Obtenir les Recommandations", 
                type="primary",
                use_container_width=True
            )
        
        # Slider pour le nombre de recommandations
        n_recommendations = st.slider(
            "🏆 Nombre de recommandations:", 
            min_value=1, max_value=20, value=8,
            key="n_recs_slider"
        )
        
        # Section d'aide pour les algorithmes
        with st.expander("ℹ️ Comprendre les algorithmes de recommandation"):
            st.markdown("""
            **🧠 Système hybride Jaccard + Cosine similarity :**
            
            **🥄 Jaccard (Correspondances exactes) :**
            - Mesure l'intersection exacte entre vos ingrédients et ceux de la recette
            - Formule : `|Ingrédients communs| / |Tous les ingrédients uniques|`
            - Idéal pour : Utiliser exactement ce que vous avez
            
            **🧠 Cosine (Similarité sémantique TF-IDF) :**
            - Utilise la vectorisation TF-IDF pour capturer les relations sémantiques
            - Pondère les ingrédients rares (plus discriminants)
            - Idéal pour : Découvrir des recettes similaires même sans intersection exacte
            
            **🎯 Intelligent (Hybride) :**
            - Combine 40% Jaccard + 10% Cosine + 30% Rating + 20% Popularité
            - Équilibre optimal entre précision et découverte
            """)
        
        return user_input, time_limit, n_recommendations, recommend_button, sort_mode
    
    def _handle_recommendations(self, recipes_df, interactions_df, user_input, 
                              time_limit, n_recommendations, recommend_button, sort_mode):
        """Gère la logique des recommandations avec le mode de tri"""
        if recommend_button and user_input.strip():
            
            # Parser les ingrédients
            user_ingredients = self._parse_user_ingredients(user_input)
            
            st.markdown("---")
            
            # Afficher info sur le mode de tri
            sort_info = {
                "intelligent": "🎯 Tri intelligent hybride (Jaccard + Cosine + Score)",
                "jaccard": "🥄 Priorise les correspondances exactes (Jaccard)",
                "cosine": "🧠 Priorise la similarité sémantique (Cosine TF-IDF)",
                "score": "⭐ Tri par score global uniquement"
            }
            st.info(f"**Mode de tri :** {sort_info[sort_mode]}")
            
            st.subheader(f"🎯 Recommandations pour: {', '.join(user_ingredients[:5])}" + 
                        (f" + {len(user_ingredients)-5} autres..." if len(user_ingredients) > 5 else ""))
            
            # Déterminer les paramètres de tri
            if sort_mode == "intelligent":
                prioritize_jaccard = True
                custom_sort = False
            elif sort_mode == "jaccard":
                prioritize_jaccard = False  # On fera le tri nous-mêmes
                custom_sort = "jaccard"
            elif sort_mode == "cosine":
                prioritize_jaccard = False  # On fera le tri nous-mêmes
                custom_sort = "cosine"
            else:  # score
                prioritize_jaccard = False
                custom_sort = "score"
            
            # Obtenir les recommandations
            with st.spinner("🔄 Génération des recommandations personnalisées..."):
                recommendations = self.recommendation_engine.get_recommendations(
                    recipes_df, interactions_df, user_ingredients, time_limit, 
                    n_recommendations, prioritize_jaccard
                )
                
                # Appliquer tri personnalisé si nécessaire
                if custom_sort and not recommendations.empty:
                    if custom_sort == "jaccard":
                        recommendations = recommendations.sort_values('jaccard', ascending=False)
                    elif custom_sort == "cosine":
                        recommendations = recommendations.sort_values('cosine', ascending=False)
                    elif custom_sort == "score":
                        recommendations = recommendations.sort_values('score', ascending=False)
                    
                    # Garder seulement le nombre demandé
                    recommendations = recommendations.head(n_recommendations)
            
            # Afficher les résultats
            self._display_recommendations_stats(recommendations, user_ingredients, sort_mode)
            
        elif recommend_button and not user_input.strip():
            st.warning("⚠️ Veuillez entrer au moins un ingrédient")
    
    def run(self):
        """Lance l'application principale"""
        
        # Appliquer les styles
        StyleManager.apply_styles()
        
        # Header principal
        self.ui_components.display_main_header()
        
        # === CHARGEMENT DES DONNÉES ===
        data_result = self.data_manager.load_preprocessed_data()
        
        if data_result is None or data_result[0] is None:
            st.stop()
        
        recipes_df, interactions_df = data_result
        
        # === SIDEBAR - INFORMATIONS ===
        self.ui_components.display_sidebar_stats(recipes_df, interactions_df)
        
        # === INTERFACE PRINCIPALE ===
        user_input, time_limit, n_recommendations, recommend_button, sort_mode = self._handle_user_input_section()
        
        # === RECOMMANDATIONS ===
        self._handle_recommendations(
            recipes_df, interactions_df, user_input, 
            time_limit, n_recommendations, recommend_button, sort_mode
        )
        
        # === FOOTER ===
        self.ui_components.display_footer()