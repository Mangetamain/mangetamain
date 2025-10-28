"""
Tests pour le module de chargement des données Kaggle.
"""
import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock, mock_open
from preprocessing.data_load import fetch_data, load_data


class TestDataLoad:
    
    @patch('kagglehub.dataset_download')
    def test_fetch_data_success(self, mock_download):
        """Test fetch_data avec succès"""
        mock_download.return_value = '/fake/downloaded/path'
        
        result_path = fetch_data('test/dataset')
        
        assert result_path == '/fake/downloaded/path'
        mock_download.assert_called_once_with('test/dataset')
    
    @patch('kagglehub.dataset_download')
    def test_fetch_data_with_version(self, mock_download):
        """Test fetch_data avec version spécifique"""
        mock_download.return_value = '/fake/path'
        
        result_path = fetch_data('test/dataset', version='v1')
        
        mock_download.assert_called_once_with('test/dataset:v1')
        assert result_path == '/fake/path'
    
    @patch('kagglehub.dataset_download')
    def test_fetch_data_error(self, mock_download):
        """Test fetch_data avec erreur"""
        mock_download.side_effect = Exception("Download failed")
        
        with pytest.raises(Exception):
            fetch_data('test/dataset')
    
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    @patch('os.path.join')
    def test_load_data_success(self, mock_join, mock_exists, mock_read_csv):
        """Test load_data avec succès"""
        # Mock des DataFrames
        mock_recipes = pd.DataFrame({
            'id': [1, 2],
            'name': ['Recipe 1', 'Recipe 2']
        })
        mock_interactions = pd.DataFrame({
            'recipe_id': [1, 2],
            'rating': [4.5, 3.8]
        })
        
        mock_exists.return_value = True
        mock_join.side_effect = lambda x, y: f"{x}/{y}"
        mock_read_csv.side_effect = [mock_recipes, mock_interactions]
        
        files_to_load = ['RAW_recipes.csv', 'RAW_interactions.csv']
        result = load_data('/fake/path', files_to_load)
        
        assert 'RAW_recipes.csv' in result
        assert 'RAW_interactions.csv' in result
        assert len(result['RAW_recipes.csv']) == 2
        assert len(result['RAW_interactions.csv']) == 2
        assert mock_read_csv.call_count == 2
    
    @patch('os.path.exists')
    @patch('os.path.join')
    def test_load_data_file_not_found(self, mock_join, mock_exists):
        """Test load_data avec fichier manquant"""
        mock_exists.return_value = False
        mock_join.side_effect = lambda x, y: f"{x}/{y}"
        
        files_to_load = ['missing_file.csv']
        
        with pytest.raises(FileNotFoundError, match="Fichier missing_file.csv introuvable"):
            load_data('/fake/path', files_to_load)
    
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    @patch('os.path.join')
    def test_load_data_empty_files_list(self, mock_join, mock_exists, mock_read_csv):
        """Test load_data avec liste de fichiers vide"""
        result = load_data('/fake/path', [])
        
        assert isinstance(result, dict)
        assert len(result) == 0
        mock_read_csv.assert_not_called()
    
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    @patch('os.path.join')
    def test_load_data_pandas_error(self, mock_join, mock_exists, mock_read_csv):
        """Test load_data avec erreur pandas"""
        mock_exists.return_value = True
        mock_join.side_effect = lambda x, y: f"{x}/{y}"
        mock_read_csv.side_effect = pd.errors.EmptyDataError("No data")
        
        files_to_load = ['corrupt_file.csv']
        
        with pytest.raises(pd.errors.EmptyDataError):
            load_data('/fake/path', files_to_load)


class TestDataLoadIntegration:
    """Tests d'intégration pour le module data_load"""
    
    @patch('preprocessing.data_load.fetch_data')
    @patch('preprocessing.data_load.load_data')
    def test_full_data_loading_workflow(self, mock_load_data, mock_fetch_data):
        """Test du workflow complet de chargement des données"""
        # Mock des données de retour
        mock_fetch_data.return_value = '/downloaded/path'
        mock_load_data.return_value = {
            'RAW_recipes.csv': pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Recipe 1', 'Recipe 2', 'Recipe 3']
            }),
            'RAW_interactions.csv': pd.DataFrame({
                'recipe_id': [1, 2, 3],
                'rating': [5, 4, 3]
            })
        }
        
        # Simuler le workflow complet
        dataset_path = fetch_data('test/dataset')
        files_to_load = ['RAW_recipes.csv', 'RAW_interactions.csv']
        data_frames = load_data(dataset_path, files_to_load)
        
        # Vérifications
        assert dataset_path == '/downloaded/path'
        assert len(data_frames) == 2
        assert 'RAW_recipes.csv' in data_frames
        assert 'RAW_interactions.csv' in data_frames
        
        recipes_df = data_frames['RAW_recipes.csv']
        interactions_df = data_frames['RAW_interactions.csv']
        
        assert len(recipes_df) == 3
        assert len(interactions_df) == 3
        assert 'id' in recipes_df.columns
        assert 'recipe_id' in interactions_df.columns


if __name__ == '__main__':
    pytest.main([__file__])