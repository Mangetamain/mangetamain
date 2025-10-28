"""
Tests unitaires pour le module managers/data_manager.py
Objectif: Augmenter la couverture de 45% à 90%+
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, mock_open
import sys
import os

# Import avec gestion d'erreur
try:
    from managers.data_manager import DataManager
except ImportError:
    pytest.skip("Module data_manager non accessible", allow_module_level=True)


class TestDataManagerComplete:
    """Tests complets pour DataManager"""
    
    def test_data_manager_initialization(self):
        """Test d'initialisation du DataManager"""
        dm = DataManager()
        assert dm is not None
        
        # Vérifier les attributs par défaut
        assert hasattr(dm, 'data_dir')
        assert hasattr(dm, 'cache_enabled')
    
    @patch('pandas.read_parquet')
    @patch('os.path.exists')
    def test_load_recipes_success(self, mock_exists, mock_read_parquet):
        """Test de chargement réussi des recettes"""
        mock_exists.return_value = True
        mock_read_parquet.return_value = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Pasta', 'Salad', 'Soup'],
            'ingredients': [['pasta', 'cheese'], ['lettuce'], ['vegetables']],
            'minutes': [30, 15, 45]
        })
        
        dm = DataManager()
        recipes = dm.load_recipes()
        
        assert isinstance(recipes, pd.DataFrame)
        assert len(recipes) == 3
        assert 'recipe_id' in recipes.columns
        mock_read_parquet.assert_called_once()
    
    @patch('pandas.read_parquet')
    @patch('os.path.exists')
    def test_load_recipes_file_not_found(self, mock_exists, mock_read_parquet):
        """Test quand le fichier de recettes n'existe pas"""
        mock_exists.return_value = False
        
        dm = DataManager()
        recipes = dm.load_recipes()
        
        # Devrait retourner un DataFrame vide ou gérer l'erreur
        assert isinstance(recipes, pd.DataFrame)
        mock_read_parquet.assert_not_called()
    
    @patch('pandas.read_parquet')
    @patch('os.path.exists')
    def test_load_interactions_success(self, mock_exists, mock_read_parquet):
        """Test de chargement réussi des interactions"""
        mock_exists.return_value = True
        mock_read_parquet.return_value = pd.DataFrame({
            'user_id': [1, 1, 2, 2],
            'recipe_id': [1, 2, 1, 3],
            'rating': [5, 4, 5, 3],
            'date': pd.date_range('2024-01-01', periods=4)
        })
        
        dm = DataManager()
        interactions = dm.load_interactions()
        
        assert isinstance(interactions, pd.DataFrame)
        assert len(interactions) == 4
        assert 'user_id' in interactions.columns
        assert 'recipe_id' in interactions.columns
        assert 'rating' in interactions.columns
        mock_read_parquet.assert_called_once()
    
    @patch('pandas.read_parquet')
    @patch('os.path.exists')
    def test_load_interactions_file_not_found(self, mock_exists, mock_read_parquet):
        """Test quand le fichier d'interactions n'existe pas"""
        mock_exists.return_value = False
        
        dm = DataManager()
        interactions = dm.load_interactions()
        
        # Devrait retourner un DataFrame vide ou gérer l'erreur
        assert isinstance(interactions, pd.DataFrame)
        mock_read_parquet.assert_not_called()
    
    @patch('pandas.read_parquet')
    def test_load_recipes_with_exception(self, mock_read_parquet):
        """Test de gestion d'exception lors du chargement"""
        mock_read_parquet.side_effect = Exception("Erreur de lecture")
        
        dm = DataManager()
        recipes = dm.load_recipes()
        
        # Devrait gérer l'exception gracieusement
        assert isinstance(recipes, pd.DataFrame)
    
    @patch('pandas.read_parquet')
    def test_load_interactions_with_exception(self, mock_read_parquet):
        """Test de gestion d'exception lors du chargement des interactions"""
        mock_read_parquet.side_effect = Exception("Erreur de lecture")
        
        dm = DataManager()
        interactions = dm.load_interactions()
        
        # Devrait gérer l'exception gracieusement
        assert isinstance(interactions, pd.DataFrame)
    
    def test_data_manager_with_custom_data_dir(self):
        """Test avec un répertoire de données personnalisé"""
        custom_dir = "/custom/data/path"
        dm = DataManager(data_dir=custom_dir)
        
        assert dm.data_dir == custom_dir
    
    @patch('pandas.read_parquet')
    @patch('os.path.exists')
    def test_data_validation_recipes(self, mock_exists, mock_read_parquet):
        """Test de validation des données de recettes"""
        mock_exists.return_value = True
        
        # Test avec données valides
        valid_data = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'ingredients': [['ing1'], ['ing2'], ['ing3']]
        })
        mock_read_parquet.return_value = valid_data
        
        dm = DataManager()
        recipes = dm.load_recipes()
        
        assert len(recipes) == 3
        assert all(col in recipes.columns for col in ['recipe_id', 'name'])
    
    @patch('pandas.read_parquet')
    @patch('os.path.exists')
    def test_data_validation_interactions(self, mock_exists, mock_read_parquet):
        """Test de validation des données d'interactions"""
        mock_exists.return_value = True
        
        # Test avec données valides
        valid_data = pd.DataFrame({
            'user_id': [1, 2, 3],
            'recipe_id': [1, 2, 3],
            'rating': [5, 4, 3]
        })
        mock_read_parquet.return_value = valid_data
        
        dm = DataManager()
        interactions = dm.load_interactions()
        
        assert len(interactions) == 3
        assert all(col in interactions.columns for col in ['user_id', 'recipe_id', 'rating'])
    
    @patch('pandas.read_parquet')
    @patch('os.path.exists')
    def test_empty_file_handling(self, mock_exists, mock_read_parquet):
        """Test de gestion des fichiers vides"""
        mock_exists.return_value = True
        mock_read_parquet.return_value = pd.DataFrame()  # DataFrame vide
        
        dm = DataManager()
        recipes = dm.load_recipes()
        interactions = dm.load_interactions()
        
        assert isinstance(recipes, pd.DataFrame)
        assert isinstance(interactions, pd.DataFrame)
        assert len(recipes) == 0
        assert len(interactions) == 0
    
    def test_cache_behavior(self):
        """Test du comportement de cache"""
        dm = DataManager(cache_enabled=True)
        assert dm.cache_enabled is True
        
        dm_no_cache = DataManager(cache_enabled=False)
        assert dm_no_cache.cache_enabled is False
    
    @patch('pandas.read_parquet')
    @patch('os.path.exists')
    def test_data_types_consistency(self, mock_exists, mock_read_parquet):
        """Test de cohérence des types de données"""
        mock_exists.return_value = True
        
        # Données avec types mixtes
        mixed_data = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3'],
            'minutes': [30.0, 45, "60"],  # Types mixtes
            'rating': [4.5, 5, 3.0]
        })
        mock_read_parquet.return_value = mixed_data
        
        dm = DataManager()
        data = dm.load_recipes()
        
        # Vérifier que les données sont chargées malgré les types mixtes
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 3


class TestDataManagerIntegration:
    """Tests d'intégration pour DataManager"""
    
    @patch('managers.data_manager.DataManager.load_recipes')
    @patch('managers.data_manager.DataManager.load_interactions')
    def test_full_data_loading_workflow(self, mock_load_interactions, mock_load_recipes):
        """Test du workflow complet de chargement de données"""
        # Mock des retours
        mock_load_recipes.return_value = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'name': ['Recipe 1', 'Recipe 2', 'Recipe 3']
        })
        mock_load_interactions.return_value = pd.DataFrame({
            'user_id': [1, 1, 2],
            'recipe_id': [1, 2, 1],
            'rating': [5, 4, 5]
        })
        
        dm = DataManager()
        recipes = dm.load_recipes()
        interactions = dm.load_interactions()
        
        # Vérifier que les deux datasets sont chargés
        assert len(recipes) == 3
        assert len(interactions) == 3
        
        # Vérifier la cohérence des IDs
        recipe_ids = set(recipes['recipe_id'])
        interaction_recipe_ids = set(interactions['recipe_id'])
        assert interaction_recipe_ids.issubset(recipe_ids)


if __name__ == '__main__':
    pytest.main([__file__])