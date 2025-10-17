"""
Configuration générale de l'application MangeTaMain
"""

# Chemins des données
DATA_PATHS = {
    "recipes": "/shared_data/recipes_processed.pkl",
    "interactions": "/shared_data/interactions.pkl"
}

# Configuration du cache Streamlit
CACHE_CONFIG = {
    "data_ttl": 3600,  # 1 heure
    "recommendations_ttl": 1800  # 30 minutes
}

# Configuration du moteur de recommandations
RECOMMENDATION_CONFIG = {
    "alpha": 0.5,
    "beta": 0.3,
    "gamma": 0.2,
    "max_ingredients_display": 8
}

# Configuration de l'interface
UI_CONFIG = {
    "max_recommendations": 20,
    "default_recommendations": 8,
    "description_max_length": 300,
    "time_options": [None, 15, 30, 45, 60, 90, 120, 180]
}

# Messages de l'application
MESSAGES = {
    "data_not_found": "❌ Données preprocessées non trouvées. Exécutez d'abord le preprocessing.",
    "data_loaded": "✅ Données chargées: {recipes_count:,} recettes avec {interactions_count:,} interactions",
    "loading_data": "⚡ Chargement des données preprocessées...",
    "generating_recommendations": "🔄 Génération des recommandations personnalisées...",
    "no_recommendations": "❌ Aucune recommandation trouvée avec ces critères",
    "no_ingredients": "⚠️ Veuillez entrer au moins un ingrédient",
    "recommendation_tip": "💡 Essayez avec des ingrédients plus communs ou supprimez la limite de temps"
}