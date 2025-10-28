# 🧪 Guide Unifié des Tests - MangeTaMain

## 🎯 Vue d'ensemble

Ce guide présente le système de tests unifié de MangeTaMain, conçu pour offrir une expérience cohérente sur tous les environnements (Docker, Python direct, Windows, Linux, macOS).

### ✨ Fonctionnalités du système de tests

- 🚀 **Script unifié** : Un seul point d'entrée pour tous les tests
- 🐳 **Docker + Python** : Support automatique Docker Compose et Python direct
- 🌍 **Multi-plateforme** : Windows, Linux, macOS avec auto-détection
- 📊 **Couverture 80%+** : Suite complète avec rapports détaillés
- 🔧 **Mode développement** : Environnement interactif pour debugging
- 🧹 **Nettoyage automatique** : Gestion propre des ressources Docker

## 🚀 Utilisation Rapide

### Commande Simple
```bash
# Auto-détection de l'environnement optimal
./run_tests_unified.py

# Ou directement avec Python
python run_tests_unified.py
```

### Tests Spécifiques
```bash
# Tests unitaires seulement
./run_tests_unified.py -u

# Tests d'intégration seulement  
./run_tests_unified.py -i

# Tests de performance seulement
./run_tests_unified.py -p

# Vérification couverture existante
./run_tests_unified.py -c
```

### Modes Avancés
```bash
# Mode développement interactif (Docker)
./run_tests_unified.py -d

# Forcer utilisation Docker
./run_tests_unified.py --docker

# Forcer utilisation Python direct
./run_tests_unified.py --python

# Tests avec reconstruction des images
./run_tests_unified.py -u -b

# Mode verbose avec marqueurs
./run_tests_unified.py -v -m "unit and not slow"

# Nettoyer environnement Docker
./run_tests_unified.py --clean
```

## 🏗️ Architecture des Tests

### Structure Unifiée
```
tests/
├── unit/                          # Tests unitaires (rapides)
│   ├── test_data_load.py         # Tests de chargement Kaggle
│   ├── test_data_prepro.py       # Tests de preprocessing
│   └── test_reco_score.py        # Tests du moteur de recommandation
├── integration/                   # Tests d'intégration
│   ├── test_streamlit_app.py     # Tests de l'interface Streamlit
│   └── test_full_workflow.py     # Tests du workflow complet
├── performance/                   # Tests de performance
│   └── test_end_to_end.py        # Tests de charge et benchmarking
└── conftest.py                   # Configuration pytest commune
```

### Couverture de Tests
| Module | Couverture Cible | Tests Implémentés | Status |
|--------|------------------|-------------------|--------|
| `data_load.py` | 85% | 15+ tests complets | ✅ |
| `data_prepro.py` | 80% | 40+ tests robustes | ✅ |
| `reco_score.py` | 85% | 25+ tests algorithmes | ✅ |
| `app.py` | 75% | 20+ tests UI/UX | ✅ |
| **Total Projet** | **80%+** | **100+ tests** | 🎯 |

## 🛠️ Configuration Multi-Environnement

### Auto-détection Intelligente
Le script unifié détecte automatiquement :
- ✅ **Docker disponible** → Utilise Docker Compose (isolation maximale)
- ✅ **Python + pytest** → Utilise Python direct (plus rapide)
- ✅ **Windows/PowerShell** → Adaptation syntaxe commandes
- ✅ **Linux/macOS/Bash** → Support natif Unix

### Prérequis par Environnement

#### Docker (Recommandé)
```bash
# Vérification Docker
docker --version
docker-compose --version

# Exécution avec Docker
./run_tests_unified.py --docker
```

#### Python Direct
```bash
# Installation dépendances
pip install pytest pytest-cov coverage

# Ou avec Poetry
poetry install --with dev

# Exécution Python direct
./run_tests_unified.py --python
```

## 🎛️ Options Complètes

### Options de Type de Tests
- `-u, --unit` : Tests unitaires uniquement
- `-i, --integration` : Tests d'intégration uniquement  
- `-p, --performance` : Tests de performance uniquement
- `-c, --coverage` : Vérification couverture existante

### Options d'Environnement
- `--docker` : Forcer l'utilisation de Docker Compose
- `--python` : Forcer l'utilisation de Python direct
- `-d, --dev` : Mode développement interactif (Docker)
- `--clean` : Nettoyer l'environnement Docker

### Options de Configuration
- `-v, --verbose` : Mode verbose avec détails
- `-b, --build` : Forcer reconstruction images Docker
- `--no-coverage` : Désactiver la mesure de couverture
- `-m, --markers` : Filtrer par marqueurs pytest
- `--durations N` : Afficher les N tests les plus lents

## 📊 Rapports et Métriques

### Rapports de Couverture

#### Docker
```bash
# Les rapports sont dans le volume Docker
docker-compose --profile testing exec tests ls -la /app/test-reports/

# Rapports disponibles:
# - htmlcov/          # Rapport HTML interactif
# - coverage.xml      # Rapport XML pour CI/CD
# - junit.xml         # Rapport JUnit pour intégration
```

#### Python Direct
```bash
# Rapports locaux générés
ls htmlcov/          # Rapport HTML local
ls coverage.xml      # Rapport XML local

# Ouvrir rapport HTML
# Windows
start htmlcov/index.html
# macOS
open htmlcov/index.html  
# Linux
xdg-open htmlcov/index.html
```

### Métriques de Performance
Le script mesure et affiche :
- ⏱️ **Temps d'exécution** par catégorie de tests
- 📊 **Couverture par module** avec détails manquants
- 🎯 **Tests les plus lents** (top 10 par défaut)
- 💾 **Utilisation mémoire** Docker (si applicable)

## 🔧 Mode Développement

### Mode Interactif
```bash
# Lancement du mode développement
./run_tests_unified.py -d

# Dans le container interactif:
poetry run pytest tests/unit/           # Tests unitaires
poetry run pytest tests/integration/    # Tests d'intégration  
poetry run pytest --cov=src            # Tests avec couverture
poetry run coverage html               # Générer rapport HTML
pytest -k test_specific_function       # Test spécifique
pytest --pdb                          # Debugging avec pdb
exit                                   # Quitter
```

### Debugging Avancé
```bash
# Tests avec debugging
./run_tests_unified.py -u -v -m "not slow"

# Tests spécifiques avec output
python -m pytest tests/unit/test_data_prepro.py::TestIngredientPreprocessor -v -s

# Profiling des tests lents
./run_tests_unified.py --durations 20
```

## 🧹 Maintenance et Nettoyage

### Nettoyage Automatique
```bash
# Nettoyage complet environnement Docker
./run_tests_unified.py --clean

# Actions effectuées:
# - Arrêt services Docker Compose
# - Suppression containers de test
# - Nettoyage volumes Docker
# - Nettoyage images inutilisées
```

### Gestion des Ressources
```bash
# Vérification utilisation Docker
docker system df

# Nettoyage manuel avancé
docker system prune -a --volumes

# Monitoring des ressources pendant tests
docker stats
```

## 🌍 Compatibilité Multi-Plateforme

### Windows
```powershell
# PowerShell
python run_tests_unified.py

# Git Bash (recommandé)
./run_tests_unified.py

# CMD
python run_tests_unified.py --help
```

### Linux/macOS
```bash
# Bash/Zsh
./run_tests_unified.py

# Make executable si nécessaire
chmod +x run_tests_unified.py

# Direct Python
python3 run_tests_unified.py
```

### Wrapper Shell
```bash
# Utilisation du wrapper (auto-détecte python/python3)
./run_tests_unified.sh -u -v
```

## 🚀 Intégration CI/CD

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run Tests
      run: python run_tests_unified.py --python --no-coverage
    - name: Upload Coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Configuration Docker Production
```bash
# Profile de test dédié
docker-compose --profile testing up -d

# Intégration dans pipeline
./run_tests_unified.py --docker --no-coverage > test_results.log
```

## 📚 Exemples d'Usage

### Développement Quotidien
```bash
# Test rapide avant commit
./run_tests_unified.py -u

# Test complet avant push
./run_tests_unified.py

# Debugging d'un test spécifique
./run_tests_unified.py -d
# Puis dans le container: pytest tests/unit/test_specific.py -v -s --pdb
```

### Validation Release
```bash
# Suite complète avec couverture
./run_tests_unified.py -v

# Tests de performance
./run_tests_unified.py -p --durations 20

# Validation multi-environnement
./run_tests_unified.py --docker  # Test avec Docker
./run_tests_unified.py --python  # Test avec Python direct
```

### Maintenance et Monitoring
```bash
# Vérification couverture sans exécuter tests
./run_tests_unified.py -c

# Nettoyage périodique
./run_tests_unified.py --clean

# Monitoring performance
./run_tests_unified.py -p > perf_report.log
```

## 🆘 Dépannage

### Problèmes Courants

#### Docker non disponible
```bash
# Installer Docker Desktop (Windows/macOS)
# Ou Docker Engine (Linux)

# Vérifier installation
docker --version
docker-compose --version

# Redémarrer si nécessaire
docker-compose --profile testing down
./run_tests_unified.py --clean
```

#### Python/pytest manquant
```bash
# Installation via pip
pip install pytest pytest-cov coverage

# Installation via Poetry
poetry install --with dev

# Vérification
python -m pytest --version
```

#### Erreurs de permissions (Linux/macOS)
```bash
# Rendre exécutable
chmod +x run_tests_unified.py run_tests_unified.sh

# Ou utilisation directe Python
python run_tests_unified.py
```

#### Problèmes de mémoire
```bash
# Limiter les tests
./run_tests_unified.py -u  # Seulement unitaires

# Augmenter mémoire Docker
# Docker Desktop → Settings → Resources → Memory
```

### Logs de Debug
```bash
# Mode verbose maximal
./run_tests_unified.py -v --durations 50

# Logs Docker
docker-compose --profile testing logs tests

# Diagnostic environnement
./run_tests_unified.py --help
python --version
docker --version
```

## ✅ Checklist de Validation

### Avant Commit
- [ ] `./run_tests_unified.py -u` passe (tests unitaires)
- [ ] Code formaté et linted
- [ ] Pas de nouvelles dépendances non documentées

### Avant Push
- [ ] `./run_tests_unified.py` passe (tous tests)
- [ ] Couverture ≥ 80%
- [ ] Tests de performance OK
- [ ] Documentation mise à jour

### Avant Release
- [ ] Tests multi-environnement (Docker + Python)
- [ ] Tests de performance validés
- [ ] Documentation complète
- [ ] Nettoyage environnement test (`--clean`)

---

## 📞 Support

Pour toute question sur les tests :
- 📖 Consultez ce guide complet
- 🐛 Ouvrez une issue GitHub si problème persistant  
- 💬 Utilisez `./run_tests_unified.py --help` pour aide contextuelle

**🎯 Objectif atteint : Système de tests unifié et cohérent pour MangeTaMain !**