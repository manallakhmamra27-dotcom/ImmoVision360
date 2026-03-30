import os
import random
import logging
import argparse
import pandas as pd
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 0. CONFIGURATION
# ---------------------------------------------------------------------------

load_dotenv()

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CSV_INPUT  = os.path.join(BASE_DIR, "..", "data", "processed", "filtered_elysee.csv")
CSV_OUTPUT = os.path.join(BASE_DIR, "..", "data", "processed", "transformed_elysee.csv")

# ---------------------------------------------------------------------------
# 1. LOGGING
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 2. FONCTIONS DE NETTOYAGE
# ---------------------------------------------------------------------------

def nettoyer_prix(df):
    """Prix non disponible dans ce fichier — nettoyage ignoré."""
    log.info("Nettoyage prix ignoré — colonne non disponible.")
    return df


def nettoyer_nan(df):
    """Gestion des valeurs manquantes par stratégie métier."""

    cols_mediane = [
        "review_scores_rating",
        "review_scores_communication",
        "review_scores_checkin",
    ]
    for col in cols_mediane:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    if "reviews_per_month" in df.columns:
        df["reviews_per_month"] = df["reviews_per_month"].fillna(0)

    for col in ["host_response_time", "host_response_rate"]:
        if col in df.columns:
            df[col] = df[col].fillna("N/A")

    log.info("Valeurs manquantes traitées.")
    return df


# ---------------------------------------------------------------------------
# 3. FONCTIONS IA (simulées — quota API dépassé)
# ---------------------------------------------------------------------------

def analyser_image(listing_id):
    """
    Simulation de l'analyse image par Gemini.
    En production : appel réel à l'API Google Gemini Vision.
    """
    return random.choice([
        "Appartement industrialisé",
        "Appartement personnel",
        "Autre"
    ])


def analyser_texte(listing_id):
    """
    Simulation de l'analyse texte par Gemini.
    En production : appel réel à l'API Google Gemini NLP.
    """
    return random.choice([
        "Hôtélisé",
        "Voisinage naturel",
        "Neutre"
    ])


# ---------------------------------------------------------------------------
# 4. PIPELINE PRINCIPALE
# ---------------------------------------------------------------------------

def transformer(overwrite=False):

    # -- Idempotence
    if not overwrite and os.path.exists(CSV_OUTPUT):
        log.info("Fichier déjà présent — skip (idempotence).")
        log.info("Utilisez --overwrite pour forcer la re-transformation.")
        return

    # -- Chargement
    log.info(f"Chargement : {CSV_INPUT}")
    df = pd.read_csv(CSV_INPUT, low_memory=False)
    log.info(f"Lignes chargées : {len(df)}")

    # -- Nettoyage
    log.info("--- Nettoyage en cours ---")
    df = nettoyer_prix(df)
    df = nettoyer_nan(df)
    log.info(f"Lignes après nettoyage : {len(df)}")

    # -- Enrichissement IA
    log.info("--- Enrichissement IA en cours (simulation) ---")

    standardization_scores = []
    neighborhood_impacts   = []

    for _, row in df.iterrows():
        listing_id = str(int(row["id"]))

        score_image  = analyser_image(listing_id)
        impact_texte = analyser_texte(listing_id)

        standardization_scores.append(score_image)
        neighborhood_impacts.append(impact_texte)

        log.info(f"  ID {listing_id} -> Image: {score_image} | Texte: {impact_texte}")

    df["Standardization_Score"] = standardization_scores
    df["Neighborhood_Impact"]   = neighborhood_impacts

    # -- Sauvegarde
    df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8-sig")
    log.info(f"Fichier Silver enrichi produit : {CSV_OUTPUT}")

    # -- Rapport final
    log.info("=" * 60)
    log.info("RAPPORT TRANSFORM")
    log.info(f"  Lignes traitées       : {len(df)}")
    log.info(f"  Standardization_Score : {df['Standardization_Score'].value_counts().to_dict()}")
    log.info(f"  Neighborhood_Impact   : {df['Neighborhood_Impact'].value_counts().to_dict()}")
    log.info("=" * 60)


# ---------------------------------------------------------------------------
# 5. POINT D'ENTREE
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    transformer(overwrite=args.overwrite)
 