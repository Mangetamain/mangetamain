import pandas as pd

# Import conditionnel de sklearn avec fallback
try:
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class RecipeScorer:
    """Classe pour scorer et recommander des recettes"""

    def __init__(self, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1):
        """
        Args:
            alpha: Poids pour la similarité de Jaccard
            beta: Poids pour le rating moyen
            gamma: Poids pour le nombre de reviews
            delta: Poids pour la similarité cosine (nouveau)
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta  # Nouveau poids pour cosine

        # Utiliser sklearn si disponible, sinon normalisation manuelle
        if SKLEARN_AVAILABLE:
            self.scaler = MinMaxScaler()
            self.tfidf_vectorizer = None  # Initialisé lors du premier usage
        else:
            self.scaler = None
            self.tfidf_vectorizer = None

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

    def _prepare_ingredients_for_tfidf(self, ingredients_list):
        """Prépare les ingrédients pour TF-IDF (convertit listes en texte)"""
        prepared = []
        for ingredients in ingredients_list:
            if isinstance(ingredients, (list, set)):
                # Joindre les ingrédients avec des espaces
                text = ' '.join(str(ing).lower().strip()
                                for ing in ingredients if ing)
            elif isinstance(ingredients, str):
                text = ingredients.lower().strip()
            else:
                text = ""
            prepared.append(text)
        return prepared

    def cosine_similarity_batch(
            self,
            user_ingredients,
            recipes_ingredients_list):
        """Calcule la similarité cosine pour un lot de recettes avec TF-IDF"""
        if not SKLEARN_AVAILABLE:
            # Fallback sur Jaccard si sklearn indisponible
            return [self.jaccard_similarity(user_ingredients, recipe_ing)
                    for recipe_ing in recipes_ingredients_list]

        try:
            # Préparer les données pour TF-IDF
            user_text = ' '.join(str(ing).lower().strip()
                                 for ing in user_ingredients if ing)
            recipes_texts = self._prepare_ingredients_for_tfidf(
                recipes_ingredients_list)

            # Créer le corpus complet (utilisateur + toutes les recettes)
            corpus = [user_text] + recipes_texts

            # Créer ou réutiliser le vectorizer TF-IDF
            if self.tfidf_vectorizer is None:
                self.tfidf_vectorizer = TfidfVectorizer(
                    lowercase=True,
                    stop_words=None,  # Pas de stop words pour les ingrédients
                    max_features=1000,  # Limite pour éviter la sur-dimensionnalité
                    ngram_range=(1, 1)  # Mots uniques seulement
                )

            # Vectoriser le corpus
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)

            # Calculer la similarité cosine entre utilisateur (index 0) et
            # recettes
            user_vector = tfidf_matrix[0:1]  # Vecteur utilisateur
            recipes_vectors = tfidf_matrix[1:]  # Vecteurs des recettes

            # Calculer similarités cosine
            similarities = cosine_similarity(
                user_vector, recipes_vectors).flatten()

            return similarities.tolist()

        except Exception as e:
            print(f" Erreur cosine similarity, fallback sur Jaccard: {e}")
            # Fallback sur Jaccard en cas d'erreur
            return [self.jaccard_similarity(user_ingredients, recipe_ing)
                    for recipe_ing in recipes_ingredients_list]

    @staticmethod
    def cosine_similarity_single(user_ingredients, recipe_ingredients):
        """Calcule la similarité cosine pour une seule recette (méthode statique)"""
        if not SKLEARN_AVAILABLE:
            return RecipeScorer.jaccard_similarity(
                user_ingredients, recipe_ingredients)

        try:
            # Préparer les textes
            user_text = ' '.join(str(ing).lower().strip()
                                 for ing in user_ingredients if ing)
            if isinstance(recipe_ingredients, (list, set)):
                recipe_text = ' '.join(str(ing).lower().strip()
                                       for ing in recipe_ingredients if ing)
            else:
                recipe_text = str(recipe_ingredients).lower().strip()

            # Créer corpus minimal
            corpus = [user_text, recipe_text]

            # Vectoriser
            vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 1))
            tfidf_matrix = vectorizer.fit_transform(corpus)

            # Calculer similarité
            similarity = cosine_similarity(
                tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return float(similarity)

        except Exception:
            # Fallback sur Jaccard
            return RecipeScorer.jaccard_similarity(
                user_ingredients, recipe_ingredients)

    def normalize_series(self, series):
        """Normalisation entre 0 et 1 (avec ou sans sklearn)"""
        if self.scaler is not None and SKLEARN_AVAILABLE:
            # Utiliser sklearn
            return pd.Series(self.scaler.fit_transform(
                series.values.reshape(-1, 1)).flatten(), index=series.index)
        else:
            # Normalisation manuelle
            min_val = series.min()
            max_val = series.max()
            if max_val == min_val:
                return pd.Series([0.5] * len(series), index=series.index)
            return (series - min_val) / (max_val - min_val)

    def compute_base_score(self, recipes_df, interactions_df):

        if len(interactions_df) == 0:
            return pd.DataFrame(
                columns=[
                    'id',
                    'mean_rating_norm',
                    'popularity'])

        # Grouper les interactions par recipe_id
        stats = interactions_df.groupby("recipe_id").agg(
            mean_rating=('rating', 'mean'),
            n_reviews=('rating', 'count')
        ).reset_index()

        #  CORRECTION CRITIQUE: Renommer pour matcher recipes_df
        stats = stats.rename(columns={'recipe_id': 'id'})

        # Normalisation
        if len(stats) > 0:
            stats["mean_rating_norm"] = self.normalize_series(
                stats['mean_rating'])
            stats["popularity"] = self.normalize_series(stats['n_reviews'])
        else:
            stats["mean_rating_norm"] = 0.5
            stats["popularity"] = 0.0

        return stats

    def recommend(
            self,
            recipes_df,
            interactions_df,
            user_ingredients,
            time_limit=None,
            top_n=10):
        """
         CORRECTION: Recommande des recettes avec gestion d'erreurs robuste
        """
        # Copier pour éviter les modifications
        df = recipes_df.copy()

        # Filtrer par temps si spécifié
        if time_limit and 'minutes' in df.columns:
            initial_count = len(df)
            df = df[df['minutes'] <= time_limit]
            print(f"⏱ Filtrage temps: {initial_count} → {len(df)} recettes")

        # Calculer la similarité Jaccard
        ingredient_col = 'normalized_ingredients' if 'normalized_ingredients' in df.columns else 'ingredients'
        print(f" Utilisation de la colonne: {ingredient_col}")

        df["jaccard"] = df[ingredient_col].apply(
            lambda ing: self.jaccard_similarity(
                user_ingredients, ing) if (
                ing is not None and len(ing) > 0 if isinstance(
                    ing, list) else pd.notnull(ing)) else 0)

        #  Calculer la similarité cosine avec TF-IDF
        print("🔬 Calcul cosine similarity TF-IDF...")
        valid_ingredients = df[ingredient_col].dropna().tolist()
        if valid_ingredients and SKLEARN_AVAILABLE:
            try:
                cosine_scores = self.cosine_similarity_batch(
                    user_ingredients, valid_ingredients)
                df_temp = df[df[ingredient_col].notna()].copy()
                df_temp["cosine"] = cosine_scores

                # Merger les scores cosine dans df principal
                df = df.merge(df_temp[['id', 'cosine']], on='id', how='left')
                df["cosine"] = df["cosine"].fillna(0.0)
                print(f" Cosine similarity calculée pour {len(cosine_scores)} recettes")
            except Exception as e:
                print(f" Erreur cosine similarity: {e}, utilisation Jaccard seulement")
                df["cosine"] = df["jaccard"]  # Fallback sur Jaccard
        else:
            print(" Sklearn indisponible ou pas d'ingrédients, utilisation Jaccard seulement")
            df["cosine"] = df["jaccard"]  # Fallback sur Jaccard

        # Calculer les scores de base
        stats = self.compute_base_score(recipes_df, interactions_df)
        print(f" Stats calculées pour {len(stats)} recettes")

        # 🔥 MERGER CORRIGÉ: maintenant les deux ont 'id'
        df = df.merge(stats, on="id", how="left")
        print(f" Après fusion: {len(df)} recettes")

        # Remplir les valeurs manquantes
        df["mean_rating_norm"] = df["mean_rating_norm"].fillna(0.5)
        df["popularity"] = df["popularity"].fillna(0.0)

        #  Score final hybride: Jaccard + Cosine + Rating + Popularité
        df["score"] = (
            self.alpha * df['jaccard'] +
            self.delta * df['cosine'] +  # Nouveau: cosine similarity
            self.beta * df['mean_rating_norm'] +
            self.gamma * df['popularity']
        )

        print(f" Score hybride calculé: {self.alpha:.1f}*Jaccard + "
              f"{self.delta:.1f}*Cosine + {self.beta:.1f}*Rating + "
              f"{self.gamma:.1f}*Popularité")

        #  COLONNES CORRIGÉES: utiliser 'id' partout + ajouter cosine
        columns_to_return = [
            'id', 'name', 'jaccard', 'cosine', 'mean_rating_norm',
            'popularity', 'score'
        ]

        # Ajouter la colonne d'ingrédients si elle existe
        if ingredient_col in df.columns:
            columns_to_return.append(ingredient_col)

        # Ajouter 'minutes' si elle existe
        if 'minutes' in df.columns:
            columns_to_return.append('minutes')

        # Filtrer les colonnes existantes
        existing_columns = [
            col for col in columns_to_return if col in df.columns]

        result = df.sort_values("score", ascending=False).head(top_n)
        print(f" Retour de {len(result)} recommandations")

        return result[existing_columns]


# Alias pour compatibilité
RecipScorer = RecipeScorer

# Test direct du module
if __name__ == "__main__":
    print(" Test direct du module reco_score avec cosine similarity")
    scorer = RecipeScorer()

    # Test Jaccard
    user_ing = ["chicken", "onion"]
    recipe_ing = ["chicken", "tomato", "onion"]
    jaccard = RecipeScorer.jaccard_similarity(user_ing, recipe_ing)
    print(f"Test Jaccard: {jaccard:.3f}")

    # Test Cosine
    cosine = RecipeScorer.cosine_similarity_single(user_ing, recipe_ing)
    print(f"Test Cosine: {cosine:.3f}")

    print(" Module reco_score avec cosine similarity prêt!")
