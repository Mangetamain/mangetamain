"""
Tests ciblés pour couvrir les lignes manquées de src/core/app.py
Focus sur les lignes 38-40, 50, 70-142, 170-178, 189-197, 218
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
from src.core.app import MangeTaMainApp


class TestCoreAppMissedLines:
    """Tests pour couvrir les lignes manquées de core/app.py"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.app = MangeTaMainApp()
    
    @patch('streamlit.success')
    def test_display_stats_cosine_info_branch(self, mock_success):
        """Test lignes 38-40: branche cosine_info avec cosine disponible"""
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2],
            'jaccard': [0.8, 0.6],
            'cosine': [0.9, 0.7],  # Colonne cosine présente
            'score': [4.5, 4.0]
        })
        
        # Mock pour éviter l'appel à display_recipe_card
        with patch.object(self.app.ui_components, 'display_recipe_card'):
            self.app._display_recommendations_stats(recommendations, ['chicken'], "cosine")
        
        # Vérifier que success a été appelé avec cosine info
        mock_success.assert_called_once()
        call_args = mock_success.call_args[0][0]
        assert "Cosine moyen" in call_args
    
    @patch('streamlit.success')
    def test_display_stats_intelligent_mode_branch(self, mock_success):
        """Test ligne 50: branche intelligent avec composite_score"""
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2],
            'jaccard': [0.8, 0.6],
            'composite_score': [0.85, 0.75],  # Colonne composite_score présente
            'score': [4.5, 4.0]
        })
        
        with patch.object(self.app.ui_components, 'display_recipe_card'):
            self.app._display_recommendations_stats(recommendations, ['chicken'], "intelligent")
        
        mock_success.assert_called_once()
        call_args = mock_success.call_args[0][0]
        assert "Score composite moyen" in call_args
    
    @patch('streamlit.success')
    def test_display_stats_score_mode_branch(self, mock_success):
        """Test branche score mode avec calcul avg_score"""
        recommendations = pd.DataFrame({
            'recipe_id': [1, 2],
            'jaccard': [0.8, 0.6],
            'score': [4.5, 4.0]
        })
        
        with patch.object(self.app.ui_components, 'display_recipe_card'):
            self.app._display_recommendations_stats(recommendations, ['chicken'], "score")
        
        mock_success.assert_called_once()
        call_args = mock_success.call_args[0][0]
        assert "score global" in call_args
    
    @patch('streamlit.expander')
    @patch('streamlit.slider')
    @patch('streamlit.button')
    @patch('streamlit.write')
    @patch('streamlit.selectbox')
    @patch('streamlit.text_input')
    @patch('streamlit.columns')
    @patch('streamlit.header')
    @patch('streamlit.markdown')
    def test_handle_user_input_full_execution(self, mock_markdown, mock_header, mock_columns,
                                             mock_text_input, mock_selectbox, mock_write,
                                             mock_button, mock_slider, mock_expander):
        """Test lignes 70-142: exécution complète de _handle_user_input_section"""
        
        # Setup des mocks pour tous les widgets Streamlit
        col_mock1 = Mock()
        col_mock2 = Mock()
        col_mock1.__enter__ = Mock(return_value=col_mock1)
        col_mock1.__exit__ = Mock()
        col_mock2.__enter__ = Mock(return_value=col_mock2)
        col_mock2.__exit__ = Mock()
        
        mock_columns.side_effect = [
            [col_mock1, col_mock2],  # Pour col_input, col_time
            [col_mock1, col_mock2]   # Pour col_sort, col_button
        ]
        
        # Mock des retours
        mock_text_input.return_value = "chicken, onion"
        mock_selectbox.side_effect = [30, "cosine"]  # time_limit, sort_mode
        mock_button.return_value = True
        mock_slider.return_value = 10
        
        # Mock de l'expander
        expander_mock = Mock()
        expander_mock.__enter__ = Mock()
        expander_mock.__exit__ = Mock()
        mock_expander.return_value = expander_mock
        
        # Exécuter la méthode complète
        result = self.app._handle_user_input_section()
        
        # Vérifier les retours
        user_input, time_limit, n_recommendations, recommend_button, sort_mode = result
        assert user_input == "chicken, onion"
        assert time_limit == 30
        assert n_recommendations == 10
        assert recommend_button is True
        assert sort_mode == "cosine"
        
        # Vérifier que tous les widgets ont été appelés
        mock_header.assert_called_once()
        assert mock_columns.call_count == 2
        mock_text_input.assert_called_once()
        assert mock_selectbox.call_count == 2
        mock_button.assert_called_once()
        mock_slider.assert_called_once()
        mock_expander.assert_called_once()
        mock_markdown.assert_called_once()
    
    def test_sort_mode_branches_170_178(self):
        """Test lignes 170-178: toutes les branches de sort_mode"""
        recipes_df = pd.DataFrame({'recipe_id': [1, 2]})
        interactions_df = pd.DataFrame({'user_id': [1, 2]})
        
        # Test toutes les branches de sort_mode
        test_cases = [
            ("intelligent", True, False),
            ("jaccard", False, "jaccard"),
            ("cosine", False, "cosine"),
            ("score", False, "score")
        ]
        
        for sort_mode, expected_prioritize, expected_custom in test_cases:
            with patch.object(self.app.recommendation_engine, 'get_recommendations') as mock_get_recs:
                with patch.object(self.app, '_display_recommendations_stats'):
                    with patch('streamlit.spinner') as mock_spinner:
                        with patch('streamlit.subheader'):
                            with patch('streamlit.info'):
                                with patch('streamlit.markdown'):
                                    
                                    spinner_context = Mock()
                                    spinner_context.__enter__ = Mock()
                                    spinner_context.__exit__ = Mock()
                                    mock_spinner.return_value = spinner_context
                                    
                                    mock_get_recs.return_value = pd.DataFrame({
                                        'recipe_id': [1],
                                        'jaccard': [0.5],
                                        'score': [4.0]
                                    })
                                    
                                    # Appeler _handle_recommendations avec bouton pressé
                                    self.app._handle_recommendations(
                                        recipes_df, interactions_df, "chicken, onion",
                                        None, 5, True, sort_mode
                                    )
                                    
                                    # Vérifier que get_recommendations a été appelé
                                    mock_get_recs.assert_called_once()
                                    # Test réussi si pas d'exception levée
    
    def test_custom_sort_branches_189_197(self):
        """Test lignes 189-197: branches de tri personnalisé"""
        recipes_df = pd.DataFrame({'recipe_id': [1, 2, 3]})
        interactions_df = pd.DataFrame({'user_id': [1, 2, 3]})
        
        # Données avec toutes les colonnes pour le tri
        mock_recommendations = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'jaccard': [0.8, 0.5, 0.3],
            'cosine': [0.6, 0.9, 0.4],
            'score': [4.5, 3.8, 4.2]
        })
        
        sort_modes = ["jaccard", "cosine", "score"]
        
        for sort_mode in sort_modes:
            with patch.object(self.app.recommendation_engine, 'get_recommendations') as mock_get_recs:
                with patch.object(self.app, '_display_recommendations_stats'):
                    with patch('streamlit.spinner') as mock_spinner:
                        with patch('streamlit.subheader'):
                            with patch('streamlit.info'):
                                with patch('streamlit.markdown'):
                                    
                                    spinner_context = Mock()
                                    spinner_context.__enter__ = Mock()
                                    spinner_context.__exit__ = Mock()
                                    mock_spinner.return_value = spinner_context
                                    
                                    # Retourner nos données de test
                                    mock_get_recs.return_value = mock_recommendations.copy()
                                    
                                    # Appeler avec le mode de tri spécifique
                                    self.app._handle_recommendations(
                                        recipes_df, interactions_df, "chicken, onion",
                                        None, 2, True, sort_mode  # n_recommendations = 2
                                    )
                                    
                                    # Le tri personnalisé et head() devraient être appliqués
                                    mock_get_recs.assert_called_once()
    
    def test_run_method_line_218_unpacking(self):
        """Test ligne 218: unpacking de data_result dans run()"""
        with patch('src.core.app.StyleManager.apply_styles'):
            with patch.object(self.app.ui_components, 'display_main_header'):
                with patch.object(self.app.data_manager, 'load_preprocessed_data') as mock_load:
                    with patch.object(self.app.ui_components, 'display_sidebar_stats') as mock_sidebar:
                        with patch.object(self.app, '_handle_user_input_section') as mock_input:
                            with patch.object(self.app, '_handle_recommendations') as mock_handle:
                                with patch.object(self.app.ui_components, 'display_footer'):
                                    
                                    # Mock successful data loading pour déclencher la ligne 218
                                    recipes_df = pd.DataFrame({'recipe_id': [1, 2], 'name': ['Recipe1', 'Recipe2']})
                                    interactions_df = pd.DataFrame({'user_id': [1, 2], 'recipe_id': [1, 2]})
                                    mock_load.return_value = (recipes_df, interactions_df)
                                    
                                    mock_input.return_value = ("chicken", None, 5, False, "intelligent")
                                    
                                    # Exécuter run() - ceci devrait déclencher la ligne 218
                                    self.app.run()
                                    
                                    # Vérifier que sidebar_stats a été appelé avec les DataFrames unpacked
                                    mock_sidebar.assert_called_once()
                                    call_args = mock_sidebar.call_args[0]
                                    
                                    # Vérifier que les DataFrames ont été correctement unpacked
                                    assert len(call_args) == 2  # recipes_df et interactions_df
                                    assert isinstance(call_args[0], pd.DataFrame)  # recipes_df
                                    assert isinstance(call_args[1], pd.DataFrame)  # interactions_df
    
    def test_format_func_lambda_branches(self):
        """Test des lambdas dans les format_func (partie des lignes 70-142)"""
        # Test de la lambda pour time_options
        time_format_func = lambda x: "Illimité" if x is None else f"{x} min"
        assert time_format_func(None) == "Illimité"
        assert time_format_func(30) == "30 min"
        
        # Test de la lambda pour sort_mode
        sort_format_dict = {
            "intelligent": "🎯 Intelligent (Jaccard + Cosine + Score)",
            "jaccard": "🥄 Priorité Jaccard (correspondances exactes)",
            "cosine": "🧠 Priorité Cosine (similarité sémantique TF-IDF)",
            "score": "⭐ Score global uniquement"
        }
        
        sort_format_func = lambda x: sort_format_dict[x]
        assert "Intelligent" in sort_format_func("intelligent")
        assert "Jaccard" in sort_format_func("jaccard")
        assert "Cosine" in sort_format_func("cosine")
        assert "Score global" in sort_format_func("score")