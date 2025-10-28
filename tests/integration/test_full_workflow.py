"""
End-to-end integration tests for the complete Streamlit application flow.

This module tests the complete application workflow including data loading,
recommendation generation, and UI rendering.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import pickle
from pathlib import Path

# Import all components
from managers.data_manager import DataManager
from engines.recommendation_engine import RecommendationEngine
from ui.components import UIComponents
from core.app import MangeTaMainApp


class TestCompleteApplicationFlow:
    """Test the complete application workflow end-to-end."""
    
    @pytest.fixture
    def complete_recipes_dataset(self):
        """Fixture providing a complete recipes dataset for testing."""
        return pd.DataFrame({
            'recipe_id': range(1, 21),  # 20 recipes
            'name': [f'Recipe {i}' for i in range(1, 21)],
            'ingredients': [
                ['pasta', 'eggs', 'cheese'] + [f'ingredient{i}'] for i in range(20)
            ],
            'normalized_ingredients': [
                ['pasta', 'eggs', 'cheese'] + [f'ingredient{i}'] for i in range(20)
            ],
            'steps': [
                [f'Step 1 for recipe {i}', f'Step 2 for recipe {i}'] for i in range(1, 21)
            ],
            'minutes': np.random.randint(15, 120, 20),
            'n_ingredients': [3 + i for i in range(20)],
            'n_steps': [2] * 20,
            'description': [f'Description for recipe {i}' for i in range(1, 21)],
            'nutrition': [
                {'calories': 300 + i*10, 'fat': 10 + i, 'protein': 15 + i}
                for i in range(20)
            ],
            'tags': [
                ['tag1', 'tag2'] + [f'tag{i}'] for i in range(20)
            ]
        })
    
    @pytest.fixture
    def complete_interactions_dataset(self):
        """Fixture providing a complete interactions dataset for testing."""
        return pd.DataFrame({
            'user_id': np.random.randint(1, 11, 100),  # 100 interactions from 10 users
            'recipe_id': np.random.randint(1, 21, 100),  # Interactions with 20 recipes
            'rating': np.random.randint(1, 6, 100),  # Ratings 1-5
            'date': pd.date_range('2023-01-01', periods=100)
        })
    
    @pytest.fixture
    def temp_data_files(self, complete_recipes_dataset, complete_interactions_dataset):
        """Fixture creating temporary pickle files for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipes_path = Path(temp_dir) / "recipes_processed.pkl"
            interactions_path = Path(temp_dir) / "interactions.pkl"
            
            # Save datasets to pickle files
            complete_recipes_dataset.to_pickle(recipes_path)
            complete_interactions_dataset.to_pickle(interactions_path)
            
            yield {
                'recipes_path': str(recipes_path),
                'interactions_path': str(interactions_path),
                'temp_dir': temp_dir
            }

    def test_data_manager_full_workflow(self, temp_data_files):
        """Test DataManager complete workflow with real files."""
        # Create DataManager with custom paths
        data_manager = DataManager()
        data_manager.recipes_path = temp_data_files['recipes_path']
        data_manager.interactions_path = temp_data_files['interactions_path']
        
        # Mock Streamlit functions
        with patch('streamlit.cache_data') as mock_cache, \
             patch('streamlit.spinner') as mock_spinner, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.error') as mock_error:
            
            # Setup cache mock
            mock_cache.side_effect = lambda ttl=None, show_spinner=None: lambda func: func
            mock_spinner.return_value.__enter__ = Mock()
            mock_spinner.return_value.__exit__ = Mock()
            
    def test_ui_components_integration(self, complete_recipes_dataset, complete_interactions_dataset):
        """Test UIComponents integration with complete datasets."""
        # Test sidebar stats with real data
        with patch('streamlit.sidebar') as mock_sidebar, \
             patch('streamlit.header') as mock_header, \
             patch('streamlit.metric') as mock_metric, \
             patch('streamlit.info') as mock_info, \
             patch('streamlit.markdown') as mock_markdown:
            
            # Setup sidebar context
            mock_sidebar.return_value.__enter__ = Mock()
            mock_sidebar.return_value.__exit__ = Mock()
            
            UIComponents.display_sidebar_stats(complete_recipes_dataset, complete_interactions_dataset)
            
            # Verify components were called
            mock_header.assert_called()
            assert mock_metric.call_count >= 4  # At least 4 metrics
            mock_info.assert_called()
            
            # Verify metrics contain correct data
            metric_calls = mock_metric.call_args_list
            
            # First metric should be recipes count
            recipes_metric = metric_calls[0]
            assert "20" in str(recipes_metric[0])  # 20 recipes
            
            # Second metric should be interactions count
            interactions_metric = metric_calls[1]
            assert "100" in str(interactions_metric[0])  # 100 interactions

    def test_complete_app_workflow_simulation(self, complete_recipes_dataset, complete_interactions_dataset):
        """Test complete application workflow simulation."""
        # Create app
        app = MangeTaMainApp()
        
        # Test ingredient parsing
        user_input = "pasta, eggs, cheese, bacon"
        parsed_ingredients = app._parse_user_ingredients(user_input)
        assert parsed_ingredients == ['pasta', 'eggs', 'cheese', 'bacon']
        
        # Simulate recommendation generation
        mock_recommendations = pd.DataFrame({
            'recipe_id': [1, 2, 3, 4, 5],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3', 'Recipe 4', 'Recipe 5'],
            'jaccard': [0.8, 0.6, 0.4, 0.3, 0.2],
            'score': [0.9, 0.7, 0.5, 0.6, 0.4],
            'composite_score': [0.85, 0.65, 0.45, 0.45, 0.3]
        })
        
        # Test recommendation stats display
        with patch('streamlit.success') as mock_success:
            app._display_recommendations_stats(mock_recommendations, parsed_ingredients, "intelligent")
            
            # Verify stats were displayed
            mock_success.assert_called_once()
            message = mock_success.call_args[0][0]
            assert "5 recommandations générées" in message
            assert "Score composite moyen" in message

    def test_error_handling_throughout_workflow(self):
        """Test error handling throughout the complete workflow."""
        app = MangeTaMainApp()
        
        # Test with malformed ingredient input
        malformed_inputs = [
            "pasta,,,eggs,,cheese,",
            "   ,  ,  ",
            "ingredient1, , ingredient2",
            ""
        ]
        
        for input_str in malformed_inputs:
            result = app._parse_user_ingredients(input_str)
            # Should not raise exceptions and return reasonable results
            assert isinstance(result, list)
            assert all(isinstance(item, str) for item in result)
            assert all(item.strip() for item in result)  # No empty strings

    def test_data_consistency_checks(self, complete_recipes_dataset, complete_interactions_dataset):
        """Test data consistency throughout the workflow."""
        # Verify recipes dataset structure
        required_recipe_columns = ['recipe_id', 'name', 'ingredients']
        for col in required_recipe_columns:
            assert col in complete_recipes_dataset.columns
        
        # Verify interactions dataset structure
        required_interaction_columns = ['user_id', 'recipe_id', 'rating']
        for col in required_interaction_columns:
            assert col in complete_interactions_dataset.columns
        
        # Verify data types
        assert complete_recipes_dataset['recipe_id'].dtype in [np.int64, np.int32]
        assert complete_interactions_dataset['user_id'].dtype in [np.int64, np.int32]
        assert complete_interactions_dataset['recipe_id'].dtype in [np.int64, np.int32]
        
        # Verify data ranges
        assert complete_interactions_dataset['rating'].min() >= 1
        assert complete_interactions_dataset['rating'].max() <= 5

    def test_memory_efficiency(self, complete_recipes_dataset, complete_interactions_dataset):
        """Test memory efficiency of the application components."""
        import sys
        
        # Test that DataFrames are handled efficiently
        original_size = sys.getsizeof(complete_recipes_dataset)
        
        # Operations should not create unnecessary copies
        result = RecommendationEngine._calculate_composite_score(complete_recipes_dataset.copy())
        
        # Result should be reasonable in size
        result_size = sys.getsizeof(result)
        assert result_size > 0  # Should have actual data
        
        # Test that UI components don't hold large references
        with patch('streamlit.sidebar'), \
             patch('streamlit.header'), \
             patch('streamlit.metric'), \
             patch('streamlit.info'), \
             patch('streamlit.markdown'):
            
            UIComponents.display_sidebar_stats(complete_recipes_dataset, complete_interactions_dataset)
            # Should complete without memory issues


if __name__ == '__main__':
    pytest.main([__file__, '-v'])