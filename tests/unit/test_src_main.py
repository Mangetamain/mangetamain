"""
Tests simples pour le module src/main.py
"""

import pytest
from src import main


class TestSrcMainModule:
    """Tests pour le module src/main.py"""
    
    def test_version_exists(self):
        """Test que la version est définie"""
        assert hasattr(main, '__version__')
        assert main.__version__ == "2.0.0"
        assert isinstance(main.__version__, str)

    def test_all_exports_list(self):
        """Test que __all__ est correctement défini"""
        assert hasattr(main, '__all__')
        assert isinstance(main.__all__, list)
        assert len(main.__all__) > 0

    def test_expected_exports_in_all(self):
        """Test que tous les exports attendus sont dans __all__"""
        expected_exports = [
            'MangeTaMainApp',
            'DataManager', 
            'RecommendationEngine',
            'UIComponents',
            'StyleManager',
            'DATA_PATHS',
            'CACHE_CONFIG',
            'RECOMMENDATION_CONFIG',
            'UI_CONFIG',
            'MESSAGES'
        ]
        
        for export in expected_exports:
            assert export in main.__all__, f"Export '{export}' manquant dans __all__"

    def test_imports_available(self):
        """Test que les imports principaux sont disponibles"""
        # Test des classes principales
        assert hasattr(main, 'MangeTaMainApp')
        assert hasattr(main, 'DataManager')
        assert hasattr(main, 'RecommendationEngine')
        assert hasattr(main, 'UIComponents')
        assert hasattr(main, 'StyleManager')

    def test_config_imports_available(self):
        """Test que les configurations sont importées"""
        assert hasattr(main, 'DATA_PATHS')
        assert hasattr(main, 'CACHE_CONFIG')
        assert hasattr(main, 'RECOMMENDATION_CONFIG')
        assert hasattr(main, 'UI_CONFIG')
        assert hasattr(main, 'MESSAGES')
        
        # Test que ce sont des dictionnaires
        assert isinstance(main.DATA_PATHS, dict)
        assert isinstance(main.CACHE_CONFIG, dict)
        assert isinstance(main.RECOMMENDATION_CONFIG, dict)
        assert isinstance(main.UI_CONFIG, dict)
        assert isinstance(main.MESSAGES, dict)

    def test_all_exports_accessible(self):
        """Test que tous les exports dans __all__ sont accessibles"""
        for export_name in main.__all__:
            assert hasattr(main, export_name), f"Export '{export_name}' non accessible"
            # Vérifier que l'export n'est pas None
            export_value = getattr(main, export_name)
            assert export_value is not None, f"Export '{export_name}' est None"