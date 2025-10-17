# MangeTaMain - Architecture Modulaire

## 📁 Structure du Projet

```
streamlit-poetry-docker/
├── app.py                    # Point d'entrée principal
├── src/                      # Code source modulaire
│   ├── __init__.py
│   ├── core/                 # Classes principales
│   │   ├── __init__.py
│   │   └── app.py           # Application principale MangeTaMainApp
│   ├── managers/            # Gestionnaires de données
│   │   ├── __init__.py
│   │   └── data_manager.py  # DataManager
│   ├── engines/             # Moteurs de traitement
│   │   ├── __init__.py
│   │   └── recommendation_engine.py  # RecommendationEngine
│   ├── ui/                  # Interface utilisateur
│   │   ├── __init__.py
│   │   └── components.py    # UIComponents
│   └── utils/               # Utilitaires
│       ├── __init__.py
│       ├── styles.py        # StyleManager
│       └── config.py        # Configuration
├── data/                    # Données (si locales)
├── Dockerfile
└── pyproject.toml
```

## 🏗️ Architecture

### Classes Principales

1. **`MangeTaMainApp`** (`src/core/app.py`)
   - Orchestre l'ensemble de l'application
   - Gère le flux principal d'exécution
   - Coordonne les autres composants

2. **`DataManager`** (`src/managers/data_manager.py`)
   - Responsable du chargement des données
   - Gestion du cache des données
   - Validation des chemins et fichiers

3. **`RecommendationEngine`** (`src/engines/recommendation_engine.py`)
   - Moteur de recommandations avec cache
   - Interface avec le système de scoring
   - Gestion des paramètres de recommandation

4. **`UIComponents`** (`src/ui/components.py`)
   - Composants d'interface réutilisables
   - Cartes de recettes, statistiques, header, footer
   - Logique d'affichage isolée

5. **`StyleManager`** (`src/utils/styles.py`)
   - Gestion centralisée des styles CSS
   - Thème et apparence de l'application

## 🚀 Utilisation

L'application se lance avec le même point d'entrée :

```bash
streamlit run app.py
```

## ✅ Avantages de cette Architecture

- **Séparation des responsabilités** : Chaque classe a un rôle bien défini
- **Maintenabilité** : Code organisé et facile à modifier
- **Réutilisabilité** : Composants modulaires réutilisables
- **Testabilité** : Chaque module peut être testé indépendamment
- **Scalabilité** : Facile d'ajouter de nouvelles fonctionnalités
- **Configuration centralisée** : Paramètres dans `config.py`

## 🔧 Modifications Futures

Pour modifier l'application :

- **Styles** → `src/utils/styles.py`
- **Interface** → `src/ui/components.py`
- **Données** → `src/managers/data_manager.py`
- **Recommandations** → `src/engines/recommendation_engine.py`
- **Configuration** → `src/utils/config.py`
- **Logic métier** → `src/core/app.py`