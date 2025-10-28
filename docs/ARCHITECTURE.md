# MangeTaMain - Architecture Modulaire

## 📁 Structure du Projet

```
streamlit-poetry-docker/
├── app.py                    # Point d'entrée principal
├── src/                      # Code source modulaire
│   ├── __init__.py
│   ├── main.py              # Module principal d'orchestration
│   ├── core/                # Classes principales
│   │   ├── __init__.py
│   │   └── app.py          # Application principale MangeTaMainApp
│   ├── managers/           # Gestionnaires de données
│   │   ├── __init__.py
│   │   └── data_manager.py # DataManager
│   ├── engines/            # Moteurs de traitement
│   │   ├── __init__.py
│   │   └── recommendation_engine.py  # RecommendationEngine
│   ├── ui/                 # Interface utilisateur
│   │   ├── __init__.py
│   │   └── components.py   # UIComponents
│   └── utils/              # Utilitaires
│       ├── __init__.py
│       ├── styles.py       # StyleManager
│       └── config.py       # Configuration
├── data/                   # Données (si locales)
├── test-reports/           # Rapports de couverture et tests
├── Dockerfile
├── Dockerfile.test
└── pyproject.toml
tests/                      # Tests (niveau racine du projet)
├── unit/                   # Tests unitaires (16 fichiers)
└── integration/            # Tests d'intégration
```

## 🏗️ Architecture

### Classes Principales

1. **Module Principal** (`src/main.py`)
   - Point d'entrée et orchestration générale
   - Coordination entre les différents composants
   - Gestion des imports et initialisation

2. **`MangeTaMainApp`** (`src/core/app.py`)
   - Orchestre l'ensemble de l'application
   - Gère le flux principal d'exécution
   - Coordonne les autres composants

3. **`DataManager`** (`src/managers/data_manager.py`)
   - Responsable du chargement des données
   - Gestion du cache des données
   - Validation des chemins et fichiers

4. **`RecommendationEngine`** (`src/engines/recommendation_engine.py`)
   - Moteur de recommandations avec cache
   - Interface avec le système de scoring
   - Gestion des paramètres de recommandation

5. **`UIComponents`** (`src/ui/components.py`)
   - Composants d'interface réutilisables
   - Cartes de recettes, statistiques, header, footer
   - Logique d'affichage isolée

6. **`StyleManager`** (`src/utils/styles.py`)
   - Gestion centralisée des styles CSS
   - Thème et apparence de l'application

## 🧪 Infrastructure de Tests

Le projet dispose d'une suite de tests exhaustive :
- **121 tests unitaires** répartis dans 16 fichiers spécialisés
- **Tests d'intégration** pour les workflows complets
- **86% de couverture de code** globale
- **Rapports automatisés** dans `test-reports/`

## 🚀 Utilisation

L'application se lance avec le même point d'entrée :

```bash
streamlit run app.py
```

## ✅ Avantages de cette Architecture

- **Séparation des responsabilités** : Chaque classe a un rôle bien défini
- **Maintenabilité** : Code organisé et facile à modifier
- **Réutilisabilité** : Composants modulaires réutilisables
- **Testabilité** : Chaque module peut être testé indépendamment (**86% de couverture atteinte !**)
- **Scalabilité** : Facile d'ajouter de nouvelles fonctionnalités
- **Configuration centralisée** : Paramètres dans `config.py`
- **Qualité assurée** : Suite de tests exhaustive avec 121 tests unitaires

## 🔧 Modifications Futures

Pour modifier l'application :

- **Orchestration générale** → `src/main.py`
- **Logique métier** → `src/core/app.py`
- **Styles** → `src/utils/styles.py`
- **Interface** → `src/ui/components.py`
- **Données** → `src/managers/data_manager.py`
- **Recommandations** → `src/engines/recommendation_engine.py`
- **Configuration** → `src/utils/config.py`
- **Tests** → `tests/unit/` et `tests/integration/`