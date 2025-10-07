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
            import pickle
            with open(ingr_map_path, 'rb') as f:
                self.ingr_map = pickle.load(f)
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
            # chercher dans la mapping
            raw_lower = raw_ingredient.lower().strip()
            if raw_lower in self.raw_to_normalized:
                return self.raw_to_normalized[raw_lower]
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

