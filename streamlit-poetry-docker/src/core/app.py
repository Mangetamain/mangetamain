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

    def _display_recommendations_stats(self, recommendations, user_ingredients):
        """Affiche les statistiques des recommandations"""
        if not recommendations.empty:
            # Statistiques rapides
            avg_jaccard = recommendations['jaccard'].mean()
            matches_count = (recommendations['jaccard'] > 0).sum()

            st.success(f"🎉 **{len(recommendations)} recommandations générées** | "
                       f"Correspondances moyennes: {avg_jaccard:.2f} | "
                       f"Recettes avec matches: {matches_count}/{len(recommendations)}")

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

        # Paramètres additionnels
        col_recs, col_button = st.columns([1, 2])

        with col_recs:
            n_recommendations = st.slider(
                "🏆 Nombre de recommandations:",
                min_value=1, max_value=20, value=8
            )

        with col_button:
            st.write("")  # Spacer
            recommend_button = st.button(
                "🔍 Obtenir les Recommandations",
                type="primary",
                use_container_width=True
            )

        return user_input, time_limit, n_recommendations, recommend_button

    def _handle_recommendations(self, recipes_df, interactions_df, user_input,
                                time_limit, n_recommendations, recommend_button):
        """Gère la logique des recommandations"""
        if recommend_button and user_input.strip():

            # Parser les ingrédients
            user_ingredients = self._parse_user_ingredients(user_input)

            st.markdown("---")
            extra = f" + {len(user_ingredients)-5} autres..." if len(user_ingredients) > 5 else ""
            st.subheader(f"🎯 Recommandations pour: {', '.join(user_ingredients[:5])}" + extra)

            # Obtenir les recommandations
            with st.spinner("🔄 Génération des recommandations personnalisées..."):
                recommendations = self.recommendation_engine.get_recommendations(
                    recipes_df, interactions_df, user_ingredients, time_limit, n_recommendations
                )

            # Afficher les résultats
            self._display_recommendations_stats(recommendations, user_ingredients)

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
        user_input, time_limit, n_recommendations, recommend_button = self._handle_user_input_section()

        # === RECOMMANDATIONS ===
        self._handle_recommendations(
            recipes_df, interactions_df, user_input,
            time_limit, n_recommendations, recommend_button
        )

        # === FOOTER ===
        self.ui_components.display_footer()
