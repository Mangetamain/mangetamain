"""
Tests pour le module de configuration
"""

import pytest
from src.utils.config import (
    DATA_PATHS,
    CACHE_CONFIG,
    RECOMMENDATION_CONFIG,
    UI_CONFIG,
    MESSAGES
)


class TestConfig:
    """Tests de configuration"""

    def test_data_paths_structure(self):
        """Test de la structure des chemins de données"""
        assert isinstance(DATA_PATHS, dict)
        assert "recipes" in DATA_PATHS
        assert "interactions" in DATA_PATHS
        assert DATA_PATHS["recipes"] == "/shared_data/recipes_processed.pkl"
        assert DATA_PATHS["interactions"] == "/shared_data/interactions.pkl"

    def test_cache_config_structure(self):
        """Test de la configuration du cache"""
        assert isinstance(CACHE_CONFIG, dict)
        assert "data_ttl" in CACHE_CONFIG
        assert "recommendations_ttl" in CACHE_CONFIG
        assert CACHE_CONFIG["data_ttl"] == 3600
        assert CACHE_CONFIG["recommendations_ttl"] == 1800

    def test_recommendation_config_structure(self):
        """Test de la configuration des recommandations"""
        assert isinstance(RECOMMENDATION_CONFIG, dict)
        required_keys = [
            "alpha", "beta", "gamma", "max_ingredients_display",
            "jaccard_weight", "global_weight", "high_jaccard_threshold",
            "high_jaccard_bonus", "prioritize_jaccard"
        ]
        for key in required_keys:
            assert key in RECOMMENDATION_CONFIG

    def test_ui_config_structure(self):
        """Test de la configuration UI"""
        assert isinstance(UI_CONFIG, dict)
        assert "max_recommendations" in UI_CONFIG
        assert "default_recommendations" in UI_CONFIG
        assert "description_max_length" in UI_CONFIG
        assert "time_options" in UI_CONFIG
        assert isinstance(UI_CONFIG["time_options"], list)

    def test_messages_structure(self):
        """Test de la structure des messages"""
        assert isinstance(MESSAGES, dict)