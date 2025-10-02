import kagglehub
import pandas as pd 
import os
import yaml

with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

def fetch_data(dataset_name, version=None)->str:
    if version:
        dataset_name = f"{dataset_name}:{version}"
    return kagglehub.dataset_download(dataset_name)

def load_data(path,files)->pd.DataFrame:
    data_frames = {}
    for file in files : 
        file_path = os.path.join(path, file)
        if os.path.exists(file_path):
            data_frames[file] = pd.read_csv(file_path)
        else:
            raise FileNotFoundError(f"{file} introuvable dans le {path}")
    return data_frames

if __name__ == "__main__":
    dataset_path = fetch_data(config['dataset']['name'])
    dfs = load_data(dataset_path, config['dataset']['files'])
    for name, df in dfs.items():
        print(f"Data from {name}:")
        print(df.head())
    recipes_df = dfs.get('RAW_recipes.csv')
    interactions_df = dfs.get('RAW_interactions.csv')
    print(" Recipes shape:", recipes_df.shape)
    print(" Interactions shape:", interactions_df.shape)
