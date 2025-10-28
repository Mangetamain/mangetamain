"""
Tests de performance et end-to-end pour le système de recommandation.
"""
import pytest
import time
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os
import pickle

from preprocessing.data_prepro import RecipePreprocessor, RecipeFeatures
from preprocessing.reco_score import RecipeScorer


class TestPerformance:
    """Tests de performance du système"""
    
    @pytest.fixture
    def large_dataset(self):
        """Créer un dataset de test volumineux"""
        n_recipes = 1000
        
        recipes = []
        for i in range(n_recipes):
            recipe = {
                'id': i,
                'ingredients': f"['ingredient_{i%20}', 'ingredient_{(i+1)%20}', 'ingredient_{(i+2)%20}']",
                'nutrition': f'[{300+i%200}, {10+i%15}, {5+i%10}, {50+i%30}, {20+i%10}, {25+i%20}, {800+i%400}]',
                'tags': f"['tag_{i%10}', 'tag_{(i+1)%10}']",
                'steps': f"['Step 1 for recipe {i}', 'Step 2 for recipe {i}']",
                'minutes': 30 + (i % 60),
                'n_steps': 2 + (i % 5),
                'n_ingredients': 3,
                'description': f'Description for recipe {i}'
            }
            recipes.append(recipe)
        
        return pd.DataFrame(recipes)
    
    def test_preprocessing_performance(self, large_dataset):
        """Test performance du preprocessing"""
        preprocessor = RecipePreprocessor()
        
        start_time = time.time()
        features = preprocessor.preprocess_dataframe(large_dataset)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Vérifications
        assert len(features) == len(large_dataset)
        assert all(isinstance(f, RecipeFeatures) for f in features)
        
        # Performance: devrait traiter 1000 recettes en moins de 30 secondes
        assert processing_time < 30, f"Preprocessing took {processing_time:.2f}s, expected < 30s"
        
        print(f"Preprocessing 1000 recipes took {processing_time:.2f} seconds")
        print(f"Average time per recipe: {processing_time/len(large_dataset)*1000:.2f} ms")
    
    def test_scorer_initialization_performance(self):
        """Test performance d'initialisation du scorer"""
        # Créer un grand nombre de features
        features = []
        for i in range(500):
            feature = RecipeFeatures(
                recipe_id=i,
                ingredients={f'ingredient_{i%50}', f'ingredient_{(i+1)%50}'},
                ingredient_categories={f'cat_{i%10}': [f'ingredient_{i%50}']},
                normalized_ingredients_list=[f'ingredient_{i%50}', f'ingredient_{(i+1)%50}'],
                nutrition_dict={'calories': 300+i, 'protein': 20+i%15},
                tags={f'tag_{i%20}'},
                meal_type=['breakfast', 'lunch', 'dinner'][i%3],
                dietary_restrictions=[],
                cuisine_type=f'cuisine_{i%8}',
                n_steps=2+i%4,
                effort_score=(i%10)/10.0,
                cooking_techniques={f'technique_{i%6}'},
                description_keywords=[f'keyword_{i%15}']
            )
            features.append(feature)
        
        start_time = time.time()
        scorer = RecipeScorer(features)
        end_time = time.time()
        
        init_time = end_time - start_time
        
        # Vérifications
        assert len(scorer.recipe_features) == 500
        assert scorer.tfidf_matrix.shape[0] == 500
        
        # Performance: initialisation devrait prendre moins de 10 secondes
        assert init_time < 10, f"Scorer initialization took {init_time:.2f}s, expected < 10s"
        
        print(f"Scorer initialization for 500 recipes took {init_time:.2f} seconds")
    
    def test_recommendation_performance(self):
        """Test performance des recommandations"""
        # Créer des features de test
        features = []
        for i in range(200):
            feature = RecipeFeatures(
                recipe_id=i,
                ingredients={f'ingredient_{i%30}', f'ingredient_{(i+1)%30}', f'ingredient_{(i+2)%30}'},
                ingredient_categories={f'cat_{i%8}': [f'ingredient_{i%30}']},
                normalized_ingredients_list=[f'ingredient_{i%30}'],
                nutrition_dict={'calories': 250+i*2, 'protein': 15+i%20},
                tags={f'tag_{i%15}', f'tag_{(i+5)%15}'},
                meal_type=['breakfast', 'lunch', 'dinner'][i%3],
                dietary_restrictions=[],
                cuisine_type=f'cuisine_{i%6}',
                n_steps=1+i%6,
                effort_score=(i%12)/12.0,
                cooking_techniques={f'technique_{i%8}'},
                description_keywords=[f'keyword_{i%20}']
            )
            features.append(feature)
        
        scorer = RecipeScorer(features)
        
        # Test recommandation simple
        start_time = time.time()
        recommendations = scorer.recommend(['ingredient_1', 'ingredient_2'], {}, top_k=10)
        end_time = time.time()
        
        recommendation_time = end_time - start_time
        
        # Vérifications
        assert len(recommendations) == 10
        assert all('total_score' in rec for rec in recommendations)
        
        # Performance: recommandation devrait prendre moins de 5 secondes
        assert recommendation_time < 5, f"Recommendation took {recommendation_time:.2f}s, expected < 5s"
        
        print(f"Single recommendation (200 recipes) took {recommendation_time:.2f} seconds")
    
    def test_batch_recommendation_performance(self):
        """Test performance des recommandations en batch"""
        # Créer des features plus petites pour le test batch
        features = []
        for i in range(50):
            feature = RecipeFeatures(
                recipe_id=i,
                ingredients={f'ingredient_{i%15}', f'ingredient_{(i+1)%15}'},
                ingredient_categories={},
                normalized_ingredients_list=[f'ingredient_{i%15}'],
                nutrition_dict={'calories': 300+i*5},
                tags={f'tag_{i%8}'},
                meal_type='dinner',
                dietary_restrictions=[],
                cuisine_type='american',
                n_steps=2,
                effort_score=0.5,
                cooking_techniques={'bake'},
                description_keywords=[]
            )
            features.append(feature)
        
        scorer = RecipeScorer(features)
        
        # Préparer plusieurs requêtes utilisateur
        user_queries = [
            ['ingredient_1', 'ingredient_2'],
            ['ingredient_3', 'ingredient_4'],
            ['ingredient_5'],
            ['ingredient_1', 'ingredient_6'],
            ['ingredient_7', 'ingredient_8']
        ]
        
        start_time = time.time()
        all_similarities = scorer.cosine_similarity_batch(user_queries)
        end_time = time.time()
        
        batch_time = end_time - start_time
        
        # Vérifications
        assert all_similarities.shape == (5, 50)  # 5 queries x 50 recipes
        
        # Performance: batch devrait être plus rapide que les requêtes individuelles
        print(f"Batch similarity (5 queries, 50 recipes) took {batch_time:.2f} seconds")
        
        # Comparer avec les requêtes individuelles
        start_time = time.time()
        for query in user_queries:
            scorer.cosine_similarity_single(query)
        end_time = time.time()
        
        individual_time = end_time - start_time
        
        print(f"Individual similarities took {individual_time:.2f} seconds")
        
        # Le batch devrait être plus efficace (ou au moins pas beaucoup plus lent)
        efficiency_ratio = batch_time / individual_time
        assert efficiency_ratio < 2.0, f"Batch is {efficiency_ratio:.2f}x slower than individual"


class TestEndToEnd:
    """Tests end-to-end du système complet"""
    
    def test_complete_pipeline(self):
        """Test du pipeline complet de bout en bout"""
        # 1. Créer des données de test
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Chicken Rice', 'Beef Pasta', 'Veggie Salad'],
            'ingredients': [
                "['chicken breast', 'rice', 'garlic']",
                "['ground beef', 'pasta', 'tomato sauce']",
                "['lettuce', 'tomato', 'cucumber', 'olive oil']"
            ],
            'nutrition': [
                '[400, 10, 5, 50, 30, 25, 800]',
                '[600, 20, 8, 70, 25, 30, 1200]',
                '[150, 8, 3, 20, 5, 10, 300]'
            ],
            'tags': [
                "['dinner', 'main-dish', 'easy']",
                "['lunch', 'italian', 'comfort-food']",
                "['lunch', 'healthy', 'vegetarian', 'quick']"
            ],
            'steps': [
                "['Cook rice', 'Season chicken', 'Saute chicken', 'Combine']",
                "['Boil pasta', 'Brown beef', 'Make sauce', 'Combine']",
                "['Wash vegetables', 'Chop vegetables', 'Make dressing', 'Toss salad']"
            ],
            'minutes': [30, 45, 15],
            'n_steps': [4, 4, 4],
            'n_ingredients': [3, 3, 4],
            'description': [
                'Quick and easy chicken rice bowl',
                'Traditional beef pasta with rich sauce',
                'Fresh and healthy vegetable salad'
            ]
        })
        
        # 2. Preprocessing
        preprocessor = RecipePreprocessor()
        features = preprocessor.preprocess_dataframe(test_data)
        
        assert len(features) == 3
        assert all(isinstance(f, RecipeFeatures) for f in features)
        
        # 3. Création du scorer
        scorer = RecipeScorer(features)
        
        assert len(scorer.recipe_features) == 3
        assert len(scorer.all_ingredients) > 0
        
        # 4. Test de recommandations avec différents scénarios
        
        # Scénario 1: Utilisateur avec ingrédients spécifiques
        recommendations = scorer.recommend(['chicken', 'rice'], {}, top_k=2)
        
        assert len(recommendations) == 2
        assert recommendations[0]['recipe_id'] == 1  # Devrait recommander le chicken rice
        
        # Scénario 2: Préférences alimentaires
        veg_recommendations = scorer.recommend(
            ['lettuce', 'tomato'], 
            {'dietary_restrictions': ['vegetarian']}, 
            top_k=1
        )
        
        assert len(veg_recommendations) == 1
        
        # Scénario 3: Contrainte d'effort
        easy_recommendations = scorer.recommend(
            ['pasta'], 
            {'max_effort': 0.3}, 
            top_k=3
        )
        
        assert len(easy_recommendations) <= 3
        # Vérifier que les recommandations respectent la contrainte d'effort
        for rec in easy_recommendations:
            recipe_features = next(rf for rf in features if rf.recipe_id == rec['recipe_id'])
            assert recipe_features.effort_score <= 0.3
        
        # 5. Vérifier la structure des résultats
        for rec in recommendations:
            assert 'recipe_id' in rec
            assert 'total_score' in rec
            assert 'scores' in rec
            assert isinstance(rec['scores'], dict)
            assert 'jaccard' in rec['scores']
            assert 'cosine' in rec['scores']
            assert 'rating' in rec['scores']
            assert 'popularity' in rec['scores']
    
    def test_data_persistence(self):
        """Test sauvegarde et chargement des données"""
        # 1. Créer des données de test
        test_features = [
            RecipeFeatures(
                recipe_id=1,
                ingredients={'chicken', 'rice'},
                ingredient_categories={'proteins': ['chicken']},
                normalized_ingredients_list=['chicken', 'rice'],
                nutrition_dict={'calories': 400},
                tags={'dinner'},
                meal_type='dinner',
                dietary_restrictions=[],
                cuisine_type='american',
                n_steps=3,
                effort_score=0.3,
                cooking_techniques={'saute'},
                description_keywords=['delicious']
            )
        ]
        
        test_df = pd.DataFrame({
            'id': [1],
            'name': ['Test Recipe']
        })
        
        scorer = RecipeScorer(test_features)
        
        # 2. Sauvegarder dans un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            data_to_save = {
                'features': test_features,
                'original_df': test_df,
                'scorer': scorer
            }
            
            pickle.dump(data_to_save, tmp_file)
            tmp_file_path = tmp_file.name
        
        try:
            # 3. Charger les données
            with open(tmp_file_path, 'rb') as f:
                loaded_data = pickle.load(f)
            
            # 4. Vérifier l'intégrité des données
            assert 'features' in loaded_data
            assert 'original_df' in loaded_data
            assert 'scorer' in loaded_data
            
            assert len(loaded_data['features']) == 1
            assert len(loaded_data['original_df']) == 1
            
            # 5. Vérifier que le scorer fonctionne
            loaded_scorer = loaded_data['scorer']
            recommendations = loaded_scorer.recommend(['chicken'], {}, top_k=1)
            
            assert len(recommendations) == 1
            assert recommendations[0]['recipe_id'] == 1
            
        finally:
            # Nettoyer le fichier temporaire
            os.unlink(tmp_file_path)
    
    def test_error_handling_robustness(self):
        """Test robustesse face aux erreurs"""
        # Test avec des données corrompues/incomplètes
        corrupted_data = pd.DataFrame({
            'id': [1, 2, 3],
            'ingredients': [
                "['chicken']",  # Données valides
                "corrupted_data",  # Données corrompues
                None  # Données manquantes
            ],
            'nutrition': [
                '[400, 10, 5]',  # Valide
                'not_a_list',  # Invalide
                ''  # Vide
            ],
            'tags': [
                "['dinner']",  # Valide
                'invalid',  # Invalide
                None  # Null
            ],
            'steps': [
                "['cook']",  # Valide
                'bad_format',  # Invalide
                None  # Null
            ],
            'minutes': [30, None, 'invalid'],
            'n_steps': [3, None, 'bad'],
            'description': ['Good', None, '']
        })
        
        # Le preprocessing ne devrait pas planter
        preprocessor = RecipePreprocessor()
        features = preprocessor.preprocess_dataframe(corrupted_data)
        
        # Devrait produire des features pour toutes les recettes
        assert len(features) == 3
        
        # Le scorer devrait pouvoir être créé même avec des données partielles
        scorer = RecipeScorer(features)
        
        # Les recommandations devraient fonctionner
        recommendations = scorer.recommend(['chicken'], {}, top_k=3)
        
        # Devrait retourner au moins une recommandation
        assert len(recommendations) > 0
    
    def test_scalability_stress(self):
        """Test de résistance à la charge"""
        # Créer un dataset de taille moyenne
        n_recipes = 100
        
        features = []
        for i in range(n_recipes):
            feature = RecipeFeatures(
                recipe_id=i,
                ingredients={f'ing_{i%20}', f'ing_{(i+1)%20}', f'ing_{(i+2)%20}'},
                ingredient_categories={f'cat_{i%5}': [f'ing_{i%20}']},
                normalized_ingredients_list=[f'ing_{i%20}', f'ing_{(i+1)%20}'],
                nutrition_dict={'calories': 200+i*3, 'protein': 10+i%25},
                tags={f'tag_{i%12}', f'tag_{(i+3)%12}'},
                meal_type=['breakfast', 'lunch', 'dinner'][i%3],
                dietary_restrictions=[],
                cuisine_type=f'cuisine_{i%7}',
                n_steps=1+i%7,
                effort_score=(i%15)/15.0,
                cooking_techniques={f'tech_{i%10}'},
                description_keywords=[f'kw_{i%18}']
            )
            features.append(feature)
        
        scorer = RecipeScorer(features)
        
        # Test avec de nombreuses requêtes consécutives
        n_queries = 20
        start_time = time.time()
        
        for i in range(n_queries):
            user_ingredients = [f'ing_{i%20}', f'ing_{(i+1)%20}']
            recommendations = scorer.recommend(user_ingredients, {}, top_k=5)
            assert len(recommendations) == 5
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Completed {n_queries} recommendations on {n_recipes} recipes in {total_time:.2f}s")
        print(f"Average time per recommendation: {total_time/n_queries:.3f}s")
        
        # Performance acceptable: moins de 0.5s par recommandation en moyenne
        avg_time = total_time / n_queries
        assert avg_time < 0.5, f"Average recommendation time {avg_time:.3f}s is too slow"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])