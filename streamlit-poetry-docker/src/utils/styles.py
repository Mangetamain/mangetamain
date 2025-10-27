"""
Gestionnaire des styles CSS pour l'application MangeTaMain
"""

import streamlit as st


class StyleManager:
    """Gestionnaire des styles CSS pour l'application"""

    @staticmethod
    def apply_styles():
        """Applique les styles CSS à l'application"""
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
