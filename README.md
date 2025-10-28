# 🍽️ MangeTaMain - Système de Recommandation de Recettes

[![Tests](https://img.shields.io/badge/tests-80%25%20coverage-green.svg)](./tests/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](./docker-compose.yml)
[![Streamlit](https://img.shields.io/badge/streamlit-app-FF4B4B.svg)](./streamlit-poetry-docker/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](./pyproject.toml)

Un système intelligent de recommandation de recettes basé sur l'IA, utilisant des algorithmes d'apprentissage automatique hybrides pour suggérer des recettes personnalisées selon les préférences et ingrédients de l'utilisateur.

## ✨ Fonctionnalités

- 🤖 **IA Hybride** : Combinaison Jaccard + Cosine + Rating + Popularité
- 🥗 **231,629 recettes** traitées et optimisées
- 🔍 **Recherche intelligente** par ingrédients disponibles  
- 🎯 **Préférences personnalisées** : type de repas, restrictions alimentaires, niveau d'effort
- 📊 **Scoring nutritionnel** automatique avec analyse de santé
- 🚀 **Interface moderne** avec Streamlit
- 🐳 **Déploiement Docker** multi-plateforme (AMD64 + ARM64)
- 🧪 **Suite de tests complète** avec 80%+ de couverture

## 🚀 Démarrage Rapide

### Option 1: Données Pré-construites (Recommandé)
```bash
# Démarrage instantané avec données optimisées
docker-compose --profile use-prebuilt up -d
```
- ✅ Données préprocessées depuis Docker Hub (`andranik777/mangetamain-data:latest`)
- ✅ Démarrage instantané, aucun preprocessing
- ✅ Application disponible sur http://localhost:8501
- ✅ ~1.2GB téléchargés une seule fois

### Option 2: Reconstruction Locale des Données
```bash
# Processing local des données brutes (~5-10 minutes)
docker-compose --profile rebuild-data up -d
```
- 🔄 Traitement local des données Kaggle
- ⏱️ 5-10 minutes de preprocessing initial
- 📊 231,629 recettes analysées et optimisées

### Option 3: Mode Développement
```bash
# Environnement de développement avec hot-reload
docker-compose --profile development up -d
```

## 🧪 Tests et Qualité

### Exécution Rapide des Tests
```bash
# Script unifié avec menu interactif
./run_tests.sh

# Ou directement avec Python
python run_tests.py
```

### Options de Test Disponibles
```bash
# Tests spécifiques
./run_tests.sh -u                 # Tests unitaires uniquement
./run_tests.sh -i                 # Tests d'intégration uniquement
./run_tests.sh -p                 # Tests de performance
./run_tests.sh -c                 # Rapport de couverture uniquement

# Mode développement
./run_tests.sh -d                 # Mode développement interactif
./run_tests.sh --clean           # Nettoyer environnement Docker
```

### Couverture Actuelle
| Module | Couverture | Tests |
|--------|------------|-------|
| `data_load.py` | 85% | ✅ 15+ tests |
| `data_prepro.py` | 80% | ✅ 40+ tests |
| `reco_score.py` | 85% | ✅ 25+ tests |
| `app.py` | 75% | ✅ 20+ tests |
| **Total** | **80%+** | **100+ tests** |

## 🏗️ Architecture

### Structure du Projet
```
mangetamain/
├── preprocessing/              # Pipeline de preprocessing
│   ├── data_load.py           # Chargement données Kaggle
│   ├── data_prepro.py         # Preprocessing avancé
│   └── reco_score.py          # Moteur de recommandation
├── streamlit-poetry-docker/   # Interface utilisateur
│   └── app.py                 # Application Streamlit
├── tests/                     # Suite de tests complète
│   ├── unit/                  # Tests unitaires
│   ├── integration/           # Tests d'intégration
│   └── performance/           # Tests de performance
├── docker-compose.yml         # Orchestration multi-services
└── docs/                      # Documentation technique
```

### Pipeline de Données
1. **Extraction** : Kaggle API → Raw Data (CSV)
2. **Transformation** : 
   - Normalisation des ingrédients
   - Analyse nutritionnelle
   - Extraction des techniques de cuisson
   - Classification des types de repas
3. **Chargement** : Features optimisées → Pickle
4. **Scoring** : Algorithmes ML hybrides
5. **Interface** : Streamlit avec préférences utilisateur

## 🤖 Algorithmes de Recommandation

### Scoring Composite
Le système utilise 4 algorithmes combinés :

```python
score_total = (
    jaccard_weight * jaccard_similarity +      # Similarité des ingrédients
    cosine_weight * cosine_similarity +        # Similarité TF-IDF  
    rating_weight * nutrition_rating +         # Score nutritionnel
    popularity_weight * popularity_score       # Score de popularité
)
```

### Fonctionnalités Avancées
- **Jaccard Similarity** : Correspondance exacte des ingrédients
- **Cosine Similarity + TF-IDF** : Analyse sémantique des ingrédients
- **Nutrition Scoring** : Évaluation automatique de la valeur nutritionnelle
- **Popularity Metrics** : Scoring basé sur les tags et la complexité
- **User Preferences** : Filtrage par type de repas, restrictions, effort

## 📊 Données et Performance

### Dataset
- **Source** : Kaggle Food.com Recipes
- **Volume** : 231,629 recettes traitées
- **Features extraites** : 15+ attributs par recette
- **Optimisations** : Normalisation, catégorisation, indexation

### Métriques de Performance
- **Preprocessing** : 30ms par recette
- **Recommandation** : < 2s pour 100 recettes  
- **Mémoire** : < 500MB pour 1000 recettes
- **Scalabilité** : Support pour millions de recettes

## 🐳 Docker et Déploiement

### Profiles Docker Compose
```bash
# Production avec données pré-construites
docker-compose --profile use-prebuilt up -d

# Développement avec reconstruction
docker-compose --profile rebuild-data up -d  

# Tests automatisés
docker-compose --profile testing up -d

# Développement interactif
docker-compose --profile development up -d
```

### Compatibilité Multi-plateforme
- ✅ **Linux AMD64** : Serveurs de production
- ✅ **macOS ARM64** : Développement Apple Silicon
- ✅ **Windows AMD64** : Environnements Windows
- ✅ **CI/CD** : GitHub Actions, Jenkins

## 🔧 Développement

### Configuration de l'Environnement
```bash
# Installation des dépendances
poetry install --with dev

# Variables d'environnement
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_api_key"

# Développement local
cd preprocessing
poetry run python data_prepro.py

cd ../streamlit-poetry-docker
poetry run streamlit run app.py
```

### Scripts de Développement
```bash
# Tests et développement
./run_tests.sh -d                 # Mode développement interactif
./run_tests.sh -u -v             # Tests unitaires en mode verbose
./run_tests.sh --build           # Forcer reconstruction images
./run_tests.sh --clean           # Nettoyer environnement Docker
```

## 📚 Documentation

### Guides Disponibles
- 📖 **[Architecture](./docs/ARCHITECTURE.md)** : Conception technique détaillée
- 🐳 **[Docker Usage](./docs/DOCKER_VOLUME_USAGE.md)** : Guide des volumes et déploiement
- 🧪 **[Tests Guide](./TEST_GUIDE.md)** : Documentation complète des tests
- 🚀 **[API Reference](./docs/API.md)** : Documentation des fonctions

### Exemples d'Usage
```python
# Utilisation programmatique
from preprocessing.reco_score import RecipeScorer
from preprocessing.data_prepro import RecipePreprocessor

# Charger les données
scorer = RecipeScorer.load_from_pickle("processed_data.pkl")

# Obtenir des recommandations
recommendations = scorer.recommend(
    user_ingredients=['chicken', 'rice', 'garlic'],
    user_preferences={
        'meal_type': 'dinner',
        'max_effort': 0.5,
        'dietary_restrictions': ['healthy']
    },
    top_k=5
)
```

## 🤝 Contribution

### Workflow de Contribution
1. 🍴 Fork le repository
2. 🌿 Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. 🧪 Ajouter des tests pour les nouvelles fonctionnalités
4. ✅ Vérifier que tous les tests passent (`./run_tests.sh`)
5. 📝 Commit les changes (`git commit -m 'Add amazing feature'`)
6. 📤 Push vers la branche (`git push origin feature/amazing-feature`)
7. 🔄 Ouvrir une Pull Request

### Standards de Qualité
- ✅ Couverture de tests > 80%
- ✅ Type hints Python
- ✅ Documentation des fonctions
- ✅ Tests de performance inclus
- ✅ Compatibilité multi-plateforme

## 📈 Roadmap

### Version Actuelle (v1.0)
- ✅ Système de recommandation hybride
- ✅ Interface Streamlit complète
- ✅ Déploiement Docker multi-plateforme
- ✅ Suite de tests avec 80%+ couverture

### Prochaines Versions
- 🔄 **v1.1** : API REST avec FastAPI
- 🔄 **v1.2** : Système de ratings utilisateur
- 🔄 **v1.3** : Intégration base de données PostgreSQL
- 🔄 **v2.0** : Modèles deep learning avec transformers

## 📞 Support

### Problèmes Courants
1. **Erreur de mémoire** : Réduire la taille du dataset ou augmenter la RAM Docker
2. **Timeout Kaggle** : Vérifier les credentials dans `.env`
3. **Port 8501 occupé** : Changer le port dans `docker-compose.yml`

### Obtenir de l'Aide
- 🐛 **Issues** : [GitHub Issues](https://github.com/Mangetamain/mangetamain/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/Mangetamain/mangetamain/discussions)
- 📧 **Contact** : team@mangetamain.com

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](./LICENSE) pour plus de détails.

---

<div align="center">

**🍽️ MangeTaMain - Découvrez votre prochaine recette favorite !**

[Demo](http://localhost:8501) • [Documentation](./docs/) • [Tests](./tests/) • [Docker Hub](https://hub.docker.com/r/andranik777/mangetamain-data)

</div>