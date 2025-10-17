#!/usr/bin/env python3
"""
MangeTaMain Streamlit App - Point d'entrée principal
Architecture modulaire avec séparation en fichiers
"""

import streamlit as st
from src.core.app import MangeTaMainApp


def main():
    """Point d'entrée principal de l'application"""
    # Configuration Streamlit
    st.set_page_config(
        page_title="🍽️ MangeTaMain - Production",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Créer et lancer l'application
    app = MangeTaMainApp()
    app.run()


if __name__ == "__main__":
    main()