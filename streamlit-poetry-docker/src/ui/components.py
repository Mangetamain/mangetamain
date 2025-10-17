"""
Composants d'interface utilisateur pour l'application MangeTaMain
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List


class UIComponents:
    """Composants d'interface utilisateur"""

    @staticmethod
    def display_recipe_card(recipe: pd.Series, rank: int, user_ingredients: List[str]):
        """Affiche une carte de recette stylée"""

        with st.container():
            st.markdown(f"""
            <div class="recipe-card">
                <h3>🏆 #{rank} - {recipe['name']}</h3>
            </div>
            """, unsafe_allow_html=True)

            # Métriques en colonnes
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("🎯 Score Global", f"{recipe['score']:.3f}")

            with col2:
                st.metric("🥄 Jaccard", f"{recipe['jaccard']:.3f}")

            with col3:
                if pd.notnull(recipe.get('minutes')):
                    st.metric("⏱️ Temps", f"{recipe['minutes']} min")
                else:
                    st.metric("⏱️ Temps", "N/A")

            with col4:
                if pd.notnull(recipe.get('mean_rating_norm')):
                    st.metric("⭐ Rating", f"{recipe['mean_rating_norm']:.2f}")

            # Détails des ingrédients
            if 'normalized_ingredients' in recipe and isinstance(recipe['normalized_ingredients'], list):
                recipe_ingredients = recipe['normalized_ingredients']
                common_ingredients = set(user_ingredients) & set(recipe_ingredients)
                missing_ingredients = set(recipe_ingredients) - set(user_ingredients)

                if common_ingredients:
                    st.success(f"🤝 **Ingrédients que vous avez**: {', '.join(sorted(common_ingredients))}")

                if missing_ingredients:
                    missing_list = list(missing_ingredients)[:8]  # Limiter l'affichage
                    extra = f" + {len(missing_ingredients)-8} autres..." if len(missing_ingredients) > 8 else ""
                    st.info(f"🛒 **À acheter**: {', '.join(missing_list)}" + extra)

            # Description si disponible
            if pd.notnull(recipe.get('description')):
                with st.expander("📖 Description"):
                    desc = str(recipe['description'])
                    st.write(desc[:300] + "..." if len(desc) > 300 else desc)

    @staticmethod
    def display_main_header():
        """Affiche l'en-tête principal"""
        st.markdown("""
        <div class="main-header">
            <h1>🍽️ MangeTaMain - Recommandations Personnalisées</h1>
            <p>Trouvez les meilleures recettes avec vos ingrédients disponibles</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def display_sidebar_stats(recipes_df: pd.DataFrame, interactions_df: pd.DataFrame):
        """Affiche les statistiques dans la sidebar"""
        with st.sidebar:
            st.header("📊 Statistiques du Dataset")

            # Métriques du dataset
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🍽️ Recettes Disponibles", f"{len(recipes_df):,}")
            st.metric("👥 Interactions Utilisateurs", f"{len(interactions_df):,}")

            # Calculer quelques stats en temps réel
            if 'normalized_ingredients' in recipes_df.columns:
                has_ingredients = recipes_df['normalized_ingredients'].apply(
                    lambda x: isinstance(x, list) and len(x) > 0
                ).sum()
                st.metric("✅ Recettes avec Ingrédients", f"{has_ingredients:,}")

            st.metric("📈 Taux de Couverture", "100%")
            st.info(f"📅 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 🎯 Comment utiliser")
            st.markdown("""
            1. **Entrez vos ingrédients** disponibles
            2. **Sélectionnez le temps** de préparation max
            3. **Ajustez le nombre** de recommandations
            4. **Cliquez sur Recommander** 🚀
            """)

    @staticmethod
    def display_footer():
        """Affiche le footer de l'application"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem;">
            🍽️ <strong>MangeTaMain</strong> - Système de Recommandation de Recettes<br>
            Développé avec ❤️ en utilisant Streamlit et des données Food.com
        </div>
        """, unsafe_allow_html=True)