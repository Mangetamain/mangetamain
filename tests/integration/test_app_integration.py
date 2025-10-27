"""
Integration tests for the main Streamlit application.

This module contains integration tests for the MangeTaMainApp class and
related application workflow tests.
"""

import unittest
import pytest
import pandas as pd
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
from typing import List

# Import the class under test
from src.core.app import MangeTaMainApp


class TestMangeTaMainApp(unittest.TestCase):
    """Integration tests for MangeTaMainApp class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = MangeTaMainApp()
        
        # Sample data for testing
        self.sample_recipes = pd.DataFrame({
            'recipe_id': [1, 2, 3, 4, 5],
            'name': ['Pasta Carbonara', 'Caesar Salad', 'Apple Pie', 'Chicken Stew', 'Vegetable Soup'],
            'ingredients': [
                ['pasta', 'eggs', 'cheese', 'bacon'],
                ['lettuce', 'chicken', 'parmesan', 'croutons'],
                ['apples', 'flour', 'sugar', 'butter'],
                ['chicken', 'carrots', 'onions', 'potatoes'],
                ['vegetables', 'broth', 'herbs']
            ],
            'minutes': [30, 15, 60, 45, 25]
        })
        
        self.sample_interactions = pd.DataFrame({
            'user_id': [1, 1, 2, 2, 3, 3, 4, 5],
            'recipe_id': [1, 2, 1, 3, 2, 4, 5, 1],
            'rating': [5, 4, 5, 3, 4, 5, 3, 4]
        })

    def test_app_initialization(self):
        """Test that the app initializes correctly with all components."""
        self.assertIsNotNone(self.app.data_manager)
        self.assertIsNotNone(self.app.recommendation_engine)
        self.assertIsNotNone(self.app.ui_components)

    def test_parse_user_ingredients_single_ingredient(self):
        """Test parsing single ingredient input."""
        result = self.app._parse_user_ingredients("pasta")
        self.assertEqual(result, ["pasta"])

    def test_parse_user_ingredients_multiple_ingredients(self):
        """Test parsing multiple ingredients input."""
        result = self.app._parse_user_ingredients("pasta, eggs, cheese")
        self.assertEqual(result, ["pasta", "eggs", "cheese"])

    def test_parse_user_ingredients_with_spaces_and_mixed_case(self):
        """Test parsing ingredients with extra spaces and mixed case."""
        result = self.app._parse_user_ingredients("  PASTA  , Eggs ,  cheese  ")
        self.assertEqual(result, ["pasta", "eggs", "cheese"])

    def test_parse_user_ingredients_empty_input(self):
        """Test parsing empty or whitespace-only input."""
        result = self.app._parse_user_ingredients("")
        self.assertEqual(result, [])
        
        result = self.app._parse_user_ingredients("   ")
        self.assertEqual(result, [])

    def test_parse_user_ingredients_with_empty_segments(self):
        """Test parsing input with empty segments between commas."""
        result = self.app._parse_user_ingredients("pasta,, eggs, ,cheese")
        self.assertEqual(result, ["pasta", "eggs", "cheese"])

    @patch('streamlit.success')
    def test_display_recommendations_stats_with_data(self, mock_success):
        """Test display of recommendation statistics with data."""
        # Create sample recommendations
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'jaccard': [0.8, 0.6, 0.4],
            'score': [0.9, 0.7, 0.5],
            'composite_score': [0.85, 0.65, 0.45]
        })
        
        user_ingredients = ['pasta', 'eggs']
        
        # Test with intelligent sort mode
        self.app._display_recommendations_stats(recommendations, user_ingredients, "intelligent")
        
        # Verify success message was called
        mock_success.assert_called_once()
        
        # Check that the message contains expected information
        call_args = mock_success.call_args[0][0]
        self.assertIn("3 recommandations générées", call_args)
        self.assertIn("Score composite moyen", call_args)

    def test_display_recommendations_stats_empty_dataframe(self):
        """Test display of stats with empty recommendations."""
        empty_recommendations = pd.DataFrame()
        
        # Should not raise an exception
        with patch('streamlit.success') as mock_success:
            self.app._display_recommendations_stats(empty_recommendations, [], "intelligent")
            # Success should not be called for empty recommendations
            mock_success.assert_not_called()


class TestMangeTaMainAppPytest:
    """Pytest-style tests for MangeTaMainApp class."""
    
    @pytest.fixture
    def app(self):
        """Fixture to create MangeTaMainApp instance."""
        return MangeTaMainApp()
    
    @pytest.fixture
    def sample_recommendations(self):
        """Fixture providing sample recommendations DataFrame."""
        return pd.DataFrame({
            'recipe_id': [1, 2, 3, 4],
            'name': ['Recipe A', 'Recipe B', 'Recipe C', 'Recipe D'],
            'jaccard': [0.9, 0.7, 0.5, 0.3],
            'score': [0.8, 0.9, 0.6, 0.7],
            'composite_score': [0.85, 0.8, 0.55, 0.5]
        })

    def test_app_component_initialization(self, app):
        """Test that all app components are properly initialized."""
        assert hasattr(app, 'data_manager')
        assert hasattr(app, 'recommendation_engine')
        assert hasattr(app, 'ui_components')
        
        # Components should not be None
        assert app.data_manager is not None
        assert app.recommendation_engine is not None
        assert app.ui_components is not None

    @pytest.mark.parametrize("input_string,expected_output", [
        ("pasta", ["pasta"]),
        ("pasta, eggs", ["pasta", "eggs"]),
        ("PASTA, EGGS, CHEESE", ["pasta", "eggs", "cheese"]),
        ("  pasta  ,  eggs  ", ["pasta", "eggs"]),
        ("pasta,eggs,cheese,bacon", ["pasta", "eggs", "cheese", "bacon"]),
        ("", []),
        ("   ", []),
        ("pasta,, eggs, ,cheese", ["pasta", "eggs", "cheese"]),
        ("Pasta, Eggs & Cheese", ["pasta", "eggs & cheese"]),  # Special characters preserved
    ])
    def test_parse_user_ingredients_variations(self, app, input_string, expected_output):
        """Test ingredient parsing with various input formats."""
        result = app._parse_user_ingredients(input_string)
        assert result == expected_output

    @patch('streamlit.success')
    def test_recommendations_stats_display_formats(self, mock_success, app, sample_recommendations):
        """Test different formats of recommendation statistics display."""
        user_ingredients = ['pasta', 'eggs']
        
        # Test different sort modes
        sort_modes = ["intelligent", "jaccard", "score"]
        
        for sort_mode in sort_modes:
            mock_success.reset_mock()
            app._display_recommendations_stats(sample_recommendations, user_ingredients, sort_mode)
            
            # Verify success was called
            assert mock_success.called
            
            # Get the message content
            message = mock_success.call_args[0][0]
            
            # Common elements should be present
            assert "4 recommandations générées" in message
            assert "Jaccard moyen" in message
            assert "Recettes avec correspondances" in message
            
            # Mode-specific elements
            if sort_mode == "intelligent":
                assert "Score composite moyen" in message
            elif sort_mode == "jaccard":
                assert "Tri par Jaccard" in message
            elif sort_mode == "score":
                assert "Tri par score global" in message

    def test_ingredient_parsing_unicode_and_special_chars(self, app):
        """Test ingredient parsing with Unicode and special characters."""
        # Test with Unicode characters
        unicode_input = "pâtes, œufs, fromage"
        result = app._parse_user_ingredients(unicode_input)
        assert result == ["pâtes", "œufs", "fromage"]
        
        # Test with numbers and special characters
        special_input = "ingredient-1, item_2, component.3"
        result = app._parse_user_ingredients(special_input)
        assert result == ["ingredient-1", "item_2", "component.3"]

    def test_very_long_ingredient_list(self, app):
        """Test parsing very long ingredient lists."""
        # Create a long list of ingredients
        long_list = ", ".join([f"ingredient{i}" for i in range(100)])
        result = app._parse_user_ingredients(long_list)
        
        assert len(result) == 100
        assert result[0] == "ingredient0"
        assert result[99] == "ingredient99"


class TestMangeTaMainAppIntegration:
    """Integration tests for the complete MangeTaMainApp workflow."""
    
    def test_app_with_mocked_components(self):
        """Test app workflow with mocked components."""
        # Create app instance
        app = MangeTaMainApp()
        
        # Mock the components
        app.data_manager = Mock()
        app.recommendation_engine = Mock()
        app.ui_components = Mock()
        
        # Test that components can be accessed
        assert app.data_manager is not None
        assert app.recommendation_engine is not None
        assert app.ui_components is not None

    def test_app_resilience_to_malformed_data(self):
        """Test app behavior with malformed or edge case data."""
        app = MangeTaMainApp()
        
        # Test with malformed recommendations DataFrame
        malformed_recs = pd.DataFrame({
            'recipe_id': [1, 2],
            'name': ['Recipe 1', None],  # None value
            'jaccard': [0.5, float('nan')],  # NaN value
            'score': [0.7, 0.8]
        })
        
        with patch('streamlit.success'):
            # Should handle malformed data gracefully
            app._display_recommendations_stats(malformed_recs, [], "intelligent")

    @patch('src.core.app.DataManager')
    @patch('src.core.app.RecommendationEngine')
    @patch('src.core.app.UIComponents')
    def test_component_instantiation(self, mock_ui, mock_engine, mock_data_manager):
        """Test that components are properly instantiated during app creation."""
        # Create app (this should instantiate components)
        app = MangeTaMainApp()
        
        # Verify that each component class was instantiated
        mock_data_manager.assert_called_once()
        mock_engine.assert_called_once()
        mock_ui.assert_called_once()


if __name__ == '__main__':
    # Run unittest tests
    unittest.main(verbosity=2)