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
- 🔄 Updates shared volume with fresh preprocessed data
- 🔄 Use when data needs to be updated

### Option 3: Testing Mode
```bash
docker-compose --profile testing up -d
```
- 🧪 Runs automated tests
- 🧪 Generates test reports

## 🛑 Stop Services
```bash
docker-compose down
```


## 🐳 Docker Hub
Preprocessed data is available at: `andranik777/mangetamain-data:latest`

## 📖 Documentation
- [Docker Volume Usage](docs/DOCKER_VOLUME_USAGE.md) - Detailed volume management
- [Architecture](docs/ARCHITECTURE.md) - System architecture
- [Tests](docs/TESTS_README.md) - Testing information