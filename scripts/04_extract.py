import os
import pandas as pd
import logging
 
# ---------------------------------------------------------------------------
# 0. CONFIGURATION
# ---------------------------------------------------------------------------
 
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CSV_INPUT   = os.path.join(BASE_DIR, "..", "data", "raw", "tabular", "listings.csv")
OUTPUT_DIR  = os.path.join(BASE_DIR, "..", "data", "processed")
CSV_OUTPUT  = os.path.join(OUTPUT_DIR, "filtered_elysee.csv")
 
QUARTIER_CIBLE = "Élysée"
 
# ---------------------------------------------------------------------------
# Colonnes utiles — mappées aux 3 hypothèses
# ---------------------------------------------------------------------------
COLS_TO_KEEP = [
    # -- Identifiant (clé de jointure avec images et textes)
    "id",
 
    # -- Hypothèse A : Concentration économique (Machine à Cash)
    "host_id",                              # Pour regrouper par hôte
    "calculated_host_listings_count",       # Nombre de biens gérés par l'hôte
    "price",                                # Prix par nuitée
    "availability_365",                     # Disponibilité annuelle
    "property_type",                        # Type de bien
    "room_type",                            # Logement entier vs chambre
 
    # -- Hypothèse B : Déshumanisation (Lien Social)
    "host_response_time",                   # Temps de réponse (agence = rapide)
    "host_response_rate",                   # Taux de réponse
    "host_is_superhost",                    # Superhost = professionnel ?
    "host_identity_verified",              # Vérification identité
 
    # -- Avis et notes (complément hypothèse B)
    "number_of_reviews",
    "review_scores_rating",
    "review_scores_communication",
    "review_scores_checkin",
    "reviews_per_month",
 
    # -- Hypothèse C : Standardisation visuelle (Image)
    "picture_url",                          # Lien image (pour vérification jointure)
 
    # -- Géographie
    "neighbourhood_cleansed",
    "latitude",
    "longitude",
]
 
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
# 2. PIPELINE
# ---------------------------------------------------------------------------
 
def extraire():
 
    # -- Création du dossier processed si inexistant
    os.makedirs(OUTPUT_DIR, exist_ok=True)
 
    # -- Idempotence : skip si déjà produit
    if os.path.exists(CSV_OUTPUT):
        log.info(f"Fichier déjà présent : {CSV_OUTPUT} — skip (idempotence).")
        log.info("Utilisez --overwrite pour forcer la ré-extraction.")
        return
 
    # -- Chargement du CSV brut
    log.info(f"Chargement du CSV brut : {CSV_INPUT}")
    df = pd.read_csv(CSV_INPUT, low_memory=False)
    log.info(f"Lignes totales : {len(df)} | Colonnes totales : {len(df.columns)}")
 
    # -- Filtrage géographique
    df_elysee = df[df["neighbourhood_cleansed"] == QUARTIER_CIBLE].copy()
    log.info(f"Annonces dans '{QUARTIER_CIBLE}' : {len(df_elysee)}")
 
    # -- Vérification des colonnes manquantes
    manquantes = [c for c in COLS_TO_KEEP if c not in df_elysee.columns]
    if manquantes:
        log.warning(f"Colonnes absentes du CSV (ignorées) : {manquantes}")
    cols_valides = [c for c in COLS_TO_KEEP if c in df_elysee.columns]
 
    # -- Sélection des colonnes utiles
    df_filtre = df_elysee[cols_valides].copy()
    log.info(f"Colonnes conservées : {len(cols_valides)} / {len(df.columns)}")
 
    # -- Sauvegarde Zone Silver
    df_filtre.to_csv(CSV_OUTPUT, index=False, encoding="utf-8-sig")
    log.info(f"Fichier Silver produit : {CSV_OUTPUT}")
 
    # -- Rapport
    log.info("=" * 60)
    log.info("RAPPORT EXTRACT")
    log.info(f"  Annonces extraites  : {len(df_filtre)}")
    log.info(f"  Colonnes retenues   : {len(cols_valides)}")
    log.info(f"  Colonnes supprimées : {len(df.columns) - len(cols_valides)}")
    log.info("=" * 60)
 
 
# ---------------------------------------------------------------------------
# 3. POINT D'ENTREE
# ---------------------------------------------------------------------------
 
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true",
                        help="Ré-extrait même si le fichier existe déjà.")
    args = parser.parse_args()
 
    if args.overwrite and os.path.exists(CSV_OUTPUT):
        os.remove(CSV_OUTPUT)
        log.info("Mode overwrite : fichier existant supprimé.")
 
    extraire()