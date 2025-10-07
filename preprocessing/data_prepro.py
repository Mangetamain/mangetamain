import pandas as pd
import numpy as np
import ast 
import string
import re
import logging
from dataclasses import dataclass
from typing import List, Set, Dict, Optional
from collections import defaultdict

# configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RecipeFeatures:
    recipe_id: int
    ingredients: Set[str]
    ingredient_categories: Dict[str, List[str]]
    nutrition_dict: Dict[str, float]
    tags: Set[str]
    meal_type: Optional[str]
    dietary_restrictions: List[str]
    cuisine_type: Optional[str]
    n_steps: int
    effort_score: float  # Score d'effort (0-1)
    cooking_techniques: Set[str]
    description_keywords: List[str]

class IngredientPreprocessor:
    "prétraitement des ingrédients avec catégorisation et normalisation via ingr_map.pkl"
    CATEGORIES = {
        'proteins': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 
                     'turkey', 'lamb', 'egg', 'tofu', 'tempeh'],
        'dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'sour cream'],
        'vegetables': ['tomato', 'onion', 'garlic', 'carrot', 'potato', 'broccoli',
                       'spinach', 'pepper', 'mushroom', 'lettuce', 'cucumber'],
        'fruits': ['apple', 'banana', 'orange', 'lemon', 'strawberry', 'blueberry'],
        'grains': ['flour', 'rice', 'pasta', 'bread', 'oat', 'quinoa', 'wheat'],
        'spices': ['salt', 'pepper', 'cumin', 'paprika', 'cinnamon', 'basil', 
                   'oregano', 'thyme', 'rosemary'],
        'oils': ['olive oil', 'vegetable oil', 'coconut oil', 'butter'],
        'sweeteners': ['sugar', 'honey', 'maple syrup', 'brown sugar']
    }
    # MESURES A RETIRER
    MEASURES = r'\b(cup|tablespoon|teaspoon|pound|ounce|oz|lb|tsp|tbsp|ml|l|g|kg|pinch|dash)\b'
    
    def __init__(self, ingr_map_path: Optional[str] = None):
        self.ingredient_to_category = {}
        for category, ingredients in self.CATEGORIES.items():
            for ing in ingredients:
                self.ingredient_to_category[ing] = category
        self.ingr_map = None
        self.raw_to_normalized = {}
        
        if ingr_map_path:
            self._load_ingredient_map(ingr_map_path)
    
    def _load_ingredient_map(self, ingr_map_path: str):
        try:
            # Charger le fichier CSV au lieu du fichier PKL
            self.ingr_map = pd.read_csv(ingr_map_path)
            for _, row in self.ingr_map.iterrows():
                raw = row['raw_ingr'].lower().strip()
                normalized = row.get('replaced', row.get('normalized', raw))
                self.raw_to_normalized[raw] = normalized.lower().strip()
            logger.info("Ingredient map loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading ingredient map: {e}")
            logger.warning("Proceeding without ingredient normalization.")
            
    def normalize_ingredient(self, raw_ingredient:str) -> str:
        if self.ingr_map is not None:
            # Première tentative: correspondance exacte
            raw_lower = raw_ingredient.lower().strip()
            if raw_lower in self.raw_to_normalized:
                return self.raw_to_normalized[raw_lower]
            
            # Deuxième tentative: nettoyer d'abord puis chercher dans la carte
            pre_cleaned = self._manual_clean(raw_ingredient)
            if pre_cleaned in self.raw_to_normalized:
                return self.raw_to_normalized[pre_cleaned]
        
        # Fallback: nettoyage manuel seulement
        return self._manual_clean(raw_ingredient)
    
    def _manual_clean(self, ingredient: str) -> str:
        # nettoyage manual si ingr_map non disponible
        ing = ingredient.lower().strip()
        ing = re.sub(r'\d+\.?\d*\s*/?\s*\d*', '', ing)  # retirer les quantités
        ing = re.sub(self.MEASURES, '', ing, flags=re.IGNORECASE)  # retirer les mesures
        ing = re.sub(r'[^\w\s-]', '', ing)  # retirer la ponctuation    
        ing = re.sub(r'\b(fresh|dried|frozen|chopped|diced|sliced|minced|ground)\b', 
                    '', ing, flags=re.IGNORECASE)
        ing = ' '.join(ing.split())  # retirer les espaces multiples
        return ing
    
    def parse_and_clean(self, ingredients_str: str)-> List[str]:
        try: 
            ingredients_list = ast.literal_eval(ingredients_str)
            cleaned = []
            for raw_ing in ingredients_list:
                # Normalisation via ingr_map (ou fallback manuel)
                normalized_ing = self.normalize_ingredient(raw_ing)
                
                if normalized_ing and len(normalized_ing) > 2:
                    cleaned.append(normalized_ing)
            # Dédupliquer (car plusieurs variantes peuvent donner le même normalisé)
            return list(set(cleaned))
        except (ValueError, SyntaxError) as e:
            logger.error(f"Erreur parsing ingredients: {e}")
            return []
        
    def categorize(self, ingredients: List[str]) -> Dict[str, List[str]]:
        categorized = defaultdict(list)
        for ing in ingredients:
            category_found = False
            # Chercher dans quelle catégorie se trouve l'ingrédient
            for base_ing, category in self.ingredient_to_category.items():
                if base_ing in ing:
                    categorized[category].append(ing)
                    category_found = True
                    break
            if not category_found:
                categorized['other'].append(ing)
        return dict(categorized)

class NutritionPreprocessor:
    NUTRITION_FIELDS = ['calories', 'fat','total_fat', 'carbohydrates', 
                        'sugar', 'protein', 'sodium']
    
    def parse_nutrition(self, nutrition_str: str) -> Dict[str, float]:
        """
        Parse la chaîne de nutrition en dictionnaire avec valeurs float. 
        "[calories, fat, sugar, ...]" -> {'calories': val, 'fat': val, ...}
        """
        try:
            values = ast.literal_eval(nutrition_str)
            # Vérifier que nous avons le bon nombre de valeurs
            if len(values) != len(NutritionPreprocessor.NUTRITION_FIELDS):
                logger.warning(f"Nombre incorrect de valeurs nutritionnelles: {len(values)}")
                return {}
            nutrition_dict = dict(zip(NutritionPreprocessor.NUTRITION_FIELDS, 
                                     [float(v) for v in values]))
            return nutrition_dict
        except (ValueError, SyntaxError) as e:
            logger.error(f"Erreur parsing nutrition: {e}")
            return {}
    @staticmethod
    def compute_health_score(nutrition: Dict[str,float])->float:
        """construction d'un score de nutrition simple (0-1)"""
        if not nutrition:
            return 0.5  # score neutre si pas de données
        # Calculer un score basé sur les nutriments
        penalties = 0.0
        penalties += max(0, (nutrition.get('calories', 0) - 600) / 2000)
        penalties += max(0, (nutrition.get('sugar', 0) - 50) / 200)
        penalties += max(0, (nutrition.get('sodium', 0) - 1000) / 4000)

        protein_bonus = min(nutrition.get('protein', 0) / 50, 0.3)
        score = max(0, min(1, 1-penalties + protein_bonus))
        return round(score, 2)
class TagsPreprocessor:
    """extraction de l'information structurées a partir des tags"""
    MEAL_TYPES= {'breakfast': ['breakfast', 'brunch'],
                 'lunch': ['lunch', 'main-dish'],
                 'dinner': ['dinner', 'main-dish'],
                 'snack': ['snacks', 'appetizers']}
    DIETARY = {
        'vegetarian': ['vegetarian', 'vegan'],
        'vegan': ['vegan'],
        'low-carb': ['low-carb', 'low-carbohydrate'],
        'gluten-free': ['gluten-free'],
        'dairy-free': ['dairy-free', 'lactose-free'],
        'healthy': ['healthy', 'low-fat', 'low-sodium', 'low-calorie']
    }
    CUISINES = [
        'mexican', 'italian', 'chinese', 'indian', 'french', 'thai',
        'japanese', 'greek', 'spanish', 'american', 'mediterranean'
    ]
    @staticmethod
    def parse_tags(tags_str:str) -> Set[str]:
        """nettoyer les tags"""
        try: 
            tags = ast.literal_eval(tags_str)
            return { tag.lower().strip() for tag in tags }
        except (ValueError, SyntaxError) as e:
            logger.error(f"Erreur parsing tags: {e}")
            return set()
    @classmethod
    def extract_meal_type(cls, tags:Set[str]) -> Optional[str]:
        for meal_type, keywords in cls.MEAL_TYPES.items():
            if any(keyword in tags for keyword in keywords):
                return meal_type
        return None
    @classmethod 
    def extract_dietary_restriction(cls, tags:Set[str])-> List[str]:
        restrictions = []
        for restriction, keywords in cls.DIETARY.items():
            if any(keyword in tags for keyword in keywords):
                restrictions.append(restriction)
        return restrictions
    @classmethod
    def extract_cuisine_type(cls, tags:Set[str])-> Optional[str]:
        for cuisine in cls.CUISINES:
            if cuisine in tags:
                return cuisine
        return None
    @staticmethod
    def extract_time_constrained(tags:Set[str])-> bool:
        time_patterns = {
            '15-minutes-or-less': 15,
            '30-minutes-or-less': 30,
            '60-minutes-or-less': 60,
            '4-hours-or-less': 240
        }
        for pattern, minutes in time_patterns.items():
            if pattern in tags:
                return minutes
        return None