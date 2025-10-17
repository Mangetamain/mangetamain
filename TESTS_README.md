# Tests - MangeTaMain

Ce document explique comment lancer et utiliser les tests unitaires pour l'application MangeTaMain.

## 🧪 Configuration des Tests

Le projet utilise une infrastructure de tests complète avec :
- **pytest** pour les tests unitaires
- **coverage.py** pour la couverture de code
- **Docker** pour l'environnement de test isolé
- **Mocking** pour les dépendances externes

## 🚀 Lancement des Tests

### Option 1: Script de test automatisé (Recommandé)

Le script `run-tests.sh` fournit une interface simple pour exécuter les tests :

```bash
# Lancer tous les tests unitaires
./run-tests.sh -u

# Lancer tous les tests (unitaires + intégration)
./run-tests.sh

# Mode développement interactif
./run-tests.sh -d

# Générer seulement le rapport de couverture
./run-tests.sh -c

# Forcer la reconstruction de l'image Docker
./run-tests.sh -u --build

# Mode verbose
./run-tests.sh -u --verbose

# Nettoyer l'environnement de test
./run-tests.sh --clean
```

### Option 2: Docker Compose direct

```bash
# Démarrer les services de test
docker-compose --profile testing up -d preprocessing

# Exécuter les tests unitaires
docker-compose --profile testing run --rm tests poetry run pytest tests/unit/

# Exécuter avec couverture
docker-compose --profile testing run --rm tests poetry run pytest tests/unit/ --cov=src --cov-report=html

# Mode développement interactif
docker-compose --profile testing run --rm tests-dev
```

### Option 3: Développement local (si Poetry installé)

```bash
# Installer les dépendances de développement
poetry install --with dev

# Lancer les tests unitaires
poetry run pytest tests/unit/

# Avec couverture
poetry run pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing
```

## 📊 Rapports de Test

### Couverture de Code

Les rapports de couverture sont générés automatiquement :
- **Rapport HTML** : Accessible dans le volume Docker `test_reports/htmlcov/index.html`
- **Rapport XML** : Pour intégration CI/CD dans `test_reports/coverage.xml`
- **Rapport Terminal** : Affiché directement dans la console

```bash
# Voir les rapports générés
docker-compose --profile testing exec tests ls -la /app/test-reports/
```

### Métriques Actuelles

- ✅ **15 tests** passent avec succès
- 📈 **22% de couverture** de code globale
- 🎯 Tests couvrent les modules principaux :
  - `RecommendationEngine` (69% couvert)
  - `UIComponents` (28% couvert)
  - `DataManager` (tests complets)

## 🏗️ Structure des Tests

```
tests/
├── unit/                          # Tests unitaires
│   ├── test_recommendation_engine.py  # Tests moteur de recommandation
│   ├── test_ui_components.py         # Tests composants UI
│   └── test_data_manager.py          # Tests gestionnaire de données
└── integration/                   # Tests d'intégration
    ├── test_app_integration.py       # Tests intégration app
    └── test_full_workflow.py         # Tests workflow complet
```

## 🛠️ Tests Disponibles

### Tests Unitaires
- **RecommendationEngine** : Calcul des scores composites, normalisation
- **UIComponents** : Affichage des composants Streamlit
- **DataManager** : Chargement et gestion des données

### Tests d'Intégration
- **Workflow complet** : Pipeline de recommandation end-to-end
- **Intégration app** : Tests des interactions entre composants

## 🔧 Développement des Tests

### Ajouter un nouveau test

1. Créer le fichier dans `tests/unit/` ou `tests/integration/`
2. Utiliser pytest et les fixtures disponibles
3. Mocker les dépendances externes (Streamlit, pandas, etc.)

Exemple :
```python
import pytest
from unittest.mock import patch, Mock
from src.engines.recommendation_engine import RecommendationEngine

def test_nouvelle_fonctionnalite():
    with patch('streamlit.cache_data'):
        result = RecommendationEngine.nouvelle_methode()
        assert result is not None
```

### Fixtures Disponibles

- `sample_recipe` : Recette d'exemple
- `sample_recipes_df` : DataFrame de recettes de test
- `sample_interactions_df` : DataFrame d'interactions utilisateur

## 🐳 Configuration Docker

Les tests utilisent des services Docker dédiés :

- **tests** : Service principal pour l'exécution des tests
- **tests-dev** : Service interactif pour le développement
- **preprocessing** : Service de préparation des données

### Variables d'environnement

```yaml
POETRY_CACHE_DIR: /tmp/poetry_cache
PYTHONPATH: /app:/preprocessing
```

## ⚡ Commandes Rapides

```bash
# Test rapide
./run-tests.sh -u

# Développement avec hot-reload
./run-tests.sh -d

# Nettoyer après tests
./run-tests.sh --clean

# Voir l'aide
./run-tests.sh --help
```

## 🚨 Dépannage

### Problèmes Courants

1. **Tests ne démarrent pas** :
   ```bash
   # Vérifier Docker
   docker --version
   docker-compose --version
   
   # Nettoyer l'environnement
   ./run-tests.sh --clean
   ```

2. **Erreurs de dépendances** :
   ```bash
   # Forcer la reconstruction
   ./run-tests.sh -u --build
   ```

3. **Problèmes de volumes** :
   ```bash
   # Nettoyer les volumes Docker
   docker volume prune
   ```

### Logs de Debug

```bash
# Voir les logs du service de test
docker-compose --profile testing logs tests

# Mode verbose
./run-tests.sh -u --verbose
```

## 📋 Prochaines Étapes

- [ ] Améliorer la couverture de code (objectif : 80%)
- [ ] Ajouter des tests de performance
- [ ] Intégration CI/CD avec GitHub Actions
- [ ] Tests de régression automatisés

---

**💡 Conseil** : Utilisez toujours `./run-tests.sh -u` pour un test rapide avant de commiter vos changements !