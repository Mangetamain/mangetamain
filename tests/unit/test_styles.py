"""
Tests pour le gestionnaire de styles
"""

import pytest
from unittest.mock import patch, Mock
from src.utils.styles import StyleManager


class TestStyleManager:
    """Tests pour le gestionnaire de styles"""
    
    @patch('streamlit.markdown')
    def test_apply_styles(self, mock_markdown):
        """Test de l'application des styles"""
        StyleManager.apply_styles()
        
        # Vérifier que st.markdown a été appelé
        mock_markdown.assert_called_once()
        
        # Vérifier que le CSS a été passé
        call_args = mock_markdown.call_args
        assert call_args is not None
        css_content = call_args[0][0]
        assert "<style>" in css_content
        assert ".main-header" in css_content
        assert "unsafe_allow_html=True" in str(call_args)