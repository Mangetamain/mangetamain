# Formulations mathématiques — indicateurs pour visualisation

Voici les formules mathématiques précises et compactes pour chaque indicateur utilisé dans le scoring. Utilisez-les dans la doc ou pour afficher dans l'UI.

---

## 1. Jaccard (similarité d'ensembles)
Soient A et B des ensembles d'ingrédients :
- Jaccard(A,B) = |A ∩ B| / |A ∪ B|
- Cas particulier : si |A ∪ B| = 0 alors Jaccard(A,B) = 0

Formule :
$$J(A,B) = \frac{|A \cap B|}{|A \cup B|}$$

---

## 2. TF–IDF (poids d'un terme) et similarité cosinus
Pour un terme $t$, document $d$ (recette) et corpus de $N$ documents :
- TF (optionnel normalisé) : $\mathrm{tf}_{t,d} = \frac{f_{t,d}}{\sum_{t'} f_{t',d}}$ ou simple fréquence $f_{t,d}$
- IDF (lissage pour éviter div/0) : $\mathrm{idf}_t = \log\left(\frac{N}{1 + \mathrm{df}_t}\right)$
- TF–IDF : $w_{t,d} = \mathrm{tf}_{t,d} \times \mathrm{idf}_t$

Vectorisation :
- vecteur recette $v_d = [w_{t_1,d}, w_{t_2,d}, \dots]$
- vecteur requête utilisateur $q = [w_{t_1,q}, w_{t_2,q}, \dots]$

Similarité cosinus :
$$\cos(v_d,q) = \frac{v_d \cdot q}{\|v_d\|_2 \; \|q\|_2}$$

- Si $\|v_d\|_2=0$ ou $\|q\|_2=0$ alors $\cos(v_d,q)=0$.

Batch (toutes recettes) : normaliser tous les vecteurs pour accélérer
$$\text{cosines} = V \cdot \hat{q} \quad\text{où}\quad \hat{q}=\frac{q}{\|q\|_2},\; \hat{V}=\frac{V}{\|V\|_2\text{ (ligne par ligne)}}$$

---

## 3. Moyenne des notes (rating) et normalisation Min–Max
Soit la moyenne des notes d'une recette $r$ :
$$\bar{r} = \frac{1}{m}\sum_{i=1}^m r_i$$

Min–Max normalization sur tout l'ensemble :
$$\tilde{r} = \begin{cases}
\frac{\bar{r}-\min(\bar{r})}{\max(\bar{r})-\min(\bar{r})}, & \text{si } \max\neq\min\\[8pt]
0.5, & \text{si } \max=\min
\end{cases}$$

---

## 4. Popularité (nombre d'interactions) — normalisation Min–Max
Soit $n_r$ le nombre d'interactions (avis) pour la recette :
$$\text{pop}_r = \begin{cases}
\frac{n_r-\min(n)}{\max(n)-\min(n)}, & \max(n)\neq\min(n)\\[6pt]
0.0, & \text{si } \max(n)=\min(n)
\end{cases}$$

---

## 5. Mise à l'échelle robuste (optionnelle)
Pour réduire l'effet des outliers, utiliser log-scaling avant Min–Max :
$$n'_r = \log(1 + n_r),\quad \text{puis Min–Max sur } n'_r$$

---

## 6. Score hybride final (combinatoire linéaire)
Combiner les composantes normalisées en un score unique :
$$\text{score}_r = \alpha \cdot J(A,B_r) + \delta \cdot \cos(v_{B_r},q) + \beta \cdot \tilde{r} + \gamma \cdot \text{pop}_r$$

avec contraintes usuelles : $\alpha,\beta,\gamma,\delta \ge 0$. Optionnel : normaliser les poids pour $\alpha+\beta+\gamma+\delta=1$.

Exemple (valeurs par défaut) :
$\alpha=0.4,\ \beta=0.3,\ \gamma=0.2,\ \delta=0.1$

---

## 7. Traitement des cas limites (formules à appliquer)
- Divisions par zéro : retourner 0 ou valeur neutre (ex. 0.5 pour ratings uniformes).
- Données manquantes : remplacer par valeur neutre avant combinaison.
- Préférence utilisateur : appliquer multiplicateur $w_{\text{pref}} \in [0,2]$ sur certaines composantes si souhaité.

---

## 8. Métriques d'évaluation (formulations)
- **Precision_k** : Proportion d'éléments pertinents parmi les k premiers résultats
$$\mathrm{P_k} = \frac{1}{k}\sum_{i=1}^k \mathbf{1}[\text{rel}_i = 1]$$

- **Recall_k** : Proportion d'éléments pertinents récupérés parmi tous les éléments pertinents
$$\mathrm{R_k} = \frac{|\{\text{éléments pertinents dans les k premiers}\}|}{|\{\text{tous les éléments pertinents}\}|}$$

- **DCG_k** (Discounted Cumulative Gain) et **NDCG@k** :
$$\mathrm{DCG_k} = \sum_{i=1}^k \frac{2^{\text{rel}_i}-1}{\log_2(i+1)}$$
$$\mathrm{NDCG_k} = \frac{\mathrm{DCG_k}}{\mathrm{IDCG_k}}$$
où $\mathrm{IDCG_k}$ est le DCG idéal (tri par pertinence décroissante)

- **MRR** (Mean Reciprocal Rank) : Position du premier élément pertinent
$$\mathrm{MRR} = \frac{1}{|Q|}\sum_{q=1}^{|Q|} \frac{1}{\text{rank}_q}$$

---

## 9. Recommandations d'implémentation pratique
- **TF-IDF optimisé** : Pré-calculer la matrice TF-IDF pour tout le corpus de recettes, vectoriser seulement la requête utilisateur à la volée
- **Normalisation robuste** : Toujours normaliser les composantes en [0,1] avant combinaison linéaire
- **Gestion des erreurs** : En cas d'échec TF-IDF (sklearn indisponible), utiliser Jaccard comme fallback
- **Logging** : Ajouter des logs pour les cas où $\max=\min$ dans Min-Max
- **Performance** : Limiter `max_features` dans TF-IDF pour contrôler la mémoire (ex: 1000)
- **Tests A/B** : Évaluer différents poids $(\alpha, \beta, \gamma, \delta)$ avec des métriques réelles

---

## 10. Contexte d'utilisation dans le projet
Ce système de scoring hybride est implémenté dans `preprocessing/reco_score.py` avec :
- Fallback automatique si sklearn n'est pas disponible
- Support des deux modes : batch (plusieurs recettes) et unitaire (une recette)
- Normalisation robuste des ratings et popularité
- Logging détaillé pour le debugging

**Utilisation recommandée** : Ajuster les poids selon le contexte :
- **Découverte** : Augmenter $\gamma$ (popularité) pour des recettes sûres
- **Personnalisation** : Augmenter $\alpha$ (Jaccard) pour correspondance exacte d'ingrédients
- **Qualité** : Augmenter $\beta$ (rating) pour privilégier les meilleures recettes
- **Sémantique** : Augmenter $\delta$ (cosine) pour similarité lexicale avancée

---



