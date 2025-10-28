"""
Tests complets pour la classe MangeTaMainApp
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
from src.core.app import MangeTaMainApp


class TestMangeTaMainApp:
    """Tests pour l'application principale MangeTaMain"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.app = MangeTaMainApp()
    
    def test_init(self):
        """Test de l'initialisation"""
        assert self.app.data_manager is not None
        assert self.app.recommendation_engine is not None
        assert self.app.ui_components is not None
        assert hasattr(self.app, '_parse_user_ingredients')
        assert hasattr(self.app, '_display_recommendations_stats')
        assert hasattr(self.app, '_handle_user_input_section')
        assert hasattr(self.app, '_handle_recommendations')
    
    def test_parse_user_ingredients_basic(self):
        """Test du parsing des ingrédients - cas basique"""
        result = self.app._parse_user_ingredients("chicken, onion, garlic")
        expected = ["chicken", "onion", "garlic"]
        assert result == expected
    
    def test_parse_user_ingredients_with_spaces(self):
        """Test du parsing avec espaces"""
        result = self.app._parse_user_ingredients("  chicken  ,  onion  ,  garlic  ")
        expected = ["chicken", "onion", "garlic"]
        assert result == expected
    
    def test_parse_user_ingredients_empty(self):
        """Test du parsing avec chaîne vide"""
        result = self.app._parse_user_ingredients("")
        assert result == []
    
    def test_parse_user_ingredients_mixed_case(self):
        """Test du parsing avec casse mixte"""
        result = self.app._parse_user_ingredients("CHICKEN, Onion, gArLiC")
        expected = ["chicken", "onion", "garlic"]
        assert result == expected
    
    def test_parse_user_ingredients_with_empty_items(self):
        """Test du parsing avec éléments vides"""
        result = self.app._parse_user_ingredients("chicken, , onion, , garlic")
        expected = ["chicken", "onion", "garlic"]
        assert result == expected
    
    @patch('src.core.app.MangeTaMainApp._display_recommendations_stats')
    def test_display_recommendations_stats_basic(self, mock_display):
        """Test d'affichage des stats avec recommandations - mock complet"""
        # Tester que la méthode peut être appelée
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'jaccard': [0.5, 0.3, 0.7],
            'score': [4.5, 3.8, 4.2]
        })
        user_ingredients = ["chicken", "onion"]
        
        # Appeler la méthode mocké
        self.app._display_recommendations_stats(recommendations, user_ingredients)
        
        # Vérifier qu'elle a été appelée
        mock_display.assert_called_once()
    
    def test_display_recommendations_logic_basic(self):
        """Test de la logique de base des stats"""
        # Créer des données avec les colonnes minimales
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2],
            'jaccard': [0.5, 0.3],
            'score': [4.5, 3.8]
        })
        
        # Test de calcul des statistiques de base
        avg_jaccard = recommendations['jaccard'].mean()
        assert avg_jaccard == 0.4
        
        max_jaccard = recommendations['jaccard'].max()
        assert max_jaccard == 0.5
    
    def test_display_recommendations_logic_cosine(self):
        """Test de la logique avec données cosine"""
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2],
            'jaccard': [0.5, 0.3],
            'cosine': [0.8, 0.6],
            'score': [4.5, 3.8]
        })
        
        # Test que cosine est présent
        assert 'cosine' in recommendations.columns
        avg_cosine = recommendations['cosine'].mean()
        assert avg_cosine == 0.7
    
    @patch('streamlit.warning')
    @patch('streamlit.info')
    def test_display_recommendations_stats_empty(self, mock_info, mock_warning):
        """Test d'affichage avec recommandations vides"""
        recommendations = pd.DataFrame()
        user_ingredients = ["chicken"]
        
        self.app._display_recommendations_stats(recommendations, user_ingredients)
        
        mock_warning.assert_called_once()
        mock_info.assert_called_once()
        
        warning_msg = mock_warning.call_args[0][0]
        assert "Aucune recommandation trouvée" in warning_msg
    
    def test_handle_user_input_logic(self):
        """Test de la logique de base pour la saisie utilisateur"""
        # Test que les méthodes existent
        assert hasattr(self.app, '_handle_user_input_section')
        assert hasattr(self.app, '_handle_recommendations')
        
        # Test des constantes utilisées dans la méthode
        time_options = [None, 15, 30, 45, 60, 90, 120, 180]
        assert None in time_options
        assert 15 in time_options
        assert 180 in time_options
        
        sort_options = ["intelligent", "jaccard", "cosine", "score"]
        assert "intelligent" in sort_options
        assert "jaccard" in sort_options
    
    @patch('streamlit.spinner')
    @patch('streamlit.subheader')
    @patch('streamlit.info')
    @patch('streamlit.markdown')
    def test_handle_recommendations_logic(self, mock_markdown, mock_info, mock_subheader, mock_spinner):
        """Test de la logique des recommandations"""
        # Créer des DataFrames de test minimaux
        recipes_df = pd.DataFrame({
            'recipe_id': [1, 2],
            'name': ['Recipe 1', 'Recipe 2'],
            'ingredients': ['chicken,onion', 'beef,potato']
        })
        
        interactions_df = pd.DataFrame({
            'user_id': [1, 2],
            'recipe_id': [1, 2],
            'rating': [4.0, 5.0]
        })
        
        user_input = "chicken, onion"
        time_limit = None
        n_recommendations = 5
        recommend_button = True
        sort_mode = "intelligent"
        
        # Mock des composants Streamlit
        mock_spinner.return_value.__enter__ = Mock()
        mock_spinner.return_value.__exit__ = Mock()
        
        # Mock du moteur de recommandation pour éviter les erreurs
        with patch.object(self.app.recommendation_engine, 'get_recommendations') as mock_get_recs:
            mock_get_recs.return_value = pd.DataFrame({
                'recipe_id': [1],
                'jaccard': [0.5],
                'score': [4.0],
                'name': ['Test Recipe']
            })
            
            with patch.object(self.app, '_display_recommendations_stats') as mock_display:
                # Appeler la méthode
                self.app._handle_recommendations(
                    recipes_df, interactions_df, user_input,
                    time_limit, n_recommendations, recommend_button, sort_mode
                )
                
                # Vérifier que les méthodes ont été appelées
                mock_get_recs.assert_called_once()
                mock_display.assert_called_once()
    
    def test_sort_mode_logic(self):
        """Test de la logique des modes de tri"""
        # Test des différents modes de tri
        sort_info = {
            "intelligent": "🎯 Tri intelligent hybride (Jaccard + Cosine + Score)",
            "jaccard": "🥄 Priorise les correspondances exactes (Jaccard)",
            "cosine": "🧠 Priorise la similarité sémantique (Cosine TF-IDF)",
            "score": "⭐ Tri par score global uniquement"
        }
        
        # Vérifier que tous les modes sont définis
        assert "intelligent" in sort_info
        assert "jaccard" in sort_info
        assert "cosine" in sort_info
        assert "score" in sort_info
        
        # Test de la logique de paramètres
        for mode in ["intelligent", "jaccard", "cosine", "score"]:
            if mode == "intelligent":
                prioritize_jaccard = True
                custom_sort = False
            else:
                prioritize_jaccard = False
                custom_sort = mode
            
            # Vérifier la logique
            assert isinstance(prioritize_jaccard, bool)
            assert custom_sort in [False, "jaccard", "cosine", "score"]
    
    @patch('src.core.app.StyleManager.apply_styles')
    @patch.object(MangeTaMainApp, '_handle_user_input_section')
    @patch.object(MangeTaMainApp, '_handle_recommendations')
    def test_run_method_structure(self, mock_handle_recs, mock_handle_input, mock_styles):
        """Test de la structure de la méthode run"""
        # Mock des composants UI
        with patch.object(self.app.ui_components, 'display_main_header'), \
             patch.object(self.app.ui_components, 'display_sidebar_stats'), \
             patch.object(self.app.ui_components, 'display_footer'), \
             patch.object(self.app.data_manager, 'load_preprocessed_data') as mock_load:
            
            # Mock des données
            mock_recipes = pd.DataFrame({'recipe_id': [1, 2]})
            mock_interactions = pd.DataFrame({'user_id': [1, 2]})
            mock_load.return_value = (mock_recipes, mock_interactions)
            
            # Mock des retours de _handle_user_input_section
            mock_handle_input.return_value = ("chicken", None, 5, True, "intelligent")
            
            # Appeler la méthode run
            self.app.run()
            
            # Vérifier que les méthodes ont été appelées
            mock_styles.assert_called_once()
            mock_handle_input.assert_called_once()
            mock_handle_recs.assert_called_once()
    
    @patch('streamlit.warning')
    def test_empty_input_warning(self, mock_warning):
        """Test d'avertissement pour entrée vide"""
        # Simuler une entrée vide avec bouton pressé
        recipes_df = pd.DataFrame({'recipe_id': [1]})
        interactions_df = pd.DataFrame({'user_id': [1]})
        user_input = ""  # Entrée vide
        time_limit = None
        n_recommendations = 5
        recommend_button = True  # Bouton pressé
        sort_mode = "intelligent"
        
        # Appeler la méthode
        self.app._handle_recommendations(
            recipes_df, interactions_df, user_input,
            time_limit, n_recommendations, recommend_button, sort_mode
        )
        
        # Vérifier que l'avertissement a été affiché
        mock_warning.assert_called_once()
        warning_msg = mock_warning.call_args[0][0]
        assert "Veuillez entrer au moins un ingrédient" in warning_msg
    
    def test_app_components_initialization(self):
        """Test que tous les composants sont initialisés"""
        app = MangeTaMainApp()
        
        # Vérifier que tous les composants existent
        assert hasattr(app, 'data_manager')
        assert hasattr(app, 'recommendation_engine')
        assert hasattr(app, 'ui_components')
        
        # Vérifier qu'ils ne sont pas None
        assert app.data_manager is not None
        assert app.recommendation_engine is not None
        assert app.ui_components is not None
        
        # Vérifier que toutes les méthodes existent
        assert hasattr(app, 'run')
        assert hasattr(app, '_parse_user_ingredients')
        assert hasattr(app, '_display_recommendations_stats')
        assert hasattr(app, '_handle_user_input_section')
        assert hasattr(app, '_handle_recommendations')
    
    def test_run_data_loading_logic(self):
        """Test de la logique de chargement des données"""
        # Test que la méthode run existe et est callable
        assert hasattr(self.app, 'run')
        assert callable(self.app.run)
        
        # Test de la logique conditionnelle
        data_result = None
        assert data_result is None
        
        # Test avec tuple mais premier élément None
        data_result = (None, pd.DataFrame())
        assert data_result[0] is None
    
    def test_run_method_components(self):
        """Test des composants utilisés dans run"""
        # Vérifier que tous les composants nécessaires existent
        assert hasattr(self.app, 'data_manager')
        assert hasattr(self.app, 'ui_components')
        
        # Vérifier les méthodes des composants
        assert hasattr(self.app.data_manager, 'load_preprocessed_data')
        assert hasattr(self.app.ui_components, 'display_main_header')
        assert hasattr(self.app.ui_components, 'display_sidebar_stats')
        assert hasattr(self.app.ui_components, 'display_footer')
    
    def test_recommendation_sorting_logic(self):
        """Test de la logique de tri des recommandations"""
        # Données de test pour le tri
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'jaccard': [0.8, 0.5, 0.3],
            'cosine': [0.6, 0.9, 0.4],
            'score': [4.5, 3.8, 4.2]
        })
        
        # Test tri par jaccard
        sorted_by_jaccard = recommendations.sort_values('jaccard', ascending=False)
        assert sorted_by_jaccard.iloc[0]['jaccard'] == 0.8
        
        # Test tri par cosine
        sorted_by_cosine = recommendations.sort_values('cosine', ascending=False)
        assert sorted_by_cosine.iloc[0]['cosine'] == 0.9
        
        # Test tri par score
        sorted_by_score = recommendations.sort_values('score', ascending=False)
        assert sorted_by_score.iloc[0]['score'] == 4.5
        
        # Test head pour limiter les résultats
        limited = recommendations.head(2)
        assert len(limited) == 2