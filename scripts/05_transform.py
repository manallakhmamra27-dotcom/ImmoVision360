"""
=============================================================================
ImmoVision 360 — Script 05 : Transform
=============================================================================
Mission   : Nettoyer le fichier filtré et l'enrichir avec des scores IA.
            - Feature 1 : Standardization_Score (1, 0 ou -1)
            - Feature 2 : Neighborhood_Impact   (1, 0 ou -1)
            Produit : data/processed/transformed_elysee.csv
Phase     : 2 — ETL (Transform)
Note      : Valeurs simulées par génération aléatoire (1, 0, -1)
            conformément aux consignes du professeur.
=============================================================================
"""

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

    # Imputation par médiane (notes)
    cols_mediane = [
        "review_scores_rating",
        "review_scores_communication",
        "review_scores_checkin",
    ]
    for col in cols_mediane:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Imputation logique : 0 si pas encore de commentaires
    if "reviews_per_month" in df.columns:
        df["reviews_per_month"] = df["reviews_per_month"].fillna(0)

    # Imputation logique : "N/A" pour les colonnes textuelles
    for col in ["host_response_time", "host_response_rate"]:
        if col in df.columns:
            df[col] = df[col].fillna("N/A")

    log.info("Valeurs manquantes traitées.")
    return df


# ---------------------------------------------------------------------------
# 3. FONCTIONS IA (valeurs aléatoires 1, 0, -1)
# ---------------------------------------------------------------------------

def analyser_image(listing_id):
    """
    Simulation du score de standardisation visuelle.
     1  = Appartement personnel (authentique)
     0  = Neutre / Autre
    -1  = Appartement industrialisé (standardisé)
    En production : appel réel à Google Gemini Vision.
    """
    return random.choice([1, 0, -1])


def analyser_texte(listing_id):
    """
    Simulation du score d'impact social.
     1  = Voisinage naturel (accueil humain)
     0  = Neutre
    -1  = Hôtélisé (accueil impersonnel)
    En production : appel réel à Google Gemini NLP.
    """
    return random.choice([1, 0, -1])


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
    log.info("--- Enrichissement IA en cours (simulation 1/0/-1) ---")

    standardization_scores = []
    neighborhood_impacts   = []

    for _, row in df.iterrows():
        listing_id = str(int(row["id"]))
        standardization_scores.append(analyser_image(listing_id))
        neighborhood_impacts.append(analyser_texte(listing_id))

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
 