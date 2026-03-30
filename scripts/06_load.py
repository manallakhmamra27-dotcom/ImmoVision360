
import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
 
# ---------------------------------------------------------------------------
# 0. CONFIGURATION
# ---------------------------------------------------------------------------
 
load_dotenv()
 
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CSV_SILVER  = os.path.join(BASE_DIR, "..", "data", "processed", "transformed_elysee.csv")
 
# Connexion PostgreSQL via variables d'environnement (.env)
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "immovision_db")
 
TABLE_NAME  = "elysee_listings_silver"
 
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
 
def charger():
 
    # -- Vérification que le fichier Silver existe
    if not os.path.exists(CSV_SILVER):
        raise FileNotFoundError(
            f"Fichier Silver introuvable : {CSV_SILVER}\n"
            "Lancez d'abord 05_transform.py"
        )
 
    # -- Chargement du CSV Silver
    log.info(f"Chargement du fichier Silver : {CSV_SILVER}")
    df = pd.read_csv(CSV_SILVER, low_memory=False)
    log.info(f"Lignes a charger : {len(df)} | Colonnes : {len(df.columns)}")
 
    # -- Connexion PostgreSQL
    connection_string = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    log.info(f"Connexion a PostgreSQL : {DB_HOST}:{DB_PORT}/{DB_NAME}")
 
    try:
        engine = create_engine(connection_string)
 
        # -- Test de connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log.info("Connexion PostgreSQL etablie avec succes.")
 
    except Exception as e:
        log.error(f"Impossible de se connecter a PostgreSQL : {e}")
        log.error("Verifiez vos identifiants dans le fichier .env")
        raise
 
    # -- Injection (idempotence via if_exists='replace')
    log.info(f"Injection dans la table : {TABLE_NAME}")
    try:
        df.to_sql(
            TABLE_NAME,
            engine,
            if_exists="replace",    # Recrée la table à chaque run (idempotence)
            index=False,
            chunksize=500,          # Insertion par lots de 500 lignes
        )
        log.info(f"Injection reussie : {len(df)} lignes chargees.")
 
    except Exception as e:
        log.error(f"Erreur lors de l'injection : {e}")
        raise
 
    # -- Verification post-load
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
        count = result.fetchone()[0]
    log.info(f"Verification PostgreSQL : {count} lignes dans '{TABLE_NAME}'.")
 
    # -- Rapport final
    log.info("=" * 60)
    log.info("RAPPORT LOAD")
    log.info(f"  Table cible     : {TABLE_NAME}")
    log.info(f"  Base de donnees : {DB_NAME}")
    log.info(f"  Lignes injectees: {count}")
    log.info(f"  Colonnes        : {list(df.columns)}")
    log.info("=" * 60)
    log.info("Data Warehouse pret. Phase 3 peut commencer.")
 
 
# ---------------------------------------------------------------------------
# 3. POINT D'ENTREE
# ---------------------------------------------------------------------------
 
if __name__ == "__main__":
    charger()