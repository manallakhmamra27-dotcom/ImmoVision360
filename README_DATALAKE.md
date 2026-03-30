# README — Data Lake (Zone Bronze)

## Objectif
Stocker toutes les données brutes du projet ImmoVision 360 dans leur format natif,
sans transformation, pour garantir la reproductibilité et la traçabilité.

---

## Architecture

```
data/raw/
├── tabular/
│   ├── listings.csv     # Annonces Airbnb (81 853 lignes, 70 colonnes)
│   └── reviews.csv      # Commentaires voyageurs
├── images/              # Photos des appartements [ID].jpg (320x320 px)
└── texts/               # Commentaires agrégés par annonce [ID].txt
```

---

## Conventions de nommage

| Type | Format | Exemple |
|------|--------|---------|
| Image | `<ID>.jpg` | `785412.jpg` |
| Texte | `<ID>.txt` | `785412.txt` |
| Tabulaire | nom original | `listings.csv` |

---

## Principes appliqués

### Schema-on-Read
Contrairement à une base SQL, le Data Lake accepte tout sans contrainte de schéma.
La structure est définie au moment de la lecture (Phase 2).

### Partitionnement
Les données sont organisées par type (tabular / images / texts) pour faciliter
le traitement sélectif en Phase 2.

### Idempotence
Les scripts d'ingestion vérifient si le fichier existe déjà avant de le télécharger.
Relancer un script ne crée pas de doublons.

---

## Sources

| Fichier | Source | Licence |
|---------|--------|---------|
| listings.csv | Inside Airbnb | CC BY 4.0 |
| reviews.csv | Inside Airbnb | CC BY 4.0 |
| images/ | URLs dans listings.csv | Usage académique |