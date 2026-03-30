

import os
import re
import logging
import pandas as pd

# ══════════════════════════════════════════════════════════════
# 1. CONFIGURATION
# ══════════════════════════════════════════════════════════════

CSV_REVIEWS  = "data/raw/tabular/reviews.csv"
CSV_LISTINGS = "data/raw/tabular/listings.csv"
OUTPUT_DIR   = "data/raw/texts/"
LOG_FILE     = "data/raw/ingestion_textes.log"

QUARTIER_CIBLE = "Élysée"
OVERWRITE = False

# ══════════════════════════════════════════════════════════════
# 2. LOGGER
# ══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8")
    ]
)
log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# 3. FONCTIONS
# ══════════════════════════════════════════════════════════════

def nettoyer_texte(texte):
    """Nettoyage léger du texte."""
    if not isinstance(texte, str):
        return ""
    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte


def charger_ids_elysee(csv_listings, quartier):
    """Retourne les IDs des annonces du quartier cible."""
    log.info(f"Lecture de listings.csv pour filtrer le quartier '{quartier}'...")

    try:
        df = pd.read_csv(csv_listings, on_bad_lines='skip', engine='python')
    except FileNotFoundError:
        log.error(f"Fichier introuvable : {csv_listings}")
        raise

    log.info(f"  Colonnes listings : {list(df.columns)}")

    # Trouver la colonne quartier
    col_quartier = None
    for candidate in ["neighbourhood_cleansed", "neighbourhood"]:
        if candidate in df.columns:
            col_quartier = candidate
            break

    if col_quartier is None:
        raise ValueError("Colonne quartier introuvable dans listings.csv")

    df_filtre = df[df[col_quartier].str.contains(quartier, case=False, na=False)]
    ids = set(df_filtre["id"].astype(str).str.strip().tolist())
    log.info(f"  {len(ids)} annonces trouvées dans '{quartier}'")
    return ids


def charger_reviews(csv_reviews, ids_cibles):
    """
    Lit reviews.csv et retourne un dictionnaire
    { listing_id : [commentaire1, commentaire2, ...] }
    """
    log.info(f"Lecture de reviews.csv...")

    try:
        # Lecture avec détection automatique du séparateur
        df = pd.read_csv(csv_reviews, on_bad_lines='skip', engine='python', sep=None)
    except FileNotFoundError:
        log.error(f"Fichier introuvable : {csv_reviews}")
        raise

    log.info(f"  Total commentaires dans le CSV : {len(df)}")
    log.info(f"  Colonnes reviews : {list(df.columns)}")

    # Trouver la colonne listing_id
    col_listing = None
    for col in df.columns:
        if 'listing' in col.lower() and 'id' in col.lower():
            col_listing = col
            break
    if col_listing is None:
        # Essayer la première colonne
        col_listing = df.columns[0]
        log.warning(f"  Colonne listing_id non trouvée, utilisation de : {col_listing}")

    # Trouver la colonne texte
    col_texte = None
    for col in df.columns:
        if 'comment' in col.lower() or 'text' in col.lower():
            col_texte = col
            break
    if col_texte is None:
        raise ValueError(f"Colonne texte introuvable. Colonnes : {list(df.columns)}")

    log.info(f"  Colonne ID utilisée : {col_listing}")
    log.info(f"  Colonne texte utilisée : {col_texte}")

    # Filtrer sur les IDs Élysée
    df[col_listing] = df[col_listing].astype(str).str.strip()
    df_filtre = df[df[col_listing].isin(ids_cibles)].copy()
    log.info(f"  Commentaires pour l'Élysée : {len(df_filtre)}")

    # Nettoyer les textes
    df_filtre[col_texte] = df_filtre[col_texte].apply(nettoyer_texte)
    df_filtre = df_filtre[df_filtre[col_texte].str.len() > 0]

    # Regrouper par listing_id
    groupes = df_filtre.groupby(col_listing)[col_texte].apply(list).to_dict()
    log.info(f"  Annonces avec commentaires : {len(groupes)}")

    return groupes


def ecrire_fichier_texte(listing_id, commentaires, output_dir, overwrite):
    """Crée le fichier <ID>.txt avec tous les commentaires."""
    dest_path = os.path.join(output_dir, f"{listing_id}.txt")

    # IDEMPOTENCE
    if os.path.exists(dest_path) and not overwrite:
        return "skip"

    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(f"Commentaires pour l'annonce {listing_id}:\n")
            f.write("=" * 50 + "\n\n")
            for i, commentaire in enumerate(commentaires, 1):
                f.write(f"• Avis {i} :\n{commentaire}\n\n")
        return "succes"
    except Exception as e:
        log.warning(f"  Erreur pour l'ID {listing_id} : {e}")
        return "erreur"


# ══════════════════════════════════════════════════════════════
# 4. PROGRAMME PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    log.info("=" * 60)
    log.info("  ImmoVision 360 — Ingestion des textes (Phase 1)")
    log.info(f"  Quartier cible : {QUARTIER_CIBLE}")
    log.info(f"  Mode overwrite : {OVERWRITE}")
    log.info("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ids_elysee = charger_ids_elysee(CSV_LISTINGS, QUARTIER_CIBLE)
    groupes = charger_reviews(CSV_REVIEWS, ids_elysee)

    if not groupes:
        log.error("Aucun commentaire à traiter. Arrêt du script.")
        return

    nb_succes  = 0
    nb_skips   = 0
    nb_erreurs = 0
    total      = len(groupes)

    log.info(f"\nCréation de {total} fichiers texte...\n")

    for i, (listing_id, commentaires) in enumerate(groupes.items(), 1):
        log.info(f"  [{i}/{total}] ID {listing_id} — {len(commentaires)} commentaire(s)")

        resultat = ecrire_fichier_texte(listing_id, commentaires, OUTPUT_DIR, OVERWRITE)

        if resultat == "succes":
            nb_succes += 1
        elif resultat == "skip":
            nb_skips += 1
            log.info(f"    Skip (déjà présent)")
        else:
            nb_erreurs += 1

    # RAPPORT FINAL
    taux = round((nb_succes + nb_skips) / total * 100, 1) if total > 0 else 0

    log.info("\n" + "=" * 60)
    log.info("  RAPPORT D'AUDIT — Ingestion Textes")
    log.info("=" * 60)
    log.info(f"  Total annonces avec commentaires : {total}")
    log.info(f"  Fichiers créés                   : {nb_succes}")
    log.info(f"  Fichiers déjà présents (skip)    : {nb_skips}")
    log.info(f"  Erreurs                          : {nb_erreurs}")
    log.info(f"  Taux de complétion               : {taux} %")
    log.info(f"\n  Log sauvegardé dans : {LOG_FILE}")
    log.info("=" * 60)
    log.info("  Script terminé. Prochaine étape : 03_sanity_check.py")
    log.info("=" * 60)


if __name__ == "__main__":
    main()