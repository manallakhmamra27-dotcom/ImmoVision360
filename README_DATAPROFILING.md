# README — Data Profiling (Bloc B & C)

## Objectif
Décrire chaque variable du jeu de données `elysee_tabular` avant tout graphique,
puis croiser les variables pour répondre aux hypothèses de la Maire.

---

## Table utilisée
- **Base** : `immovision` (PostgreSQL)
- **Table** : `elysee_tabular`
- **Lignes** : 2 625 annonces du quartier Élysée

---

## Traitement des valeurs manquantes
Toutes les valeurs NULL ont été remplacées par **-1**.
La valeur -1 signifie "information non disponible" dans toute l'analyse.
Elle est distincte des 0 métier (ex: disponibilité nulle = 0 jour).

---

## Description univariée (Bloc B)

| Colonne | Nature | Min | Max | Moyenne | Notes |
|---------|--------|-----|-----|---------|-------|
| `id` | Identifiant | — | — | — | Pas de calcul |
| `calculated_host_listings_count` | Quantitative | 1 | 816 | 52.2 | Max = 816 (acteur industriel) |
| `availability_365` | Quantitative | 0 | 365 | 174.7 | Moyenne = 175 jours/an |
| `host_response_rate_num` | Quantitative | -1 | 100 | 68.0 | Beaucoup de -1 (info manquante) |
| `room_type_code` | Nominale | 1 | 3 | — | 2 = logement entier (majoritaire) |
| `host_response_time_code` | Ordinale | -1 | 3 | — | 0 = très rapide, 3 = lent |
| `standardization_score` | Ordinale | -1 | 1 | — | 1=industrialisé, 0=personnel, -1=autre |
| `neighborhood_impact_score` | Ordinale | -1 | 1 | — | 1=hôtélisé, 0=voisinage, -1=autre |

---

## Croisements (Bloc C)

| Croisement | Variables | Graphique | Observation |
|-----------|-----------|-----------|-------------|
| Disponibilité vs Concentration | `availability_365` × `calculated_host_listings_count` | Nuage de points | Les hôtes multi-biens ont une disponibilité plus élevée |
| Standardisation par type | `room_type_code` × `standardization_score` | Boxplot | Les logements entiers plus standardisés |
| Impact social par disponibilité | `availability_365` × `neighborhood_impact_score` | Boxplot par classe | Logements très disponibles = plus hôtélisés |
| Réactivité par type | `room_type_code` × `host_response_time_code` | Barres groupées | Logements entiers = réponse plus rapide |

---

## Limites
- Scores H1/H2 simulés — résultats non représentatifs de la réalité
- Corrélation observée ≠ causalité
- Prix absent — impossible d'analyser la hausse des loyers