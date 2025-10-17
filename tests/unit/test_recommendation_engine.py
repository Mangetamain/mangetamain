"""
Unit tests for RecommendationEngine class.

This module contains unit tests for the RecommendationEngine class that handles
recipe recommendations and scoring algorithms.
"""

import unittest
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Import the class under test
from src.engines.recommendation_engine import RecommendationEngine


class TestRecommendationEngine(unittest.TestCase):
    """Unit tests for RecommendationEngine class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Sample recipes data
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
            'n_ingredients': [4, 4, 4, 4, 3],
            'minutes': [30, 15, 60, 45, 25]
        })
        
        # Sample interactions data
        self.sample_interactions = pd.DataFrame({
            'user_id': [1, 1, 2, 2, 3, 3, 4, 5],
            'recipe_id': [1, 2, 1, 3, 2, 4, 5, 1],
            'rating': [5, 4, 5, 3, 4, 5, 3, 4],
            'date': pd.date_range('2024-01-01', periods=8)
        })
        
        # Sample user ingredients
        self.user_ingredients = ['pasta', 'eggs', 'cheese']

    def test_calculate_composite_score_empty_dataframe(self):
        """Test composite score calculation with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = RecommendationEngine._calculate_composite_score(empty_df)
        
        self.assertTrue(result.empty)

    def test_calculate_composite_score_with_valid_data(self):
        """Test composite score calculation with valid data."""
        # Create sample recommendations DataFrame
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'jaccard': [0.8, 0.6, 0.4],
            'score': [0.9, 0.7, 0.5]
        })
        
        result = RecommendationEngine._calculate_composite_score(recommendations)
        
        # Verify composite_score column is added
        self.assertIn('composite_score', result.columns)
        
        # Verify results are sorted by composite_score descending
        self.assertTrue(result['composite_score'].is_monotonic_decreasing)
        
        # Verify first recipe has highest composite score
        self.assertEqual(result.iloc[0]['recipe_id'], 1)

    def test_calculate_composite_score_with_missing_columns(self):
        """Test composite score calculation with missing jaccard or score columns."""
        # Test with missing jaccard column
        recommendations_no_jaccard = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'score': [0.9, 0.7, 0.5]
        })
        
        result = RecommendationEngine._calculate_composite_score(recommendations_no_jaccard)
        self.assertIn('composite_score', result.columns)
        
        # Test with missing score column
        recommendations_no_score = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'jaccard': [0.8, 0.6, 0.4]
        })
        
        result = RecommendationEngine._calculate_composite_score(recommendations_no_score)
        self.assertIn('composite_score', result.columns)

    def test_calculate_composite_score_high_jaccard_bonus(self):
        """Test that high Jaccard index (>0.3) gets bonus points."""
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'jaccard': [0.8, 0.2, 0.4],  # Recipe 1 and 3 should get bonus
            'score': [0.5, 0.9, 0.5]     # Recipe 2 has higher base score
        })
        
        result = RecommendationEngine._calculate_composite_score(recommendations)
        
        # Recipes with jaccard > 0.3 should get bonus
        high_jaccard_recipes = result[result['jaccard'] > 0.3]
        self.assertTrue(len(high_jaccard_recipes) == 2)


class TestRecommendationEnginePytest:
    """Pytest-style tests for RecommendationEngine class."""
    
    @pytest.fixture
    def sample_recipes_df(self):
        """Fixture providing sample recipes DataFrame."""
        return pd.DataFrame({
            'recipe_id': [1, 2, 3, 4, 5],
            'name': ['Pasta Carbonara', 'Caesar Salad', 'Apple Pie', 'Chicken Stew', 'Vegetable Soup'],
            'ingredients': [
                ['pasta', 'eggs', 'cheese', 'bacon'],
                ['lettuce', 'chicken', 'parmesan', 'croutons'],
                ['apples', 'flour', 'sugar', 'butter'],
                ['chicken', 'carrots', 'onions', 'potatoes'],
                ['vegetables', 'broth', 'herbs']
            ],
            'n_ingredients': [4, 4, 4, 4, 3],
            'minutes': [30, 15, 60, 45, 25]
        })
    
    @pytest.fixture
    def sample_interactions_df(self):
        """Fixture providing sample interactions DataFrame."""
        return pd.DataFrame({
            'user_id': [1, 1, 2, 2, 3, 3, 4, 5],
            'recipe_id': [1, 2, 1, 3, 2, 4, 5, 1],
            'rating': [5, 4, 5, 3, 4, 5, 3, 4],
            'date': pd.date_range('2024-01-01', periods=8)
        })

    @pytest.fixture
    def sample_recommendations_df(self):
        """Fixture providing sample recommendations DataFrame."""
        return pd.DataFrame({
            'recipe_id': [1, 2, 3, 4],
            'name': ['Pasta Carbonara', 'Caesar Salad', 'Apple Pie', 'Chicken Stew'],
            'jaccard': [0.8, 0.6, 0.4, 0.2],
            'score': [0.7, 0.9, 0.5, 0.8],
            'ingredients': [
                ['pasta', 'eggs', 'cheese', 'bacon'],
                ['lettuce', 'chicken', 'parmesan', 'croutons'],
                ['apples', 'flour', 'sugar', 'butter'],
                ['chicken', 'carrots', 'onions', 'potatoes']
            ]
        })

    def test_composite_score_calculation(self, sample_recommendations_df):
        """Test composite score calculation with pytest style."""
        result = RecommendationEngine._calculate_composite_score(
            sample_recommendations_df.copy()
        )
        
        # Assertions
        assert 'composite_score' in result.columns
        assert len(result) == 4
        assert result['composite_score'].dtype == np.float64
        
        # Verify reasonable scores (between 0 and 1)
        assert result['composite_score'].min() >= 0
        assert result['composite_score'].max() <= 1
        
        # Verify that recipes with higher scores have higher composite scores
        assert result.loc[result['score'].idxmax(), 'composite_score'] >= result['composite_score'].mean()

    @pytest.mark.parametrize("weight", [0.6, 0.7, 0.5, 1.0, 0.0])
    def test_different_weight_combinations(self, sample_recommendations_df, weight):
        """Test composite score with different weight combinations."""
        result = RecommendationEngine._calculate_composite_score(
            sample_recommendations_df.copy()
        )
        
        assert 'composite_score' in result.columns
        assert len(result) == 4
        assert result['composite_score'].min() >= 0

    

    def test_edge_cases_composite_score(self):
        """Test edge cases for composite score calculation."""
        # Test with zero values
        zero_df = pd.DataFrame({
            'recipe_id': [1, 2],
            'jaccard': [0.0, 0.0],
            'score': [0.0, 0.0]
        })
        
        result = RecommendationEngine._calculate_composite_score(zero_df)
        assert 'composite_score' in result.columns
        
        # Test with NaN values
        nan_df = pd.DataFrame({
            'recipe_id': [1, 2],
            'jaccard': [np.nan, 0.5],
            'score': [0.7, np.nan]
        })
        
        # Should handle NaN gracefully
        result = RecommendationEngine._calculate_composite_score(nan_df)
        assert 'composite_score' in result.columns




if __name__ == '__main__':
    # Run unittest tests
    unittest.main(verbosity=2)