# README — Load (Script 06)

## Objectif
Charger le fichier Silver (`transformed_elysee.csv`) dans PostgreSQL —
le Data Warehouse final du projet ImmoVision 360.

---

## Table cible
- **Base** : `immovision_db`
- **Table** : `elysee_listings_silver`
- **Lignes** : 2 625
- **Colonnes** : 22

---

## Sécurité — Variables d'environnement

Les identifiants PostgreSQL ne sont jamais codés en dur dans le script.
Ils sont chargés depuis le fichier `.env` via `python-dotenv`.

```
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
DB_NAME=immovision_db
```

Le fichier `.env` est exclu de Git via `.gitignore`.

---

## Idempotence

Le paramètre `if_exists='replace'` garantit que :
- Le script peut être relancé sans erreur
- La table est recréée à chaque exécution avec les données les plus récentes
- Aucune duplication de lignes

---

## Schéma de la table

| Colonne | Type SQL | Description |
|---------|----------|-------------|
| `id` | BIGINT | Identifiant unique de l'annonce |
| `host_id` | BIGINT | Identifiant de l'hôte |
| `calculated_host_listings_count` | BIGINT | Nombre d'annonces de l'hôte |
| `price` | FLOAT | Prix par nuitée |
| `availability_365` | BIGINT | Jours disponibles/an |
| `property_type` | TEXT | Type de bien |
| `room_type` | TEXT | Type de location |
| `host_response_time` | TEXT | Délai de réponse |
| `host_response_rate` | TEXT | Taux de réponse |
| `host_is_superhost` | TEXT | Statut superhost |
| `review_scores_rating` | FLOAT | Note globale |
| `Standardization_Score` | INTEGER | Score IA image (1/0/-1) |
| `Neighborhood_Impact` | INTEGER | Score IA texte (1/0/-1) |

---

## Lancer le script

```bash
python scripts/06_load.py
```

## Résultat attendu

```
[INFO]  Connexion PostgreSQL etablie avec succes.
[INFO]  Injection reussie : 2625 lignes chargees.
[INFO]  Data Warehouse pret. Phase 3 peut commencer.
```