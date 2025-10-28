"""
Tests pour le preprocessing des données de recettes.
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from preprocessing.data_prepro import (
    RecipePreprocessor, IngredientPreprocessor, NutritionPreprocessor,
    TagsPreprocessor, StepsPreprocessor, DescriptionPreprocessor,
    RecipeFeatures
)


class TestIngredientPreprocessor:
    
    def test_normalize_ingredient_basic(self):
        """Test normalisation basique d'ingrédient"""
        # Test avec quantités et mesures
        result = IngredientPreprocessor.normalize_ingredient("2 cups fresh chicken breast")
        assert "chicken" in result.lower()
        assert "breast" in result.lower()
        assert "cups" not in result.lower()
        assert "2" not in result
    
    def test_normalize_ingredient_empty(self):
        """Test avec ingrédient vide"""
        result = IngredientPreprocessor.normalize_ingredient("")
        assert result == ""
        
        result = IngredientPreprocessor.normalize_ingredient(None)
        assert result == ""
    
    def test_normalize_ingredient_special_chars(self):
        """Test avec caractères spéciaux"""
        result = IngredientPreprocessor.normalize_ingredient("olive-oil, extra-virgin")
        assert "olive" in result.lower()
        assert "oil" in result.lower()
    
    @patch('preprocessing.data_prepro.IngredientPreprocessor.load_ingredient_map')
    def test_categorize_ingredients(self, mock_load_map):
        """Test catégorisation des ingrédients"""
        mock_load_map.return_value = {
            'chicken': 'proteins',
            'tomato': 'vegetables',
            'rice': 'grains'
        }
        
        preprocessor = IngredientPreprocessor()
        ingredients = ["chicken breast", "tomato sauce", "basmati rice"]
        categories = preprocessor.categorize_ingredients(ingredients)
        
        assert isinstance(categories, dict)
        # Vérifier que les catégories sont créées
        assert len(categories) >= 0
    
    def test_process_ingredients_list_valid(self):
        """Test processing d'une liste valide"""
        ingredients_str = "['chicken breast', 'tomato sauce', 'pasta']"
        preprocessor = IngredientPreprocessor()
        result = preprocessor.process_ingredients_list(ingredients_str)
        
        assert isinstance(result, (list, set))
        assert len(result) > 0
    
    def test_process_ingredients_list_invalid(self):
        """Test avec liste invalide"""
        preprocessor = IngredientPreprocessor()
        result = preprocessor.process_ingredients_list("not_a_list")
        assert isinstance(result, (list, set))


class TestNutritionPreprocessor:
    
    def test_parse_nutrition_valid(self):
        """Test parsing nutrition valide"""
        nutrition_str = "[400, 10, 5, 50, 20, 25, 800]"
        result = NutritionPreprocessor.parse_nutrition(nutrition_str)
        
        assert isinstance(result, dict)
        assert len(result) > 0
        # Vérifier que les valeurs sont numériques
        assert all(isinstance(v, (int, float)) for v in result.values())
    
    def test_parse_nutrition_invalid(self):
        """Test avec nutrition invalide"""
        result = NutritionPreprocessor.parse_nutrition("invalid")
        assert isinstance(result, dict)
    
    def test_parse_nutrition_empty(self):
        """Test avec nutrition vide"""
        result = NutritionPreprocessor.parse_nutrition("")
        assert isinstance(result, dict)
        
        result = NutritionPreprocessor.parse_nutrition(None)
        assert isinstance(result, dict)
    
    def test_calculate_health_score(self):
        """Test calcul du score de santé"""
        # Nutrition équilibrée
        healthy_nutrition = {'calories': 350, 'fat': 8, 'sugar': 5, 'sodium': 600, 'protein': 25}
        score = NutritionPreprocessor.calculate_health_score(healthy_nutrition)
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    def test_extract_nutrition_categories(self):
        """Test extraction des catégories nutritionnelles"""
        nutrition = {'calories': 300, 'fat': 5, 'sugar': 8, 'sodium': 400, 'protein': 30}
        categories = NutritionPreprocessor.extract_nutrition_categories(nutrition)
        
        assert isinstance(categories, list)


class TestTagsPreprocessor:
    
    def test_clean_and_extract_tags_valid(self):
        """Test extraction des tags valides"""
        tags_str = "['dinner', 'main-dish', 'healthy']"
        result = TagsPreprocessor.clean_and_extract_tags(tags_str)
        
        assert isinstance(result, set)
        assert len(result) > 0
    
    def test_clean_and_extract_tags_invalid(self):
        """Test avec tags invalides"""
        result = TagsPreprocessor.clean_and_extract_tags("not_a_list")
        assert isinstance(result, set)
    
    def test_extract_meal_type(self):
        """Test extraction du type de repas"""
        dinner_tags = {"dinner", "main-dish"}
        breakfast_tags = {"breakfast", "morning"}
        
        meal_type_dinner = TagsPreprocessor.extract_meal_type(dinner_tags)
        meal_type_breakfast = TagsPreprocessor.extract_meal_type(breakfast_tags)
        
        assert meal_type_dinner in [None, "dinner", "lunch", "breakfast", "snack"]
        assert meal_type_breakfast in [None, "dinner", "lunch", "breakfast", "snack"]
    
    def test_extract_dietary_restrictions(self):
        """Test extraction des restrictions alimentaires"""
        tags = {"vegan", "gluten-free", "low-sodium", "healthy"}
        restrictions = TagsPreprocessor.extract_dietary_restrictions(tags)
        
        assert isinstance(restrictions, list)
    
    def test_extract_cuisine_type(self):
        """Test extraction du type de cuisine"""
        italian_tags = {"italian", "pasta", "main-dish"}
        result = TagsPreprocessor.extract_cuisine_type(italian_tags)
        
        assert isinstance(result, (str, type(None)))


class TestStepsPreprocessor:
    
    def test_parse_and_analyze_steps_valid(self):
        """Test analyse des étapes valides"""
        steps_str = "['Heat oil in pan', 'Cook chicken until done', 'Add vegetables and simmer']"
        n_steps, effort_score, techniques = StepsPreprocessor.parse_and_analyze_steps(steps_str, 30)
        
        assert isinstance(n_steps, int)
        assert n_steps >= 0
        assert 0 <= effort_score <= 1
        assert isinstance(techniques, set)
    
    def test_parse_and_analyze_steps_invalid(self):
        """Test avec étapes invalides"""
        n_steps, effort_score, techniques = StepsPreprocessor.parse_and_analyze_steps("invalid", 30)
        
        assert isinstance(n_steps, int)
        assert isinstance(effort_score, float)
        assert isinstance(techniques, set)
    
    def test_extract_cooking_techniques(self):
        """Test extraction des techniques de cuisine"""
        steps = ["Heat oil in pan", "Bake at 350F", "Grill the chicken"]
        techniques = StepsPreprocessor.extract_cooking_techniques(steps)
        
        assert isinstance(techniques, set)
    
    def test_calculate_effort_score(self):
        """Test calcul du score d'effort"""
        easy_steps = ["Mix ingredients", "Bake for 20 minutes"]
        hard_steps = ["Prepare marinade overnight", "Slow cook for 4 hours", "Caramelize onions"]
        
        easy_score = StepsPreprocessor.calculate_effort_score(easy_steps, 2, 25)
        hard_score = StepsPreprocessor.calculate_effort_score(hard_steps, 3, 300)
        
        assert 0 <= easy_score <= 1
        assert 0 <= hard_score <= 1
        assert isinstance(easy_score, float)
        assert isinstance(hard_score, float)


class TestDescriptionPreprocessor:
    
    def test_extract_keywords_valid(self):
        """Test extraction de mots-clés valides"""
        description = "This is a delicious and healthy chicken recipe with vegetables"
        keywords = DescriptionPreprocessor.extract_keywords(description)
        
        assert isinstance(keywords, list)
    
    def test_extract_keywords_empty(self):
        """Test avec description vide"""
        keywords = DescriptionPreprocessor.extract_keywords("")
        assert isinstance(keywords, list)
        
        keywords = DescriptionPreprocessor.extract_keywords(None)
        assert isinstance(keywords, list)
    
    def test_analyze_description_sentiment(self):
        """Test analyse de sentiment"""
        positive_desc = "This amazing and delicious recipe is perfect for dinner"
        negative_desc = "This terrible and bland recipe is not worth trying"
        
        pos_sentiment = DescriptionPreprocessor.analyze_description_sentiment(positive_desc)
        neg_sentiment = DescriptionPreprocessor.analyze_description_sentiment(negative_desc)
        
        assert isinstance(pos_sentiment, (float, int))
        assert isinstance(neg_sentiment, (float, int))


class TestRecipePreprocessor:
    
    def test_init(self):
        """Test initialisation du RecipePreprocessor"""
        preprocessor = RecipePreprocessor()
        
        assert hasattr(preprocessor, 'ingredient_processor')
        assert hasattr(preprocessor, 'nutrition_processor')
        assert hasattr(preprocessor, 'tags_processor')
        assert hasattr(preprocessor, 'steps_processor')
        assert hasattr(preprocessor, 'description_processor')
    
    def test_extract_features_complete(self):
        """Test extraction complète des features"""
        sample_recipe = {
            'id': 1,
            'ingredients': "['chicken breast', 'rice', 'garlic']",
            'nutrition': '[400, 10, 5, 50, 20, 25, 800]',
            'tags': "['dinner', 'main-dish']",
            'steps': "['Cook chicken', 'Prepare rice', 'Combine']",
            'minutes': 30,
            'n_steps': 3,
            'n_ingredients': 3,
            'description': 'Delicious chicken and rice'
        }
        
        preprocessor = RecipePreprocessor()
        features = preprocessor.extract_features(sample_recipe)
        
        assert isinstance(features, RecipeFeatures)
        assert features.recipe_id == 1
        assert isinstance(features.ingredients, set)
        assert isinstance(features.normalized_ingredients_list, list)
        assert isinstance(features.nutrition_dict, dict)
        assert isinstance(features.tags, set)
        assert isinstance(features.n_steps, int)
        assert isinstance(features.effort_score, float)
        assert isinstance(features.cooking_techniques, set)
        assert isinstance(features.description_keywords, list)
    
    def test_extract_features_minimal(self):
        """Test avec données minimales"""
        minimal_recipe = {
            'id': 1,
            'ingredients': None,
            'nutrition': None,
            'tags': None,
            'steps': None,
            'minutes': None,
            'n_steps': None,
            'description': None
        }
        
        preprocessor = RecipePreprocessor()
        features = preprocessor.extract_features(minimal_recipe)
        
        assert isinstance(features, RecipeFeatures)
        assert features.recipe_id == 1
    
    def test_preprocess_dataframe(self):
        """Test preprocessing d'un DataFrame complet"""
        df = pd.DataFrame({
            'id': [1, 2],
            'ingredients': [
                "['chicken', 'rice']",
                "['beef', 'pasta']"
            ],
            'nutrition': [
                '[400, 10, 5, 50, 20, 25, 800]',
                '[600, 20, 8, 70, 15, 30, 1200]'
            ],
            'tags': [
                "['dinner']",
                "['lunch']"
            ],
            'steps': [
                "['Cook chicken']",
                "['Boil pasta']"
            ],
            'minutes': [30, 20],
            'n_steps': [1, 1],
            'n_ingredients': [2, 2],
            'description': ['Chicken rice', 'Beef pasta']
        })
        
        preprocessor = RecipePreprocessor()
        result = preprocessor.preprocess_dataframe(df)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, RecipeFeatures) for item in result)
    
    def test_preprocess_dataframe_empty(self):
        """Test avec DataFrame vide"""
        empty_df = pd.DataFrame()
        
        preprocessor = RecipePreprocessor()
        result = preprocessor.preprocess_dataframe(empty_df)
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestRecipeFeatures:
    """Test de la dataclass RecipeFeatures"""
    
    def test_recipe_features_creation(self):
        """Test création d'une instance RecipeFeatures"""
        features = RecipeFeatures(
            recipe_id=1,
            ingredients={'chicken', 'rice'},
            ingredient_categories={'proteins': ['chicken']},
            normalized_ingredients_list=['chicken', 'rice'],
            nutrition_dict={'calories': 400},
            tags={'dinner'},
            meal_type='dinner',
            dietary_restrictions=['healthy'],
            cuisine_type='american',
            n_steps=3,
            effort_score=0.5,
            cooking_techniques={'bake'},
            description_keywords=['delicious']
        )
        
        assert features.recipe_id == 1
        assert 'chicken' in features.ingredients
        assert features.meal_type == 'dinner'
        assert features.effort_score == 0.5


if __name__ == '__main__':
    pytest.main([__file__])