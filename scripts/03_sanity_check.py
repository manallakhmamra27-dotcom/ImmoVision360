

import os
import logging
import pandas as pd

# ══════════════════════════════════════════════════════════════
# 1. CONFIGURATION
# ══════════════════════════════════════════════════════════════

CSV_LISTINGS = "data/raw/tabular/listings.csv"
IMAGES_DIR   = "data/raw/images/"
TEXTS_DIR    = "data/raw/texts/"
LOG_FILE     = "data/raw/sanity_check.log"

QUARTIER_CIBLE = "Élysée"

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

def charger_ids_elysee(csv_listings, quartier):
    """Retourne la liste des IDs attendus pour le quartier cible."""
    log.info(f"Lecture de listings.csv...")

    try:
        df = pd.read_csv(csv_listings, on_bad_lines='skip', engine='python')
    except FileNotFoundError:
        log.error(f"Fichier introuvable : {csv_listings}")
        raise

    # Trouver la colonne quartier
    col_quartier = None
    for candidate in ["neighbourhood_cleansed", "neighbourhood"]:
        if candidate in df.columns:
            col_quartier = candidate
            break

    if col_quartier is None:
        raise ValueError("Colonne quartier introuvable dans listings.csv")

    df_filtre = df[df[col_quartier].str.contains(quartier, case=False, na=False)]
    ids = df_filtre["id"].astype(str).str.strip().tolist()
    log.info(f"  IDs attendus pour '{quartier}' : {len(ids)}")
    return ids


def compter_fichiers(dossier, extension):
    """Compte les fichiers d'une extension donnée dans un dossier."""
    if not os.path.exists(dossier):
        return 0, []
    fichiers = [f for f in os.listdir(dossier) if f.endswith(extension)]
    return len(fichiers), fichiers


def verifier_jointure(ids_attendus, dossier, extension):
    """
    Jointure physique : vérifie pour chaque ID si le fichier existe.
    Retourne les IDs orphelins (fichiers manquants).
    """
    orphelins = []
    for id_ in ids_attendus:
        chemin = os.path.join(dossier, f"{id_}{extension}")
        if not os.path.exists(chemin):
            orphelins.append(id_)
    return orphelins


# ══════════════════════════════════════════════════════════════
# 4. PROGRAMME PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    log.info("=" * 60)
    log.info("  ImmoVision 360 — Sanity Check du Data Lake")
    log.info(f"  Quartier cible : {QUARTIER_CIBLE}")
    log.info("=" * 60)

    # ── 1. Comptage théorique ──────────────────────────────────
    ids_attendus = charger_ids_elysee(CSV_LISTINGS, QUARTIER_CIBLE)
    total_attendu = len(ids_attendus)

    # ── 2. Comptage physique des images ───────────────────────
    nb_images, _ = compter_fichiers(IMAGES_DIR, ".jpg")

    # ── 3. Comptage physique des textes ───────────────────────
    nb_textes, _ = compter_fichiers(TEXTS_DIR, ".txt")

    # ── 4. Jointure physique — images ─────────────────────────
    log.info("\nVérification des images...")
    orphelins_images = verifier_jointure(ids_attendus, IMAGES_DIR, ".jpg")
    nb_images_ok = total_attendu - len(orphelins_images)
    taux_images = round(nb_images_ok / total_attendu * 100, 1) if total_attendu > 0 else 0

    # ── 5. Jointure physique — textes ─────────────────────────
    log.info("Vérification des textes...")
    orphelins_textes = verifier_jointure(ids_attendus, TEXTS_DIR, ".txt")
    nb_textes_ok = total_attendu - len(orphelins_textes)
    taux_textes = round(nb_textes_ok / total_attendu * 100, 1) if total_attendu > 0 else 0

    # ══════════════════════════════════════════════════════════
    # 5. RAPPORT FINAL
    # ══════════════════════════════════════════════════════════
    log.info("\n" + "=" * 60)
    log.info("  RAPPORT D'AUDIT — Sanity Check Data Lake")
    log.info("=" * 60)

    log.info(f"\n  📊 COMPTAGE GÉNÉRAL")
    log.info(f"  Total annonces CSV (attendues) : {total_attendu}")
    log.info(f"  Images présentes sur le disque : {nb_images}")
    log.info(f"  Textes présents sur le disque  : {nb_textes}")

    log.info(f"\n  🖼️  AUDIT IMAGES")
    log.info(f"  Images trouvées pour les IDs   : {nb_images_ok} / {total_attendu}")
    log.info(f"  Images manquantes (orphelines) : {len(orphelins_images)}")
    log.info(f"  Taux de complétion images      : {taux_images} %")

    if orphelins_images:
        log.info(f"\n  5 premiers IDs sans image :")
        for oid in orphelins_images[:5]:
            log.info(f"     -> {oid}")

    log.info(f"\n  📄 AUDIT TEXTES")
    log.info(f"  Textes trouvés pour les IDs    : {nb_textes_ok} / {total_attendu}")
    log.info(f"  Textes manquants (orphelins)   : {len(orphelins_textes)}")
    log.info(f"  Taux de complétion textes      : {taux_textes} %")

    if orphelins_textes:
        log.info(f"\n  5 premiers IDs sans texte :")
        for oid in orphelins_textes[:5]:
            log.info(f"     -> {oid}")

    log.info(f"\n  💾 Log sauvegardé dans : {LOG_FILE}")
    log.info("=" * 60)

    # Verdict final
    if taux_images >= 90 and taux_textes >= 90:
        log.info("  ✅ Data Lake validé ! Prochaine étape : Phase 2 ETL")
    else:
        log.info("  ⚠️  Taux de complétion insuffisant.")
        log.info("  Relance les scripts 01 et 02 pour compléter le Lake.")
    log.info("=" * 60)


if __name__ == "__main__":
    main()