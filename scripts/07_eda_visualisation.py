

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# 0. CONFIGURATION
# ---------------------------------------------------------------------------

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CSV_SILVER  = os.path.join(BASE_DIR, "..", "data", "processed", "transformed_elysee.csv")
OUTPUT_DIR  = os.path.join(BASE_DIR, "..", "data", "processed", "visualisations")

# Style global
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"]      = 11

# ---------------------------------------------------------------------------
# 1. CHARGEMENT
# ---------------------------------------------------------------------------

def charger_donnees():
    print("=" * 60)
    print("  ImmoVision 360 — Phase 3 : EDA & Visualisation")
    print("=" * 60)
    print(f"\nChargement : {CSV_SILVER}")

    df = pd.read_csv(CSV_SILVER, low_memory=False)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Lignes chargées     : {len(df)}")
    print(f"Colonnes disponibles: {list(df.columns)}\n")
    return df

# ---------------------------------------------------------------------------
# 2. ANALYSE DESCRIPTIVE (Vue d'ensemble)
# ---------------------------------------------------------------------------

def analyse_descriptive(df):
    print("=" * 60)
    print("  ÉTAPE 1 — Analyse Descriptive")
    print("=" * 60)

    print("\n--- Types de propriétés ---")
    print(df["property_type"].value_counts().head(10))

    print("\n--- Types de location ---")
    print(df["room_type"].value_counts())

    print("\n--- Valeurs manquantes (%) ---")
    missing = (df.isnull().sum() / len(df) * 100).round(2)
    print(missing[missing > 0])

    # Graphique 1 — Répartition des types de location
    fig, ax = plt.subplots()
    df["room_type"].value_counts().plot(
        kind="bar", ax=ax, color=["#2196F3", "#FF9800", "#4CAF50", "#F44336"]
    )
    ax.set_title("Répartition des types de location — Élysée", fontsize=13, fontweight="bold")
    ax.set_xlabel("Type de location")
    ax.set_ylabel("Nombre d'annonces")
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "01_types_location.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n✅ Graphique sauvegardé : {path}")

# ---------------------------------------------------------------------------
# 3. HYPOTHÈSE 1 — STANDARDISATION VISUELLE
# ---------------------------------------------------------------------------

def hypothese_standardisation(df):
    print("\n" + "=" * 60)
    print("  ÉTAPE 2 — H1 : Standardisation Visuelle")
    print("=" * 60)

    counts = df["Standardization_Score"].value_counts()
    total  = len(df)
    print("\nDistribution Standardization_Score :")
    for cat, n in counts.items():
        print(f"  {cat:<30} : {n} ({n/total*100:.1f}%)")

    industrialises = counts.get("Appartement industrialisé", 0)
    pct = round(industrialises / total * 100, 1)
    print(f"\n🔍 Conclusion H1 : {pct}% des logements sont industrialisés.")
    if pct > 40:
        print("   ⚠️  ALERTE : Plus de 40% des biens sont standardisés — preuve d'industrialisation.")
    else:
        print("   ✅  Moins de 40% des biens sont standardisés.")

    # Graphique 2 — Camembert Standardisation
    fig, ax = plt.subplots()
    colors = ["#F44336", "#4CAF50", "#FF9800"]
    counts.plot(
        kind="pie", ax=ax, autopct="%1.1f%%",
        colors=colors, startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2}
    )
    ax.set_title("H1 — Standardisation Visuelle des Logements\n(Élysée, Paris)", fontweight="bold")
    ax.set_ylabel("")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "02_standardisation.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✅ Graphique sauvegardé : {path}")

# ---------------------------------------------------------------------------
# 4. HYPOTHÈSE 2 — DÉSHUMANISATION (LIEN SOCIAL)
# ---------------------------------------------------------------------------

def hypothese_deshumanisation(df):
    print("\n" + "=" * 60)
    print("  ÉTAPE 3 — H2 : Déshumanisation du Lien Social")
    print("=" * 60)

    counts = df["Neighborhood_Impact"].value_counts()
    total  = len(df)
    print("\nDistribution Neighborhood_Impact :")
    for cat, n in counts.items():
        print(f"  {cat:<25} : {n} ({n/total*100:.1f}%)")

    hotelises = counts.get("Hôtélisé", 0)
    pct = round(hotelises / total * 100, 1)
    print(f"\n🔍 Conclusion H2 : {pct}% des logements ont un accueil hôtélisé (impersonnel).")
    if pct > 30:
        print("   ⚠️  ALERTE : Le lien social se brise — accueil impersonnel dominant.")
    else:
        print("   ✅  Le lien social reste présent dans la majorité des logements.")

    # Graphique 3 — Barres Neighborhood Impact
    fig, ax = plt.subplots()
    colors = ["#F44336", "#4CAF50", "#FF9800"]
    bars = ax.bar(counts.index, counts.values, color=colors, edgecolor="white", linewidth=1.5)
    ax.set_title("H2 — Impact Social des Logements Airbnb\n(Élysée, Paris)", fontweight="bold")
    ax.set_xlabel("Type d'accueil")
    ax.set_ylabel("Nombre d'annonces")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f"{val/total*100:.1f}%", ha="center", fontweight="bold")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "03_deshumanisation.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✅ Graphique sauvegardé : {path}")

    # Graphique 4 — Croisement Standardisation x Impact Social
    fig, ax = plt.subplots(figsize=(11, 6))
    crosstab = pd.crosstab(
        df["Standardization_Score"],
        df["Neighborhood_Impact"],
        normalize="index"
    ) * 100
    crosstab.plot(kind="bar", ax=ax, colormap="Set2", edgecolor="white")
    ax.set_title("Croisement : Standardisation vs Impact Social\n(% par catégorie)", fontweight="bold")
    ax.set_xlabel("Score de Standardisation")
    ax.set_ylabel("% de logements")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(title="Impact Social", bbox_to_anchor=(1.05, 1))
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "04_croisement_std_social.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✅ Graphique sauvegardé : {path}")

# ---------------------------------------------------------------------------
# 5. HYPOTHÈSE 3 — MACHINE À CASH (CONCENTRATION)
# ---------------------------------------------------------------------------

def hypothese_machine_cash(df):
    print("\n" + "=" * 60)
    print("  ÉTAPE 4 — H3 : Machine à Cash (Concentration des biens)")
    print("=" * 60)

    # Concentration par hôte
    host_counts = df.groupby("host_id")["id"].count().sort_values(ascending=False)
    total_biens = len(df)
    total_hotes = len(host_counts)

    # Top 5% des hôtes
    top5_pct    = max(1, int(total_hotes * 0.05))
    top5_biens  = host_counts.head(top5_pct).sum()
    pct_controle = round(top5_biens / total_biens * 100, 1)

    print(f"\nTotal hôtes uniques  : {total_hotes}")
    print(f"Total annonces       : {total_biens}")
    print(f"Top 5% hôtes ({top5_pct}) contrôlent : {top5_biens} biens ({pct_controle}%)")

    if pct_controle > 30:
        print(f"\n⚠️  ALERTE : Les {top5_pct} plus gros hôtes contrôlent {pct_controle}% du marché !")
        print("   Preuve d'une gestion industrielle concentrée.")
    else:
        print(f"\n✅  La concentration reste modérée ({pct_controle}%).")

    # Graphique 5 — Distribution des annonces par hôte
    fig, ax = plt.subplots()
    host_counts_clipped = host_counts.clip(upper=20)
    ax.hist(host_counts_clipped, bins=20, color="#2196F3", edgecolor="white", linewidth=1.2)
    ax.set_title("H3 — Distribution des annonces par hôte\n(Élysée, Paris)", fontweight="bold")
    ax.set_xlabel("Nombre d'annonces par hôte")
    ax.set_ylabel("Nombre d'hôtes")
    ax.axvline(x=host_counts.mean(), color="#F44336", linestyle="--",
               label=f"Moyenne : {host_counts.mean():.1f}")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "05_concentration_hotes.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✅ Graphique sauvegardé : {path}")

    # Graphique 6 — Top 20 hôtes (multi-propriétaires)
    fig, ax = plt.subplots(figsize=(11, 6))
    top20 = host_counts.head(20)
    bars = ax.bar(range(len(top20)), top20.values, color="#FF5722", edgecolor="white")
    ax.set_title("Top 20 Hôtes — Nombre d'annonces\n(Potentiels acteurs industriels)", fontweight="bold")
    ax.set_xlabel("Hôte (anonymisé)")
    ax.set_ylabel("Nombre d'annonces")
    ax.set_xticks(range(len(top20)))
    ax.set_xticklabels([f"H{i+1}" for i in range(len(top20))], rotation=45)
    for bar, val in zip(bars, top20.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(val), ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "06_top20_hotes.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✅ Graphique sauvegardé : {path}")

    # Graphique 7 — Disponibilité annuelle
    if "availability_365" in df.columns:
        fig, ax = plt.subplots()
        ax.hist(df["availability_365"].dropna(), bins=30,
                color="#9C27B0", edgecolor="white", linewidth=1.2)
        ax.set_title("Disponibilité Annuelle des Logements\n(0 = jamais dispo / 365 = toujours dispo)",
                     fontweight="bold")
        ax.set_xlabel("Jours disponibles par an")
        ax.set_ylabel("Nombre d'annonces")
        ax.axvline(x=df["availability_365"].mean(), color="#F44336", linestyle="--",
                   label=f"Moyenne : {df['availability_365'].mean():.0f} jours")
        ax.legend()
        plt.tight_layout()
        path = os.path.join(OUTPUT_DIR, "07_disponibilite.png")
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"✅ Graphique sauvegardé : {path}")

# ---------------------------------------------------------------------------
# 6. CARTE DE CHALEUR (Localisation GPS)
# ---------------------------------------------------------------------------

def carte_localisation(df):
    print("\n" + "=" * 60)
    print("  ÉTAPE 5 — Carte de localisation des logements")
    print("=" * 60)

    if "latitude" not in df.columns or "longitude" not in df.columns:
        print("  Colonnes GPS manquantes — carte ignorée.")
        return

    fig, ax = plt.subplots(figsize=(10, 8))

    # Couleur selon Standardization_Score
    color_map = {
        "Appartement industrialisé": "#F44336",
        "Appartement personnel":      "#4CAF50",
        "Autre":                      "#FF9800"
    }
    for cat, color in color_map.items():
        subset = df[df["Standardization_Score"] == cat]
        ax.scatter(subset["longitude"], subset["latitude"],
                   c=color, label=cat, alpha=0.5, s=15)

    ax.set_title("Carte des Logements Airbnb — Élysée\n(Rouge = Industrialisé / Vert = Personnel)",
                 fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="upper right", fontsize=9)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "08_carte_localisation.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"✅ Graphique sauvegardé : {path}")

# ---------------------------------------------------------------------------
# 7. RAPPORT FINAL EN CONSOLE
# ---------------------------------------------------------------------------

def rapport_final(df):
    print("\n" + "=" * 60)
    print("  RAPPORT DÉCISIONNEL — ImmoVision 360")
    print("  Pour la Maire de Paris")
    print("=" * 60)

    total = len(df)
    std   = df["Standardization_Score"].value_counts(normalize=True) * 100
    imp   = df["Neighborhood_Impact"].value_counts(normalize=True) * 100

    host_counts  = df.groupby("host_id")["id"].count()
    top5_pct     = max(1, int(len(host_counts) * 0.05))
    top5_biens   = host_counts.nlargest(top5_pct).sum()
    concentration = round(top5_biens / total * 100, 1)

    print(f"""
  📊 Données analysées    : {total} logements (Quartier Élysée)

  H1 — STANDARDISATION VISUELLE :
     Appartements industrialisés : {std.get('Appartement industrialisé', 0):.1f}%
     Appartements personnels     : {std.get('Appartement personnel', 0):.1f}%

  H2 — DÉSHUMANISATION :
     Accueil hôtélisé            : {imp.get('Hôtélisé', 0):.1f}%
     Voisinage naturel           : {imp.get('Voisinage naturel', 0):.1f}%
     Neutre                      : {imp.get('Neutre', 0):.1f}%

  H3 — CONCENTRATION (Machine à Cash) :
     Top 5% hôtes contrôlent     : {concentration}% des annonces

  📁 Visualisations sauvegardées dans :
     {OUTPUT_DIR}
""")
    print("=" * 60)
    print("  Phase 3 terminée. Rapport prêt pour la Mairie de Paris.")
    print("=" * 60)

# ---------------------------------------------------------------------------
# 8. PIPELINE PRINCIPALE
# ---------------------------------------------------------------------------

def main():
    df = charger_donnees()
    analyse_descriptive(df)
    hypothese_standardisation(df)
    hypothese_deshumanisation(df)
    hypothese_machine_cash(df)
    carte_localisation(df)
    rapport_final(df)

if __name__ == "__main__":
    main()