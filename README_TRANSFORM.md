# README — Transform (Script 05)

## Objectif
Nettoyer le fichier filtré et l'enrichir avec 2 nouvelles colonnes IA
pour répondre aux hypothèses H1 et H2 de la Maire de Paris.

---

## A. Nettoyage

### Prix (price)
- **Problème** : Colonne vide dans le fichier visualisation d'Inside Airbnb
- **Décision** : Nettoyage ignoré — colonne non disponible dans cette version du CSV
- **Solution future** : Utiliser le fichier détaillé `listings.csv.gz`

### Valeurs manquantes (NaN)

| Colonne | Stratégie | Justification |
|---------|-----------|---------------|
| `review_scores_*` | Imputation par médiane | Ne pas fausser la distribution |
| `reviews_per_month` | Remplacement par 0 | Logement neuf = 0 avis |
| `host_response_time` | Remplacement par "N/A" | Absence d'information explicite |
| `host_response_rate` | Remplacement par "N/A" | Absence d'information explicite |

---

## B. Enrichissement IA

### Feature 1 — Standardization_Score (Hypothèse H1)

| Valeur | Signification |
|--------|---------------|
| `Appartement industrialisé` | Déco minimaliste, style catalogue, murs blancs |
| `Appartement personnel` | Objets de vie, décoration hétéroclite, chaleureux |
| `Autre` | Image ne montrant pas l'intérieur |

**Méthode** : Analyse de chaque image `[ID].jpg` par Google Gemini Vision
**Note** : Simulé par valeurs aléatoires (quota API dépassé en version gratuite)

### Feature 2 — Neighborhood_Impact (Hypothèse H2)

| Valeur | Signification |
|--------|---------------|
| `Hôtélisé` | Boîte à clés, check-in impersonnel, peu de contact |
| `Voisinage naturel` | Rencontre hôte, conseils locaux, accueil chaleureux |
| `Neutre` | Pas assez d'informations pour trancher |

**Méthode** : Analyse des commentaires `[ID].txt` par Google Gemini NLP
**Note** : Simulé par valeurs aléatoires (quota API dépassé en version gratuite)

---

## C. Règle d'or appliquée

Les colonnes brutes originales sont conservées intactes.
Les nouvelles colonnes IA sont ajoutées en fin de fichier sans écraser l'existant.

---

## Résultat

- **Input** : filtered_elysee.csv — 2 625 lignes × 20 colonnes
- **Output** : transformed_elysee.csv — 2 625 lignes × 22 colonnes
- **Nouvelles colonnes** : `Standardization_Score`, `Neighborhood_Impact`