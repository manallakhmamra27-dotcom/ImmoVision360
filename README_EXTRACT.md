# README — Extract (Script 04)

## Objectif
Réduire les 70 colonnes du CSV brut aux seules colonnes utiles
pour tester les 3 hypothèses de la Maire de Paris.

---

## Colonnes conservées et justification

| Colonne | Hypothèse | Justification |
|---------|-----------|---------------|
| `id` | Toutes | Clé de jointure avec images et textes |
| `host_id` | H3 | Identifier les multi-propriétaires |
| `calculated_host_listings_count` | H3 | Détecter la gestion industrielle |
| `price` | H3 | Analyser la hausse des prix |
| `availability_365` | H3 | Disponibilité = usage locatif intensif |
| `property_type` | H3 | Type de bien (appartement, loft...) |
| `room_type` | H3 | Logement entier = usage hôtelier |
| `host_response_time` | H2 | Agence = réponse ultra-rapide |
| `host_response_rate` | H2 | Taux de réponse professionnel |
| `host_is_superhost` | H2 | Indicateur de professionnalisation |
| `host_identity_verified` | H2 | Confiance et authenticité |
| `number_of_reviews` | H2 | Volume d'activité |
| `review_scores_rating` | H2 | Satisfaction globale |
| `review_scores_communication` | H2 | Qualité du lien humain |
| `review_scores_checkin` | H2 | Accueil (humain vs boîte à clés) |
| `reviews_per_month` | H2 | Fréquence d'occupation |
| `picture_url` | H1 | Lien vers la photo (jointure image) |
| `neighbourhood_cleansed` | Toutes | Filtrage géographique |
| `latitude` / `longitude` | Toutes | Cartographie |

---

## Colonnes supprimées (59 colonnes)

Les colonnes supprimées sont principalement :
- Métadonnées techniques (scrape_id, last_scraped, source)
- Informations redondantes (host_url, host_thumbnail_url)
- Règles de séjour non pertinentes (minimum_nights_avg_ntm...)
- Colonnes vides dans ce fichier (price, bathrooms...)

---

## Résultat

- **Input** : listings.csv — 81 853 lignes × 70 colonnes
- **Output** : filtered_elysee.csv — 2 625 lignes × 20 colonnes
- **Réduction** : 96.8% des annonces filtrées (hors Élysée)