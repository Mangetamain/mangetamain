"""
Tests pour le gestionnaire de données
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
import os
from src.managers.data_manager import DataManager


class TestDataManager:
    """Tests pour le gestionnaire de données"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.data_manager = DataManager()
    
    def test_init(self):
        """Test de l'initialisation"""
        assert self.data_manager.recipes_path == "/shared_data/recipes_processed.pkl"
        assert self.data_manager.interactions_path == "/shared_data/interactions.pkl"
    
    @patch('os.path.exists')
    @patch('streamlit.error')
    def test_load_data_files_not_found(self, mock_error, mock_exists):
        """Test quand les fichiers n'existent pas"""
        mock_exists.return_value = False
        
        result = self.data_manager.load_preprocessed_data()
        
        assert result == (None, None)
        mock_error.assert_called_once()
    
    def test_paths_configuration(self):
        """Test de la configuration des chemins"""
        assert self.data_manager.recipes_path.endswith('recipes_processed.pkl')
        assert self.data_manager.interactions_path.endswith('interactions.pkl')
        assert '/shared_data/' in self.data_manager.recipes_path
        assert '/shared_data/' in self.data_manager.interactions_path
    
    def test_data_manager_attributes(self):
        """Test des attributs du data manager"""
        assert hasattr(self.data_manager, 'recipes_path')
        assert hasattr(self.data_manager, 'interactions_path')
        assert hasattr(self.data_manager, 'load_preprocessed_data')
        assert callable(self.data_manager.load_preprocessed_data)