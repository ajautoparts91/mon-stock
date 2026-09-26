import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestion Stock & Prix Dynamiques", layout="wide")

st.title("⚙️ Dashboard de Tarification Dynamique & Trésorerie")

@st.cache_data
def load_data():
    df = pd.read_csv("inventaire_pieces_26092026_674.csv", sep=';')
    df['Date_creation_dt'] = pd.to_datetime(df['Date creation'], format='%d/%m/%Y', errors='coerce')
    
    # Date actuelle
    ref_date = datetime.now()
    df['Jours_en_stock'] = (ref_date - df['Date_creation_dt']).dt.days.fillna(0).astype(int)
    
    # Calcul des suggestions de prix
    def calculer_prix_suggere(row):
        prix = row['PrixTotalTTC']
        jours = row['Jours_en_stock']
        if jours > 365:
            return round(prix * 0.80, 2)  # Remise de 20% si > 1 an
        elif jours > 180:
            return round(prix * 0.90, 2)  # Remise de 10% si > 6 mois
        return prix

    def recommandation(row):
        jours = row['Jours_en_stock']
        if jours > 365:
            return "🔴 Urgent : Baisse -20% (Stock > 1 an)"
        elif jours > 180:
            return "🟠 Promotion : Baisse -10% (Stock > 6 mois)"
        return "🟢 Prix Optimal"

    df['Prix_Suggere_TTC'] = df.apply(calculer_prix_suggere, axis=1)
    df['Action'] = df.apply(recommandation, axis=1)
    return df

try:
    df = load_data()

    # Indicateurs clés
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Valeur Totale du Stock", f"{df['PrixTotalTTC'].sum():,} €".replace(',', ' '))
    c2.metric("Moteurs en Stock", len(df))
    
    stock_6m = df[df['Jours_en_stock'] > 180]
    c3.metric("Trésorerie Immobilisée (> 6 mois)", f"{stock_6m['PrixTotalTTC'].sum():,} €".replace(',', ' '), f"{len(stock_6m)} pièces")
    
    stock_1y = df[df['Jours_en_stock'] > 365]
    c4.metric("Trésorerie Immobilisée (> 1 an)", f"{stock_1y['PrixTotalTTC'].sum():,} €".replace(',', ' '), f"{len(stock_1y)} pièces")

    st.markdown("---")

    # Filtres latéraux
    st.sidebar.header("🔍 Filtres & Recherche")
    recherche = st.sidebar.text_input("Rechercher (Ex: K10B, Clio, R2/A9)")
    marques = st.sidebar.multiselect("Filtrer par Marque", options=sorted(df['Marque'].dropna().unique()))
    actions = st.sidebar.multiselect("Filtrer par Action", options=df['Action'].unique())

    # Application des filtres
    df_filtered = df.copy()
    if recherche:
        df_filtered = df_filtered[
            df_filtered['Moteur'].str.contains(recherche, case=False, na=False) |
            df_filtered['Modele'].str.contains(recherche, case=False, na=False) |
            df_filtered['Emplacement'].str.contains(recherche, case=False, na=False)
        ]
    if marques:
        df_filtered = df_filtered[df_filtered['Marque'].isin(marques)]
    if actions:
        df_filtered = df_filtered[df_filtered['Action'].isin(actions)]

    # Affichage du tableau de décision
    st.subheader("📋 Liste des Pièces & Recommandations de Prix")
    st.dataframe(
        df_filtered[['Nom', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Prix_Suggere_TTC', 'Jours_en_stock', 'Action', 'Emplacement']],
        use_container_width=True
    )

except Exception as e:
    st.error(f"Veuillez vérifier que le fichier 'inventaire_pieces_26092026_674.csv' est bien présent dans le même dossier. Erreur : {e}")