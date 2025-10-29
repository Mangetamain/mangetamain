#!/usr/bin/env python3
"""
Pipeline SIMPLE pour MangeTaMain - Preprocessing complet du dataset
Injection directe dans Streamlit
"""


import os
import sys
from datetime import datetime
import logging
from multiprocessing import Pool, cpu_count
import pandas as pd
import yaml

from data_prepro import RecipePreprocessor
from data_load import fetch_data, load_data
# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('preprocessing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Imports locaux


def process_chunk(chunk_data):
    """Traite un chunk de recettes"""
    chunk, chunk_id = chunk_data

    try:
        preprocessor = RecipePreprocessor()
        processed = preprocessor.preprocess_dataframe(chunk)

        logger.info(f" Chunk {chunk_id}: {len(processed)} recettes traitées")
        return processed

    except Exception as e:
        logger.error(f" Erreur chunk {chunk_id}: {e}")
        return pd.DataFrame()


def run_complete_preprocessing():
    """
    Pipeline complet pour tout le dataset
    Résultat directement utilisable par Streamlit
    """

    logger.info(" PREPROCESSING COMPLET - MANGETAMAIN")
    start_time = datetime.now()

    # === ÉTAPE 1: CHARGEMENT DES DONNÉES ===
    logger.info(" 1. Chargement des données Kaggle...")

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Télécharger et charger
    dataset_id = config['datasets']['recipes']['dataset_id']
    dataset_path = fetch_data(dataset_id)

    files_to_load = [
        config['datasets']['recipes']['file_name'],
        config['datasets']['interactions']['file_name']
    ]

    dfs = load_data(dataset_path, files_to_load)
    recipes_df = dfs['RAW_recipes.csv'].copy()
    interactions_df = dfs['RAW_interactions.csv'].copy()

    logger.info(" Dataset complet chargé:")
    logger.info(f"   - Recettes: {len(recipes_df):,}")
    logger.info(f"   - Interactions: {len(interactions_df):,}")

    # === ÉTAPE 2: NETTOYAGE PRÉALABLE ===
    logger.info("🧹 2. Nettoyage préalable des données...")

    # Supprimer les recettes sans ingrédients
    initial_count = len(recipes_df)
    recipes_df = recipes_df.dropna(subset=['ingredients'])
    recipes_df = recipes_df[recipes_df['ingredients'] != '[]']
    # Au moins quelques caractères
    recipes_df = recipes_df[recipes_df['ingredients'].str.len() > 10]

    logger.info(f" Filtrage: {initial_count:,} → {len(recipes_df):,} recettes")

    # === ÉTAPE 3: PREPROCESSING PARALLÈLE ===
    logger.info("⚡ 3. Preprocessing parallèle du dataset complet...")

    # Configuration parallèle
    n_cores = min(cpu_count() - 1, 8)  # Utiliser tous les cores - 1
    chunk_size = max(2000, len(recipes_df) // (n_cores * 3))  # Chunks optimaux

    logger.info(f" Configuration: {n_cores} cores, chunks de {chunk_size}")

    # Créer les chunks
    chunks = []
    for i in range(0, len(recipes_df), chunk_size):
        end_idx = min(i + chunk_size, len(recipes_df))
        chunk = recipes_df.iloc[i:end_idx].copy()
        chunks.append((chunk, i // chunk_size + 1))

    logger.info(f" {len(chunks)} chunks créés pour {len(recipes_df):,} recettes")

    # Traitement parallèle
    logger.info(" Démarrage du traitement parallèle...")

    with Pool(n_cores) as pool:
        processed_chunks = pool.map(process_chunk, chunks)

    # Filtrer les chunks vides
    processed_chunks = [chunk for chunk in processed_chunks if not chunk.empty]

    logger.info(f" {len(processed_chunks)} chunks traités avec succès")

    # === ÉTAPE 4: ASSEMBLAGE FINAL ===
    logger.info(" 4. Assemblage des données preprocessées...")

    # Combiner tous les chunks
    processed_recipes = pd.concat(
        processed_chunks,
        ignore_index=True,
        sort=False)

    # Merger avec les données originales nécessaires pour Streamlit
    merge_columns = [
        'id',
        'name',
        'minutes',
        'n_steps',
        'description',
        'n_ingredients']
    processed_recipes = processed_recipes.merge(
        recipes_df[merge_columns].rename(columns={'id': 'recipe_id'}),
        on='recipe_id',
        how='left'
    )

    # Colonnes pour compatibilité avec le système de recommandation
    processed_recipes['id'] = processed_recipes['recipe_id']

    # S'assurer que la colonne normalized_ingredients existe
    if 'normalized_ingredients_list' in processed_recipes.columns:
        processed_recipes['normalized_ingredients'] = processed_recipes['normalized_ingredients_list']

    logger.info(f" Dataset final: {len(processed_recipes):,} recettes preprocessées")
    logger.info(f" Colonnes: {list(processed_recipes.columns)}")

    # === ÉTAPE 5: SAUVEGARDE POUR STREAMLIT ===
    logger.info(" 5. Sauvegarde pour injection Streamlit...")

    # Créer le répertoire de sortie
    output_dir = "/shared_data"  # Dossier partagé avec Streamlit
    os.makedirs(output_dir, exist_ok=True)

    # Sauvegarde principale (Pickle pour rapidité)
    recipes_path = os.path.join(output_dir, "recipes_processed.pkl")
    processed_recipes.to_pickle(recipes_path)

    interactions_path = os.path.join(output_dir, "interactions.pkl")
    interactions_df.to_pickle(interactions_path)

    # Sauvegarde CSV pour debug
    processed_recipes.to_csv(
        os.path.join(
            output_dir,
            "recipes_processed.csv"),
        index=False)
    interactions_df.to_csv(
        os.path.join(
            output_dir,
            "interactions.csv"),
        index=False)

    logger.info(f" Données sauvegardées dans {output_dir}")

    # === ÉTAPE 6: MÉTADONNÉES ET VALIDATION ===
    logger.info(" 6. Génération des métadonnées...")

    # Validation rapide
    has_ingredients = processed_recipes['normalized_ingredients'].apply(
        lambda x: isinstance(x, list) and len(x) > 0
    ).sum()

    duration = datetime.now() - start_time
    # 6. Génération des métadonnées
    metadata = {
        'processing_date': datetime.now().isoformat(),
        'total_recipes_input': int(
            len(recipes_df)),
        'total_recipes_processed': int(
            len(processed_recipes)),
        'recipes_with_ingredients': int(has_ingredients),
        'total_interactions': int(
            len(interactions_df)),
        'processing_time_minutes': float(
            round(
                duration.total_seconds() / 60,
                2)),
        'cores_used': int(n_cores),
        'chunks_processed': int(
            len(processed_chunks)),
        'success_rate': float(
            round(
                (len(processed_recipes) / len(recipes_df)) * 100,
                2)),
        'ready_for_streamlit': True}

    # Sauvegarder les métadonnées (format JSON plus fiable)
    metadata_path = os.path.join(output_dir, "preprocessing_metadata.json")
    import json
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    # === RÉSUMÉ FINAL ===
    logger.info("🎉 PREPROCESSING COMPLET TERMINÉ !")
    logger.info(f"⏱️ Durée totale: {duration}")
    logger.info("📊 Résultats:")
    logger.info(f"   - Recettes preprocessées: {len(processed_recipes):,}")
    logger.info(f"   - Avec ingrédients normalisés: {has_ingredients:,}")
    logger.info(f"   - Interactions: {len(interactions_df):,}")
    logger.info(f"   - Taux de succès: {metadata['success_rate']}%")
    logger.info(f"   - Vitesse: {len(processed_recipes) / duration.total_seconds():.0f} recettes/seconde")
    logger.info(f"🎯 Données prêtes pour Streamlit dans {output_dir}")

    return metadata


def verify_streamlit_data():
    """Vérification que les données sont prêtes pour Streamlit"""

    logger.info("🔍 Vérification des données pour Streamlit...")

    try:
        # Charger les données
        recipes_path = "/shared_data/recipes_processed.pkl"
        interactions_path = "/shared_data/interactions.pkl"

        if not os.path.exists(recipes_path) or not os.path.exists(
                interactions_path):
            logger.error("❌ Fichiers de données manquants")
            return False

        recipes = pd.read_pickle(recipes_path)
        interactions = pd.read_pickle(interactions_path)

        # Vérifications essentielles
        required_columns = [
            'id',
            'recipe_id',
            'name',
            'normalized_ingredients']
        missing = [
            col for col in required_columns if col not in recipes.columns]

        if missing:
            logger.error(f"❌ Colonnes manquantes: {missing}")
            return False

        # Vérifier les ingrédients
        has_ingredients = recipes['normalized_ingredients'].apply(
            lambda x: isinstance(x, list) and len(x) > 0
        ).sum()

        logger.info("✅ Validation réussie:")
        logger.info(f"   - Recettes: {len(recipes):,}")
        logger.info(f"   - Avec ingrédients: {has_ingredients:,}")
        logger.info(f"   - Interactions: {len(interactions):,}")

        return True

    except Exception as e:
        logger.error(f"❌ Erreur validation: {e}")
        return False


if __name__ == "__main__":
    """Exécution du pipeline complet"""

    try:
        # Pipeline complet
        metadata = run_complete_preprocessing()

        # Vérification automatique
        if verify_streamlit_data():
            logger.info("🎊 SUCCÈS COMPLET - Streamlit prêt !")
            logger.info(
                "🚀 Vous pouvez maintenant lancer: docker-compose up streamlit-app")
        else:
            logger.error("❌ Problème de validation des données")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ ÉCHEC du pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
