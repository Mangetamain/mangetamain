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

## 🏆 Succès de Couverture

### Amélioration Spectaculaire
- **Avant** : 53% de couverture globale
- **Après** : 86% de couverture globale (+33 points !)
- **Résultat** : Objectif 80% largement dépassé

### Détail par Module
| Module | Couverture Avant | Couverture Après | Amélioration |
|--------|------------------|------------------|--------------|
| `core/app.py` | 63% | 99% | +36 points ✨ |
| `main.py` | 0% | 100% | +100 points 🚀 |
| `config.py` | 0% | 100% | +100 points 🚀 |
| `styles.py` | 80% | 100% | +20 points ⭐ |
| `recommendation_engine.py` | 74% | 91% | +17 points 📈 |
| `components.py` | ~70% | 91% | +21 points 📊 |
| `data_manager.py` | ~85% | 100% | +15 points 💯 |

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

- ✅ **121/122 tests** passent avec succès (99.2% de réussite)
- 📈 **86% de couverture** de code globale (objectif dépassé !)
- 🎯 Tests couvrent exhaustivement tous les modules :
  - `core/app.py` (99% couvert - quasi-complet)
  - `main.py` (100% couvert - complet)
  - `config.py` (100% couvert - complet)  
  - `styles.py` (100% couvert - complet)
  - `RecommendationEngine` (91% couvert - excellent)
  - `UIComponents` (91% couvert - excellent)
  - `DataManager` (100% couvert - complet)

## 🏗️ Structure des Tests

```
tests/
├── unit/                                      # Tests unitaires (suite exhaustive)
│   ├── test_config_module.py                 # Tests module configuration
│   ├── test_config.py                        # Tests configuration complète (100%)
│   ├── test_core_app_targeted.py            # Tests ciblés core/app.py (99%)
│   ├── test_core_app.py                     # Tests principaux core/app.py
│   ├── test_data_manager.py                 # Tests gestionnaire données (100%)
│   ├── test_final_coverage.py              # Tests couverture finale
│   ├── test_main_module.py                 # Tests module principal
│   ├── test_recommendation_engine_additional.py  # Tests moteur (complément)
│   ├── test_recommendation_engine_extended.py   # Tests moteur (étendu)
│   ├── test_recommendation_engine.py       # Tests moteur recommandation (91%)
│   ├── test_src_main.py                    # Tests src/main.py (100%)
│   ├── test_styles.py                      # Tests gestionnaire styles (100%)
│   ├── test_ui_components_extended.py      # Tests UI composants (étendu)
│   ├── test_ui_components.py               # Tests composants UI (91%)
│   ├── test_ui_final.py                    # Tests UI finaux
│   └── test_ui_intensive.py                # Tests UI intensifs
└── integration/                            # Tests d'intégration
    ├── test_app_integration.py             # Tests intégration app
    └── test_full_workflow.py               # Tests workflow complet
```

## 🛠️ Tests Disponibles

### Tests Unitaires (Suite Exhaustive)
- **Configuration** : Tests complets des structures de config (100% couverture)
- **Application Principale** : Tests ciblés pour toutes les branches logiques (99% couverture)
- **RecommendationEngine** : Calcul scores composites, normalisation, gestion erreurs (91% couverture)
- **UIComponents** : Tous composants Streamlit avec mocking avancé (91% couverture)
- **DataManager** : Chargement, validation, gestion cache (100% couverture)
- **StyleManager** : CSS, thèmes, styles responsifs (100% couverture)
- **Main Module** : Point d'entrée et orchestration (100% couverture)

### Tests d'Intégration
- **Workflow complet** : Pipeline de recommandation end-to-end
- **Intégration app** : Tests des interactions entre composants

### Stratégies de Test
- **Mocking extensif** : Streamlit, pandas, fichiers système
- **Tests de branches** : Couverture de tous les chemins logiques
- **Tests d'erreurs** : Gestion robuste des cas d'échec
- **Tests de performance** : Validation des temps de réponse

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

# Tests de performance
./run-tests.sh -p

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

- [x] ~~Améliorer la couverture de code (objectif : 80%)~~ **✅ ACCOMPLI : 86% atteint !**
- [x] ~~Ajouter des tests de performance~~ **✅ ACCOMPLI : Support via -p flag**
- [x] ~~Intégration CI/CD avec GitHub Actions~~ **✅ ACCOMPLI : Workflows configurés**
- [ ] Tests de régression automatisés
- [ ] Tests end-to-end avec Selenium
- [ ] Benchmarking des performances de recommandation
- [ ] Tests de charge et de stress

---

**💡 Conseil** : Utilisez toujours `./run-tests.sh -u` pour un test rapide avant de commiter vos changements !