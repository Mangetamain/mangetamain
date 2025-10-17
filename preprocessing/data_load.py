import os
import pandas as pd
import kagglehub


def fetch_data(dataset_name, version=None):
    """Télécharge un dataset depuis Kaggle"""
    if version:
        dataset_name = f"{dataset_name}:{version}"
    return kagglehub.dataset_download(dataset_name)


def load_data(path, files):
    """Charge les fichiers CSV depuis un répertoire"""
    data_frames = {}
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.exists(file_path):
            data_frames[file] = pd.read_csv(file_path)
        else:
            raise FileNotFoundError(f"Fichier {file} introuvable dans {path}")
    return data_frames