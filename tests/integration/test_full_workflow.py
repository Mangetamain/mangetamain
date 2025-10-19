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
from src.managers.data_manager import DataManager
from src.engines.recommendation_engine import RecommendationEngine
from src.ui.components import UIComponents
from src.core.app import MangeTaMainApp


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
            
    def test_recommendation_engine_with_cosine_similarity(self, complete_recipes_dataset, complete_interactions_dataset):
        """Test RecommendationEngine with new cosine similarity features."""
        # Mock the external reco_score module
        with patch('sys.path.append'), \
             patch('streamlit.error') as mock_error:
            
            # Create mock RecipeScorer that returns data with cosine similarity
            mock_scorer = Mock()
            mock_recommendations = pd.DataFrame({
                'recipe_id': [1, 2, 3, 4, 5],
                'name': ['Pasta Carbonara', 'Caesar Salad', 'Apple Pie', 'Chicken Stew', 'Veggie Soup'],
                'jaccard': [0.8, 0.6, 0.4, 0.3, 0.2],
                'cosine': [0.9, 0.7, 0.5, 0.8, 0.3],  # Include cosine similarity
                'score': [0.85, 0.75, 0.65, 0.70, 0.55],
                'ingredients': [
                    ['pasta', 'eggs', 'cheese'],
                    ['lettuce', 'chicken', 'parmesan'],
                    ['apples', 'flour', 'sugar'],
                    ['chicken', 'carrots', 'onions'],
                    ['vegetables', 'broth', 'herbs']
                ]
            })
            mock_scorer.recommend.return_value = mock_recommendations
            
            # Mock the import of RecipeScorer
            with patch('builtins.__import__') as mock_import:
                def side_effect(name, *args, **kwargs):
                    if name == 'reco_score':
                        mock_module = Mock()
                        mock_module.RecipeScorer = Mock(return_value=mock_scorer)
                        return mock_module
                    return __import__(name, *args, **kwargs)
                
                mock_import.side_effect = side_effect
                
                # Test recommendations with new hybrid system
                recommendations = RecommendationEngine.get_recommendations(
                    recipes_df=complete_recipes_dataset,
                    interactions_df=complete_interactions_dataset,
                    user_ingredients=['pasta', 'eggs', 'cheese'],
                    time_limit=60,
                    n_recommendations=3,
                    prioritize_jaccard=True
                )
                
                # Verify basic functionality
                assert not recommendations.empty
                assert len(recommendations) <= 3
                assert 'composite_score' in recommendations.columns
                
                # Verify that RecipeScorer was called with correct hybrid parameters
                mock_scorer.recommend.assert_called_once()
                
                # Verify cosine similarity is included in results
                if 'cosine' in recommendations.columns:
                    assert recommendations['cosine'].notna().any()

    def test_hybrid_scoring_parameters(self, complete_recipes_dataset, complete_interactions_dataset):
        """Test that the new hybrid scoring parameters (alpha, beta, gamma, delta) are used correctly."""
        with patch('sys.path.append'), \
             patch('streamlit.error') as mock_error:
            
            # Create mock RecipeScorer to capture initialization parameters
            mock_scorer_class = Mock()
            mock_scorer_instance = Mock()
            mock_scorer_class.return_value = mock_scorer_instance
            mock_scorer_instance.recommend.return_value = pd.DataFrame({
                'recipe_id': [1, 2],
                'name': ['Test Recipe 1', 'Test Recipe 2'],
                'jaccard': [0.8, 0.6],
                'cosine': [0.7, 0.5],
                'score': [0.9, 0.7]
            })
            
            # Mock the import
            with patch('builtins.__import__') as mock_import:
                def side_effect(name, *args, **kwargs):
                    if name == 'reco_score':
                        mock_module = Mock()
                        mock_module.RecipeScorer = mock_scorer_class
                        return mock_module
                    return __import__(name, *args, **kwargs)
                
                mock_import.side_effect = side_effect
                
                # Call get_recommendations
                RecommendationEngine.get_recommendations(
                    recipes_df=complete_recipes_dataset,
                    interactions_df=complete_interactions_dataset,
                    user_ingredients=['pasta', 'eggs'],
                    time_limit=None,
                    n_recommendations=5
                )
                
                # Verify RecipeScorer was initialized with correct hybrid parameters
                mock_scorer_class.assert_called_once_with(
                    alpha=0.4,  # Jaccard similarity
                    beta=0.3,   # Rating moyen
                    gamma=0.2,  # Popularité
                    delta=0.1   # Cosine similarity (TF-IDF)
                )

    def test_recommendation_engine_integration(self, complete_recipes_dataset, complete_interactions_dataset):
        """Test RecommendationEngine integration with realistic data."""
        # Test composite score calculation
        sample_recommendations = pd.DataFrame({
            'recipe_id': [1, 2, 3, 4, 5],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3', 'Recipe 4', 'Recipe 5'],
            'jaccard': [0.9, 0.7, 0.5, 0.3, 0.1],
            'score': [0.6, 0.8, 0.9, 0.7, 0.5]
        })
        
        # Test composite scoring
        result = RecommendationEngine._calculate_composite_score(sample_recommendations)
        
        # Verify results
        assert 'composite_score' in result.columns
        assert len(result) == 5
        assert result['composite_score'].is_monotonic_decreasing
        
        # Verify high Jaccard bonus (recipes with jaccard > 0.3 should get bonus)
        high_jaccard_recipes = result[result['jaccard'] > 0.3]
        assert len(high_jaccard_recipes) == 4  # First 4 recipes

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

    def test_recipe_card_with_complete_data(self):
        """Test recipe card display with complete recipe data."""
        # Create a complete recipe
        complete_recipe = pd.Series({
            'recipe_id': 1,
            'name': 'Complete Test Recipe',
            'score': 0.892,
            'jaccard': 0.756,
            'minutes': 35,
            'mean_rating_norm': 4.3,
            'normalized_ingredients': ['pasta', 'eggs', 'cheese', 'bacon', 'pepper'],
            'description': 'A complete test recipe with all fields populated for comprehensive testing.'
        })
        
        user_ingredients = ['pasta', 'eggs', 'cheese']
        
        with patch('streamlit.container') as mock_container, \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.metric') as mock_metric, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.info') as mock_info, \
             patch('streamlit.expander') as mock_expander, \
             patch('streamlit.write') as mock_write:
            
            # Setup mocks
            mock_container.return_value.__enter__ = Mock()
            mock_container.return_value.__exit__ = Mock()
            mock_columns.return_value = [Mock(), Mock(), Mock(), Mock()]
            mock_expander.return_value.__enter__ = Mock()
            mock_expander.return_value.__exit__ = Mock()
            
            UIComponents.display_recipe_card(complete_recipe, 1, user_ingredients)
            
            # Verify all components were called
            mock_container.assert_called_once()
            mock_columns.assert_called_with(4)
            mock_success.assert_called_once()  # Common ingredients
            mock_info.assert_called_once()     # Missing ingredients
            mock_expander.assert_called_once() # Description section

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

    def test_performance_with_large_datasets(self):
        """Test application performance with larger datasets."""
        # Create larger datasets
        large_recipes = pd.DataFrame({
            'recipe_id': range(1, 1001),  # 1000 recipes
            'name': [f'Recipe {i}' for i in range(1, 1001)],
            'ingredients': [['ingredient1', 'ingredient2'] for _ in range(1000)],
            'jaccard': np.random.random(1000),
            'score': np.random.random(1000)
        })
        
        large_interactions = pd.DataFrame({
            'user_id': np.random.randint(1, 101, 5000),  # 5000 interactions
            'recipe_id': np.random.randint(1, 1001, 5000),
            'rating': np.random.randint(1, 6, 5000)
        })
        
        # Test composite score calculation with large dataset
        result = RecommendationEngine._calculate_composite_score(large_recipes.copy())
        
        # Verify performance and correctness
        assert len(result) == 1000
        assert 'composite_score' in result.columns
        assert result['composite_score'].is_monotonic_decreasing

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

    def test_concurrent_workflow_simulation(self):
        """Test workflow under simulated concurrent conditions."""
        import threading
        import time
        
        app = MangeTaMainApp()
        results = []
        errors = []
        
        def worker_function(worker_id):
            try:
                # Simulate user input processing
                user_input = f"ingredient{worker_id}, pasta, eggs"
                ingredients = app._parse_user_ingredients(user_input)
                
                # Simulate stats display
                mock_recs = pd.DataFrame({
                    'recipe_id': [worker_id],
                    'jaccard': [0.5],
                    'score': [0.7]
                })
                
                with patch('streamlit.success'):
                    app._display_recommendations_stats(mock_recs, ingredients, "score")
                
                results.append(f"Worker {worker_id} completed successfully")
                
            except Exception as e:
                errors.append(f"Worker {worker_id} failed: {str(e)}")
        
        # Run multiple workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify results
        assert len(results) == 5
        assert len(errors) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])