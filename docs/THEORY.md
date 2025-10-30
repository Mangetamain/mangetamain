# Formulations mathématiques — indicateurs pour visualisation

---

## 📊 Ressources Complémentaires

🗺️ **[Schéma d'Architecture Interactive](https://htmlpreview.github.io/?https://github.com/Mangetamain/mangetamain/blob/main/docs/recipe_script_diagram.html)** - Visualisation complète du système de prétraitement des recettes

---

## 1. Jaccard (similarité d'ensembles)

<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}J(A,B)=\frac{|A\cap%20B|}{|A\cup%20B|}" alt="Jaccard Formula"/>
</p>

**Définition :** Soient A et B des ensembles d'ingrédients, cette formule mesure la proportion d'ingrédients communs sur le total d'ingrédients uniques.

**Cas particulier :** Si |A ∪ B| = 0 alors J(A,B) = 0

---

## 2. TF–IDF et similarité cosinus

**TF-IDF :**
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}w_{t,d}=\mathrm{tf}_{t,d}\times\mathrm{idf}_t" alt="TF-IDF Formula"/>
</p>

**Définition :** Pour un terme t, document d (recette) et corpus de N documents, le poids TF-IDF combine la fréquence locale (tf) et l'importance globale (idf).

**Similarité cosinus :**
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}\cos(v_d,q)=\frac{v_d\cdot%20q}{\|v_d\|_2\;\|q\|_2}" alt="Cosine Similarity"/>
</p>

**Définition :** Mesure l'angle entre les vecteurs TF-IDF de la requête utilisateur et d'une recette. Valeurs dans [0,1] pour vecteurs non-négatifs.

---

## 3. Moyenne des notes et normalisation Min–Max

**Moyenne des notes :**
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}\bar{r}=\frac{1}{m}\sum_{i=1}^m%20r_i" alt="Average Rating"/>
</p>

**Définition :** Calcule la note moyenne d'une recette sur m évaluations.

**Normalisation Min-Max :**
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}\tilde{r}=\begin{cases}\frac{\bar{r}-\min(\bar{r})}{\max(\bar{r})-\min(\bar{r})}&\text{si%20}\max\neq\min\\0.5&\text{si%20}\max=\min\end{cases}" alt="Min-Max Normalization"/>
</p>

**Définition :** Transforme les notes dans l'intervalle [0,1] pour permettre la combinaison avec d'autres indicateurs.

---

## 4. Popularité (normalisation du nombre d'interactions)

<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}\text{pop}_r=\frac{n_r-\min(n)}{\max(n)-\min(n)}" alt="Popularity Normalization"/>
</p>

**Définition :** Normalise le nombre d'avis/interactions n_r d'une recette dans [0,1]. Mesure la confiance basée sur le volume d'interactions.

---

## 5. Mise à l'échelle robuste (optionnelle)

<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}n'_r=\log(1+n_r)" alt="Log Scaling"/>
</p>

**Définition :** Pour réduire l'effet des outliers, appliquer une transformation logarithmique avant la normalisation Min-Max.

---

## 6. Score hybride final

<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}\text{score}_r=\alpha\cdot%20J(A,B_r)+\delta\cdot\cos(v_{B_r},q)+\beta\cdot\tilde{r}+\gamma\cdot\text{pop}_r" alt="Hybrid Score"/>
</p>

**Définition :** Combine les quatre indicateurs avec des poids configurables pour obtenir un score final de recommandation.

**Valeurs par défaut :** α=0.4 (Jaccard), β=0.3 (Rating), γ=0.2 (Popularité), δ=0.1 (Cosinus)

---

## 7. Traitement des cas limites

**Gestion des erreurs courantes :**
- **Divisions par zéro :** Retourner 0 ou valeur neutre (ex. 0.5 pour ratings uniformes)
- **Données manquantes :** Remplacer par valeur neutre avant combinaison
- **Listes vides :** Jaccard = 0, Cosinus utilise fallback vers Jaccard
- **Échec TF-IDF :** Fallback automatique vers similarité de Jaccard

---

## 8. Métriques d'évaluation

**Precision@k :**
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}\mathrm{P@k}=\frac{1}{k}\sum_{i=1}^k\mathbf{1}[\text{rel}_i=1]" alt="Precision at k"/>
</p>

**Définition :** Proportion d'éléments pertinents parmi les k premiers résultats recommandés.

**NDCG@k :**
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}\mathrm{NDCG@k}=\frac{\mathrm{DCG@k}}{\mathrm{IDCG@k}}" alt="NDCG at k"/>
</p>

**Définition :** Normalized Discounted Cumulative Gain, prend en compte la position des éléments pertinents (plus haut = mieux).

**MRR :**
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\color{white}\mathrm{MRR}=\frac{1}{|Q|}\sum_{q=1}^{|Q|}\frac{1}{\text{rank}_q}" alt="Mean Reciprocal Rank"/>
</p>

**Définition :** Mean Reciprocal Rank, mesure la position moyenne du premier élément pertinent trouvé.

---

## 9. Recommandations d'usage

**Ajustement des poids selon le contexte :**

| Contexte | Poids à augmenter | Objectif |
|----------|-------------------|----------|
| **🔍 Découverte** | γ (Popularité) | Recommander des recettes éprouvées |
| **🎯 Personnalisation** | α (Jaccard) | Correspondance exacte d'ingrédients |
| **⭐ Qualité** | β (Rating) | Privilégier les meilleures notes |
| **🧠 Sémantique** | δ (Cosinus) | Similarité lexicale avancée |

**Implémentation pratique :**
- Toujours normaliser les composantes en [0,1] avant combinaison
- Prévoir des fallbacks pour l'indisponibilité de sklearn
- Instrumenter avec des métriques Precision@k et Coverage
- Tester différents poids via A/B testing

---