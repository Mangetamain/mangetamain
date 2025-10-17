import pandas as pd

# Import conditionnel de sklearn avec fallback
try:
    from sklearn.preprocessing import MinMaxScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class RecipeScorer:
    """Classe pour scorer et recommander des recettes"""

    def __init__(self, alpha=0.5, beta=0.3, gamma=0.2):
        """
        Args:
            alpha: Poids pour la similarité des ingrédients
            beta: Poids pour le rating moyen
            gamma: Poids pour le nombre de reviews
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        # Utiliser sklearn si disponible, sinon normalisation manuelle
        if SKLEARN_AVAILABLE:
            self.scaler = MinMaxScaler()
        else:
            self.scaler = None

    @staticmethod
    def jaccard_similarity(list1, list2) -> float:
        """Calcule la similarité de Jaccard entre deux listes"""
        if not list1 or not list2:
            return 0.0

        set1 = set(list1) if not isinstance(list1, set) else list1
        set2 = set(list2) if not isinstance(list2, set) else list2

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def normalize_series(self, series):
        """Normalisation entre 0 et 1 (avec ou sans sklearn)"""
        if self.scaler is not None and SKLEARN_AVAILABLE:
            # Utiliser sklearn
            return pd.Series(
                self.scaler.fit_transform(series.values.reshape(-1, 1)).flatten(),
                index=series.index
            )
        else:
            # Normalisation manuelle
            min_val = series.min()
            max_val = series.max()
            if max_val == min_val:
                return pd.Series([0.5] * len(series), index=series.index)
            return (series - min_val) / (max_val - min_val)

    def compute_base_score(self, recipes_df, interactions_df):

        if len(interactions_df) == 0:
            return pd.DataFrame(columns=['id', 'mean_rating_norm', 'popularity'])

        # Grouper les interactions par recipe_id
        stats = interactions_df.groupby("recipe_id").agg(
            mean_rating=('rating', 'mean'),
            n_reviews=('rating', 'count')
        ).reset_index()

        # CORRECTION CRITIQUE: Renommer pour matcher recipes_df
        stats = stats.rename(columns={'recipe_id': 'id'})

        # Normalisation
        if len(stats) > 0:
            stats["mean_rating_norm"] = self.normalize_series(stats['mean_rating'])
            stats["popularity"] = self.normalize_series(stats['n_reviews'])
        else:
            stats["mean_rating_norm"] = 0.5
            stats["popularity"] = 0.0

        return stats

    def recommend(self, recipes_df, interactions_df, user_ingredients, time_limit=None, top_n=10):
        """
        CORRECTION: Recommande des recettes avec gestion d'erreurs robuste
        """
        # Copier pour éviter les modifications
        df = recipes_df.copy()

        # Filtrer par temps si spécifié
        if time_limit and 'minutes' in df.columns:
            initial_count = len(df)
            df = df[df['minutes'] <= time_limit]
            print(f"⏱️ Filtrage temps: {initial_count} → {len(df)} recettes")

        # Calculer la similarité Jaccard
        ingredient_col = 'normalized_ingredients' if 'normalized_ingredients' in df.columns else 'ingredients'
        print(f"Utilisation de la colonne: {ingredient_col}")

        def safe_jaccard(ing):
            if ing is not None and len(ing) > 0 if isinstance(ing, list) else pd.notnull(ing):
                return self.jaccard_similarity(user_ingredients, ing)
            return 0

        df["jaccard"] = df[ingredient_col].apply(safe_jaccard)

        # Calculer les scores de base
        stats = self.compute_base_score(recipes_df, interactions_df)
        print(f"Stats calculées pour {len(stats)} recettes")

        # MERGER CORRIGÉ: maintenant les deux ont 'id'
        df = df.merge(stats, on="id", how="left")
        print(f"Après fusion: {len(df)} recettes")

        # Remplir les valeurs manquantes
        df["mean_rating_norm"] = df["mean_rating_norm"].fillna(0.5)
        df["popularity"] = df["popularity"].fillna(0.0)

        # Score final
        df["score"] = (
            self.alpha * df['jaccard'] +
            self.beta * df['mean_rating_norm'] +
            self.gamma * df['popularity']
        )

        # COLONNES CORRIGÉES: utiliser 'id' partout
        columns_to_return = [
            'id', 'name', 'jaccard', 'mean_rating_norm',
            'popularity', 'score'
        ]

        # Ajouter la colonne d'ingrédients si elle existe
        if ingredient_col in df.columns:
            columns_to_return.append(ingredient_col)

        # Ajouter 'minutes' si elle existe
        if 'minutes' in df.columns:
            columns_to_return.append('minutes')

        # Filtrer les colonnes existantes
        existing_columns = [col for col in columns_to_return if col in df.columns]

        result = df.sort_values("score", ascending=False).head(top_n)
        print(f"Retour de {len(result)} recommandations")

        return result[existing_columns]


# Alias pour compatibilité
RecipScorer = RecipeScorer


# Test direct du module
if __name__ == "__main__":
    print("Test direct du module reco_score")
    scorer = RecipeScorer()

    # Test Jaccard
    user_ing = ["chicken", "onion"]
    recipe_ing = ["chicken", "tomato", "onion"]
    jaccard = RecipeScorer.jaccard_similarity(user_ing, recipe_ing)
    print(f"Test Jaccard: {jaccard:.3f}")
    print("Module reco_score prêt!")
