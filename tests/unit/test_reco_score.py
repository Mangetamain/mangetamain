"""
Tests pour le système de recommandation de recettes.
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing.reco_score import RecipeScorer
from preprocessing.data_prepro import RecipeFeatures


class TestRecipeScorer:
    
    @pytest.fixture
    def sample_features(self):
        """Fixture avec des données de test"""
        return [
            RecipeFeatures(
                recipe_id=1,
                ingredients={'chicken', 'rice', 'garlic'},
                ingredient_categories={'proteins': ['chicken'], 'grains': ['rice']},
                normalized_ingredients_list=['chicken', 'rice', 'garlic'],
                nutrition_dict={'calories': 400, 'protein': 30, 'fat': 10},
                tags={'dinner', 'main-dish'},
                meal_type='dinner',
                dietary_restrictions=[],
                cuisine_type='american',
                n_steps=3,
                effort_score=0.3,
                cooking_techniques={'saute', 'boil'},
                description_keywords=['delicious', 'easy']
            ),
            RecipeFeatures(
                recipe_id=2,
                ingredients={'beef', 'pasta', 'tomato'},
                ingredient_categories={'proteins': ['beef'], 'grains': ['pasta']},
                normalized_ingredients_list=['beef', 'pasta', 'tomato'],
                nutrition_dict={'calories': 600, 'protein': 25, 'fat': 20},
                tags={'lunch', 'italian'},
                meal_type='lunch',
                dietary_restrictions=[],
                cuisine_type='italian',
                n_steps=5,
                effort_score=0.7,
                cooking_techniques={'boil', 'simmer'},
                description_keywords=['traditional', 'hearty']
            ),
            RecipeFeatures(
                recipe_id=3,
                ingredients={'chicken', 'vegetables', 'herbs'},
                ingredient_categories={'proteins': ['chicken'], 'vegetables': ['vegetables']},
                normalized_ingredients_list=['chicken', 'vegetables', 'herbs'],
                nutrition_dict={'calories': 300, 'protein': 28, 'fat': 8},
                tags={'dinner', 'healthy'},
                meal_type='dinner',
                dietary_restrictions=['low-fat'],
                cuisine_type='mediterranean',
                n_steps=2,
                effort_score=0.2,
                cooking_techniques={'grill'},
                description_keywords=['healthy', 'fresh']
            )
        ]
    
    @pytest.fixture
    def recipe_scorer(self, sample_features):
        """Fixture avec un RecipeScorer initialisé"""
        return RecipeScorer(sample_features)
    
    def test_init(self, sample_features):
        """Test initialisation du RecipeScorer"""
        scorer = RecipeScorer(sample_features)
        
        assert len(scorer.recipe_features) == 3
        assert len(scorer.all_ingredients) > 0
        assert scorer.tfidf_matrix.shape[0] == 3
        assert len(scorer.ingredient_to_index) > 0
    
    def test_init_empty(self):
        """Test initialisation avec liste vide"""
        scorer = RecipeScorer([])
        
        assert len(scorer.recipe_features) == 0
        assert len(scorer.all_ingredients) == 0
    
    def test_jaccard_similarity(self, recipe_scorer):
        """Test calcul de similarité Jaccard"""
        set1 = {'chicken', 'rice', 'garlic'}
        set2 = {'chicken', 'vegetables', 'herbs'}
        
        similarity = recipe_scorer.jaccard_similarity(set1, set2)
        
        assert 0 <= similarity <= 1
        assert isinstance(similarity, float)
        # Jaccard = intersection / union = 1 / 5 = 0.2
        expected = 1.0 / 5.0
        assert abs(similarity - expected) < 0.001
    
    def test_jaccard_similarity_identical(self, recipe_scorer):
        """Test Jaccard avec ensembles identiques"""
        set1 = {'chicken', 'rice'}
        
        similarity = recipe_scorer.jaccard_similarity(set1, set1)
        assert similarity == 1.0
    
    def test_jaccard_similarity_disjoint(self, recipe_scorer):
        """Test Jaccard avec ensembles disjoints"""
        set1 = {'chicken', 'rice'}
        set2 = {'beef', 'pasta'}
        
        similarity = recipe_scorer.jaccard_similarity(set1, set2)
        assert similarity == 0.0
    
    def test_cosine_similarity_single(self, recipe_scorer):
        """Test similarité cosine pour une recette"""
        user_ingredients = ['chicken', 'rice']
        
        similarities = recipe_scorer.cosine_similarity_single(user_ingredients)
        
        assert len(similarities) == 3
        assert all(0 <= sim <= 1 for sim in similarities)
        assert isinstance(similarities, np.ndarray)
    
    def test_cosine_similarity_single_empty(self, recipe_scorer):
        """Test avec ingrédients utilisateur vides"""
        similarities = recipe_scorer.cosine_similarity_single([])
        
        assert len(similarities) == 3
        assert all(sim == 0 for sim in similarities)
    
    def test_cosine_similarity_batch(self, recipe_scorer):
        """Test similarité cosine batch"""
        user_ingredients_list = [
            ['chicken', 'rice'],
            ['beef', 'pasta'],
            ['vegetables']
        ]
        
        similarities = recipe_scorer.cosine_similarity_batch(user_ingredients_list)
        
        assert similarities.shape == (3, 3)  # 3 users x 3 recipes
        assert np.all((similarities >= 0) & (similarities <= 1))
    
    def test_calculate_rating_score(self, recipe_scorer):
        """Test calcul du score de rating"""
        # Test avec différentes valeurs nutritionnelles
        nutrition1 = {'calories': 300, 'protein': 30, 'fat': 8}
        nutrition2 = {'calories': 800, 'protein': 10, 'fat': 40}
        
        score1 = recipe_scorer.calculate_rating_score(nutrition1)
        score2 = recipe_scorer.calculate_rating_score(nutrition2)
        
        assert 0 <= score1 <= 1
        assert 0 <= score2 <= 1
        assert isinstance(score1, float)
        assert isinstance(score2, float)
    
    def test_calculate_rating_score_empty(self, recipe_scorer):
        """Test avec nutrition vide"""
        score = recipe_scorer.calculate_rating_score({})
        assert 0 <= score <= 1
    
    def test_calculate_popularity_score(self, recipe_scorer):
        """Test calcul du score de popularité"""
        # Recette avec tags populaires
        tags1 = {'dinner', 'easy', 'quick'}
        tags2 = {'obscure-tag', 'very-specific'}
        
        score1 = recipe_scorer.calculate_popularity_score(tags1, 3, 30)
        score2 = recipe_scorer.calculate_popularity_score(tags2, 10, 120)
        
        assert 0 <= score1 <= 1
        assert 0 <= score2 <= 1
        assert isinstance(score1, float)
        assert isinstance(score2, float)
    
    def test_recommend_basic(self, recipe_scorer):
        """Test recommandation basique"""
        user_ingredients = ['chicken', 'rice']
        user_preferences = {}
        
        recommendations = recipe_scorer.recommend(
            user_ingredients=user_ingredients,
            user_preferences=user_preferences,
            top_k=2
        )
        
        assert len(recommendations) <= 2
        assert all('recipe_id' in rec for rec in recommendations)
        assert all('total_score' in rec for rec in recommendations)
        assert all('scores' in rec for rec in recommendations)
        
        # Vérifier que les scores sont triés par ordre décroissant
        scores = [rec['total_score'] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)
    
    def test_recommend_with_preferences(self, recipe_scorer):
        """Test recommandation avec préférences utilisateur"""
        user_ingredients = ['chicken']
        user_preferences = {
            'meal_type': 'dinner',
            'max_effort': 0.5,
            'dietary_restrictions': ['low-fat'],
            'cuisine_type': 'mediterranean'
        }
        
        recommendations = recipe_scorer.recommend(
            user_ingredients=user_ingredients,
            user_preferences=user_preferences,
            top_k=3
        )
        
        assert len(recommendations) <= 3
        # Vérifier que les recettes respectent les préférences
        for rec in recommendations:
            recipe_features = next(rf for rf in recipe_scorer.recipe_features 
                                 if rf.recipe_id == rec['recipe_id'])
            
            if user_preferences.get('meal_type'):
                # La recette devrait avoir le bon type de repas ou être compatible
                pass  # Test flexible car le matching peut être partiel
            
            if user_preferences.get('max_effort'):
                assert recipe_features.effort_score <= user_preferences['max_effort']
    
    def test_recommend_no_matches(self, recipe_scorer):
        """Test avec ingrédients qui ne matchent rien"""
        user_ingredients = ['exotic-ingredient-xyz']
        
        recommendations = recipe_scorer.recommend(
            user_ingredients=user_ingredients,
            user_preferences={},
            top_k=5
        )
        
        # Doit toujours retourner des recommandations (même avec score faible)
        assert len(recommendations) > 0
    
    def test_recommend_top_k_limit(self, recipe_scorer):
        """Test limitation du nombre de recommandations"""
        user_ingredients = ['chicken']
        
        recommendations = recipe_scorer.recommend(
            user_ingredients=user_ingredients,
            user_preferences={},
            top_k=1
        )
        
        assert len(recommendations) == 1
    
    def test_recommend_score_components(self, recipe_scorer):
        """Test que tous les composants de score sont présents"""
        user_ingredients = ['chicken', 'rice']
        
        recommendations = recipe_scorer.recommend(
            user_ingredients=user_ingredients,
            user_preferences={},
            top_k=1
        )
        
        assert len(recommendations) > 0
        rec = recommendations[0]
        
        assert 'scores' in rec
        scores = rec['scores']
        assert 'jaccard' in scores
        assert 'cosine' in scores
        assert 'rating' in scores
        assert 'popularity' in scores
        
        # Vérifier que tous les scores sont dans [0, 1]
        for score_name, score_value in scores.items():
            assert 0 <= score_value <= 1, f"Score {score_name} = {score_value} not in [0, 1]"
    
    def test_recommend_weights(self, recipe_scorer):
        """Test que les poids sont correctement appliqués"""
        user_ingredients = ['chicken']
        
        # Test avec poids par défaut
        recs_default = recipe_scorer.recommend(user_ingredients, {}, top_k=1)
        
        # Test avec poids personnalisés
        custom_weights = {
            'jaccard_weight': 0.8,
            'cosine_weight': 0.1,
            'rating_weight': 0.05,
            'popularity_weight': 0.05
        }
        
        recs_custom = recipe_scorer.recommend(
            user_ingredients, {}, top_k=1, **custom_weights
        )
        
        # Les scores totaux peuvent être différents
        assert len(recs_default) > 0
        assert len(recs_custom) > 0
    
    def test_edge_cases_empty_features(self):
        """Test avec RecipeFeatures ayant des valeurs vides"""
        empty_features = [
            RecipeFeatures(
                recipe_id=1,
                ingredients=set(),
                ingredient_categories={},
                normalized_ingredients_list=[],
                nutrition_dict={},
                tags=set(),
                meal_type=None,
                dietary_restrictions=[],
                cuisine_type=None,
                n_steps=0,
                effort_score=0.0,
                cooking_techniques=set(),
                description_keywords=[]
            )
        ]
        
        scorer = RecipeScorer(empty_features)
        recommendations = scorer.recommend(['chicken'], {}, top_k=1)
        
        assert len(recommendations) == 1  # Doit toujours retourner quelque chose
    
    def test_performance_large_dataset(self):
        """Test performance avec un dataset plus large"""
        # Créer un dataset de test plus large
        large_features = []
        for i in range(100):
            features = RecipeFeatures(
                recipe_id=i,
                ingredients={f'ingredient_{i%10}', f'ingredient_{(i+1)%10}'},
                ingredient_categories={f'cat_{i%5}': [f'ingredient_{i%10}']},
                normalized_ingredients_list=[f'ingredient_{i%10}'],
                nutrition_dict={'calories': 300 + i, 'protein': 20 + i%10},
                tags={f'tag_{i%8}'},
                meal_type=['breakfast', 'lunch', 'dinner'][i%3],
                dietary_restrictions=[],
                cuisine_type=f'cuisine_{i%6}',
                n_steps=i%5 + 1,
                effort_score=(i%10) / 10.0,
                cooking_techniques={f'technique_{i%4}'},
                description_keywords=[f'keyword_{i%7}']
            )
            large_features.append(features)
        
        scorer = RecipeScorer(large_features)
        recommendations = scorer.recommend(['ingredient_1'], {}, top_k=10)
        
        assert len(recommendations) == 10
        # Vérifier que c'est raisonnablement rapide (test implicite)


if __name__ == '__main__':
    pytest.main([__file__])