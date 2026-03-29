"""
01_ingestion_images.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Projet   : ImmoVision 360 — Gentrification de l'Élysée (Paris)
Phase    : 1 — Collecte & Ingestion (Data Lake)
Objectif : Télécharger les photos des appartements du quartier
           Élysée depuis les URLs contenues dans listings.csv,
           les redimensionner à 320×320 px et les stocker sous
           le nom <ID>.jpg dans /data/raw/images/.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import time
import logging
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# ══════════════════════════════════════════════════════════════
# 1. CONFIGURATION
# ══════════════════════════════════════════════════════════════

# Chemins relatifs depuis IMMOVISION360_DATALAKE/
CSV_PATH   = "data/raw/tabular/listings.csv"
OUTPUT_DIR = "data/raw/images/"
LOG_FILE   = "data/raw/ingestion_images.log"

# Quartier cible
QUARTIER_CIBLE = "Élysée"

# Taille des images sauvegardées
IMAGE_SIZE = (320, 320)

# Pause entre chaque téléchargement (secondes) — respecter les serveurs
SLEEP_BETWEEN_REQUESTS = 0.8

# Timeout d'une requête (secondes)
REQUEST_TIMEOUT = 10

# En-tête HTTP — identification transparente du script
HEADERS = {
    "User-Agent": (
        "ImmoVision360-AcademicBot/1.0 "
        "(Projet Data Science academique, usage non-commercial)"
    )
}

# ══════════════════════════════════════════════════════════════
# 2. LOGGER — écrit dans la console ET dans un fichier .log
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

def charger_catalogue(csv_path, quartier):
    """Lit listings.csv et filtre sur le quartier cible."""
    log.info(f"Lecture du catalogue : {csv_path}")

    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except FileNotFoundError:
        log.error(f"Fichier introuvable : {csv_path}")
        log.error("Vérifie que listings.csv est bien dans data/raw/tabular/")
        raise

    log.info(f"Total annonces dans le CSV : {len(df)}")

    # Trouver la colonne quartier
    col_quartier = None
    for candidate in ["neighbourhood_cleansed", "neighbourhood"]:
        if candidate in df.columns:
            col_quartier = candidate
            break

    if col_quartier is None:
        log.error("Colonne quartier introuvable dans le CSV.")
        raise ValueError("Colonne 'neighbourhood' manquante.")

    # Afficher tous les quartiers disponibles
    quartiers_dispo = sorted(df[col_quartier].dropna().unique())
    log.info(f"Quartiers disponibles : {quartiers_dispo}")

    # Filtrer sur le quartier cible
    df_filtre = df[df[col_quartier].str.contains(quartier, case=False, na=False)].copy()
    log.info(f"Annonces dans '{quartier}' : {len(df_filtre)}")

    if df_filtre.empty:
        log.warning(f"Aucune annonce trouvée pour '{quartier}'.")
        log.warning("Vérifie l'orthographe exacte dans la liste ci-dessus.")

    # Garder uniquement les colonnes utiles
    df_filtre = df_filtre[["id", "picture_url"]].dropna()
    df_filtre["id"] = df_filtre["id"].astype(str).str.strip()

    return df_filtre


def image_deja_presente(image_id, output_dir):
    """Idempotence : vérifie si l'image existe déjà sur le disque."""
    return os.path.exists(os.path.join(output_dir, f"{image_id}.jpg"))


def telecharger_et_sauvegarder(image_id, url, output_dir):
    """
    Télécharge l'image, la redimensionne à 320x320 et la sauvegarde.
    Retourne True si succès, False si erreur.
    Ne plante jamais (try/except sur tout).
    """
    dest_path = os.path.join(output_dir, f"{image_id}.jpg")

    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, stream=True)

        if response.status_code == 404:
            log.warning(f"  Lien mort (404) pour l'ID {image_id}")
            return False

        response.raise_for_status()

        # Ouvrir l'image et convertir en RGB
        img = Image.open(BytesIO(response.content))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        # Redimensionner à 320x320
        img = img.resize(IMAGE_SIZE, Image.LANCZOS)

        # Sauvegarder
        img.save(dest_path, "JPEG", quality=85, optimize=True)
        return True

    except requests.exceptions.Timeout:
        log.warning(f"  Timeout pour l'ID {image_id}")
        return False
    except requests.exceptions.ConnectionError:
        log.warning(f"  Erreur de connexion pour l'ID {image_id}")
        return False
    except requests.exceptions.RequestException as e:
        log.warning(f"  Erreur HTTP pour l'ID {image_id} : {e}")
        return False
    except Exception as e:
        log.warning(f"  Erreur inattendue pour l'ID {image_id} : {e}")
        return False


# ══════════════════════════════════════════════════════════════
# 4. PROGRAMME PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    log.info("=" * 60)
    log.info("  ImmoVision 360 — Ingestion des images (Phase 1)")
    log.info(f"  Quartier cible : {QUARTIER_CIBLE}")
    log.info("=" * 60)

    # Créer le dossier images s'il n'existe pas
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Charger le catalogue filtré
    df = charger_catalogue(CSV_PATH, QUARTIER_CIBLE)
    total_attendu = len(df)

    if total_attendu == 0:
        log.error("Aucune donnée à traiter. Arrêt du script.")
        return

    # Compteurs
    nb_succes     = 0
    nb_skips      = 0
    nb_erreurs    = 0
    ids_orphelins = []

    log.info(f"\nDébut du téléchargement de {total_attendu} images...\n")

    # Boucle principale
    for index, row in df.iterrows():
        image_id  = str(row["id"])
        image_url = str(row["picture_url"])
        numero    = nb_succes + nb_skips + nb_erreurs + 1

        # IDEMPOTENCE — skip si déjà présente
        if image_deja_presente(image_id, OUTPUT_DIR):
            nb_skips += 1
            log.info(f"  [{numero}/{total_attendu}] Skip (déjà présente) -> ID {image_id}")
            continue

        log.info(f"  [{numero}/{total_attendu}] Téléchargement -> ID {image_id}")

        succes = telecharger_et_sauvegarder(image_id, image_url, OUTPUT_DIR)

        if succes:
            nb_succes += 1
        else:
            nb_erreurs += 1
            ids_orphelins.append(image_id)

        # RATE LIMITING — pause entre chaque requête
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # ══════════════════════════════════════════════════════════
    # 5. RAPPORT FINAL
    # ══════════════════════════════════════════════════════════
    taux = round((nb_succes + nb_skips) / total_attendu * 100, 1) if total_attendu > 0 else 0

    log.info("\n" + "=" * 60)
    log.info("  RAPPORT D'AUDIT — Ingestion Images")
    log.info("=" * 60)
    log.info(f"  Total annonces attendues  : {total_attendu}")
    log.info(f"  Images téléchargées       : {nb_succes}")
    log.info(f"  Images déjà présentes     : {nb_skips}")
    log.info(f"  Erreurs / liens morts     : {nb_erreurs}")
    log.info(f"  Taux de complétion        : {taux} %")

    if ids_orphelins:
        log.info(f"\n  5 premiers IDs orphelins :")
        for oid in ids_orphelins[:5]:
            log.info(f"     -> {oid}")

    log.info(f"\n  Log sauvegardé dans : {LOG_FILE}")
    log.info("=" * 60)
    log.info("  Script terminé. Prochaine étape : 02_ingestion_textes.py")
    log.info("=" * 60)


if __name__ == "__main__":
    main()