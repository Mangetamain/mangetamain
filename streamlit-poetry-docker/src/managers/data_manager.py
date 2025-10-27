"""
Gestionnaire des données pour l'application MangeTaMain
"""

import streamlit as st
import pandas as pd
import os
from typing import Optional, Tuple


class DataManager:
    """Gestionnaire des données de l'application"""

    def __init__(self):
        self.recipes_path = "/shared_data/recipes_processed.pkl"
        self.interactions_path = "/shared_data/interactions.pkl"

    @st.cache_data(ttl=3600, show_spinner=False)
    def load_preprocessed_data(_self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Chargement automatique des données preprocessées - VERSION SIMPLIFIÉE
        """
        try:
            # Vérifier que les données existent
            if not os.path.exists(_self.recipes_path):
                st.error("❌ Données preprocessées non trouvées. Exécutez d'abord le preprocessing.")
                return None, None

            # Charger les données
            with st.spinner("⚡ Chargement des données preprocessées..."):
                recipes_df = pd.read_pickle(_self.recipes_path)
                interactions_df = pd.read_pickle(_self.interactions_path)

            st.success(f"✅ Données chargées: {len(recipes_df):,} recettes avec {len(interactions_df):,} interactions")

            return recipes_df, interactions_df

        except Exception as e:
            st.error(f"❌ Erreur de chargement: {e}")
            return None, None
