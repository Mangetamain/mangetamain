#!/usr/bin/env python3
"""
MangeTaMain Streamlit App - Version Production Simplifiée
Sans dépendance aux métadonnées problématiques
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Configuration Streamlit
st.set_page_config(
    page_title="🍽️ MangeTaMain - Production", 
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS simple
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
}
.metric-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #4ecdc4;
}
.recipe-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
    border-left: 4px solid #ff6b6b;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def load_preprocessed_data():
    """
    Chargement automatique des données preprocessées - VERSION SIMPLIFIÉE
    """
    
    try:
        # Chemins des données preprocessées
        recipes_path = "/shared_data/recipes_processed.pkl"
        interactions_path = "/shared_data/interactions.pkl"
        
        # Vérifier que les données existent
        if not os.path.exists(recipes_path):
            st.error("❌ Données preprocessées non trouvées. Exécutez d'abord le preprocessing.")
            return None, None
        
        # Charger les données
        with st.spinner("⚡ Chargement des données preprocessées..."):
            recipes_df = pd.read_pickle(recipes_path)
            interactions_df = pd.read_pickle(interactions_path)
        
        st.success(f"✅ Données chargées: {len(recipes_df):,} recettes avec {len(interactions_df):,} interactions")
        
        return recipes_df, interactions_df
        
    except Exception as e:
        st.error(f"❌ Erreur de chargement: {e}")
        return None, None

@st.cache_data(ttl=1800, show_spinner=False)
def get_recommendations(recipes_df, interactions_df, user_ingredients, time_limit, n_recommendations):
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

def display_recipe_card(recipe, rank, user_ingredients):
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
                st.info(f"🛒 **À acheter**: {', '.join(missing_list)}" + 
                       (f" + {len(missing_ingredients)-8} autres..." if len(missing_ingredients) > 8 else ""))
        
        # Description si disponible
        if pd.notnull(recipe.get('description')):
            with st.expander("📖 Description"):
                desc = str(recipe['description'])
                st.write(desc[:300] + "..." if len(desc) > 300 else desc)

def main():
    """Interface principale de l'application"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🍽️ MangeTaMain - Recommandations Personnalisées</h1>
        <p>Trouvez les meilleures recettes avec vos ingrédients disponibles</p>
    </div>
    """, unsafe_allow_html=True)
    
    # === CHARGEMENT DES DONNÉES ===
    data_result = load_preprocessed_data()
    
    if data_result is None or data_result[0] is None:
        st.stop()
    
    recipes_df, interactions_df = data_result
    
    # === SIDEBAR - INFORMATIONS ===
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
    
    # === INTERFACE PRINCIPALE ===
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
    
    # === RECOMMANDATIONS ===
    if recommend_button and user_input.strip():
        
        # Parser les ingrédients
        user_ingredients = [ing.strip().lower() for ing in user_input.split(",") if ing.strip()]
        
        st.markdown("---")
        st.subheader(f"🎯 Recommandations pour: {', '.join(user_ingredients[:5])}" + 
                    (f" + {len(user_ingredients)-5} autres..." if len(user_ingredients) > 5 else ""))
        
        # Obtenir les recommandations
        with st.spinner("🔄 Génération des recommandations personnalisées..."):
            recommendations = get_recommendations(
                recipes_df, interactions_df, user_ingredients, time_limit, n_recommendations
            )
        
        if not recommendations.empty:
            
            # Statistiques rapides
            avg_jaccard = recommendations['jaccard'].mean()
            max_jaccard = recommendations['jaccard'].max()
            matches_count = (recommendations['jaccard'] > 0).sum()
            
            st.success(f"🎉 **{len(recommendations)} recommandations générées** | "
                      f"Correspondances moyennes: {avg_jaccard:.2f} | "
                      f"Recettes avec matches: {matches_count}/{len(recommendations)}")
            
            # Afficher les recommandations
            for i, (_, recipe) in enumerate(recommendations.iterrows(), 1):
                display_recipe_card(recipe, i, user_ingredients)
                
        else:
            st.warning("❌ Aucune recommandation trouvée avec ces critères")
            st.info("💡 Essayez avec des ingrédients plus communs ou supprimez la limite de temps")
    
    elif recommend_button and not user_input.strip():
        st.warning("⚠️ Veuillez entrer au moins un ingrédient")
    
    # === FOOTER ===
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        🍽️ <strong>MangeTaMain</strong> - Système de Recommandation de Recettes<br>
        Développé avec ❤️ en utilisant Streamlit et des données Food.com
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()