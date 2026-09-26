import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="VHU Executive - Arbitrage & Opisto", 
    layout="wide", 
    page_icon="🚘"
)

st.title("🚘 VHU Direction — Arbitrage Stock Moteurs & Performance Opisto")
st.caption("Pilotage du BFR, libération d'emplacements et maximisation des ventes Opisto")

# --- MODULE D'IMPORTATION OPISTO ---
st.sidebar.header("📂 Mise à jour de l'inventaire Opisto")
uploaded_file = st.sidebar.file_uploader("Importer le dernier export CSV Opisto", type=['csv'])

@st.cache_data
def process_data(file_source):
    df = pd.read_csv(file_source, sep=';')
    df['Date_creation_dt'] = pd.to_datetime(df['Date creation'], format='%d/%m/%Y', errors='coerce')
    
    ref_date = datetime.now()
    df['Jours_en_stock'] = (ref_date - df['Date_creation_dt']).dt.days.fillna(0).astype(int)
    
    # Stratégie Arbitrage VHU / Opisto
    def classifier_moteur(row):
        prix = row['PrixTotalTTC']
        jours = row['Jours_en_stock']
        
        if jours > 365 and prix < 400:
            return "♻️ RECYCLAGE (Proposer Ferraille)"
        elif jours > 365 and prix >= 400:
            return "🚨 CRITIQUE : Baisse de prix agressive Opisto (-30%)"
        elif 180 < jours <= 365 and prix >= 1000:
            return "⭐ PÉPITE DORMANTE : Revoir Fiche/Photos Opisto (-10%)"
        elif 180 < jours <= 365:
            return "🟠 PROMOTION : Baisse de prix Opisto (-15%)"
        elif jours <= 90 and prix >= 1200:
            return "🔥 TOP VENTE OPISTO (Ne pas baisser le prix)"
        return "🟢 STOCK NORMAL"

    df['Decision_IA'] = df.apply(classifier_moteur, axis=1)
    return df

try:
    if uploaded_file is not None:
        df = process_data(uploaded_file)
        st.sidebar.success("✅ Nouvel inventaire Opisto chargé !")
    else:
        df = process_data("inventaire_pieces_26092026_674.csv")

    # --- KPIS GRAND PATRON VHU ---
    st.subheader("📊 Arbitrage Financier & Gestion de Parc")
    
    valeur_totale = df['PrixTotalTTC'].sum()
    total_moteurs = len(df)
    
    df_recyclage = df[df['Decision_IA'].str.contains("RECYCLAGE")]
    valeur_recyclage = df_recyclage['PrixTotalTTC'].sum()
    
    df_pepites = df[df['Decision_IA'].str.contains("PÉPITE")]
    valeur_pepites = df_pepites['PrixTotalTTC'].sum()
    
    df_critique = df[df['Jours_en_stock'] > 365]
    valeur_critique = df_critique['PrixTotalTTC'].sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Stock Total Moteurs", f"{valeur_totale:,.0f} €".replace(',', ' '), f"{total_moteurs} unités")
    k2.metric("Moteurs A Recycler/Ferraille", f"{len(df_recyclage)} unités", f"Valorisation catalogue: {valeur_recyclage:,.0f} €", delta_color="inverse")
    k3.metric("Pépites Opisto à Auditer", f"{len(df_pepites)} unités", f"Trésorerie: {valeur_pepites:,.0f} €")
    k4.metric("Capital Bloqué > 1 An", f"{valeur_critique:,.0f} €".replace(',', ' '), f"{(valeur_critique/valeur_totale*100):.1f}% du parc", delta_color="inverse")

    st.markdown("---")

    # --- SYNTHÈSE D'ARBITRAGE POUR L'ÉQUIPE PARC & VENTES ---
    st.subheader("🤖 Recommandations Stratégiques IA")
    col_rec1, col_rec2 = st.columns(2)
    
    with col_rec1:
        st.error("♻️ **ORDRE DE DÉSTOCKAGE / RECYCLAGE (Libération d'emplacement)**")
        st.write(f"**{len(df_recyclage)} moteurs** ont dépassé 1 an en stock avec un prix unitaire faible. Leur maintien en rack coûte plus cher en surface de stockage que leur valeur nette.")
        st.write("**Top Emplacements à libérer en priorité :**")
        loc_recyclage = df_recyclage['Emplacement'].value_counts().head(5)
        st.dataframe(loc_recyclage, use_container_width=True)

    with col_rec2:
        st.warning("🔍 **AUDIT QUALITÉ OPISTO (Booster la Visibilité Web)**")
        st.write(f"**{len(df_pepites)} moteurs à forte valeur (>1000€)** dorment depuis plus de 6 mois. Ils ont un fort potentiel de vente sur Opisto.")
        st.write("**Actions Ventes :** Vérifier que les codes moteurs OEM originaux sont saisis et rajouter 3 à 4 photos de qualité.")

    st.markdown("---")

    # --- FILTRES & RECHERCHE AVANCÉE ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔎 Filtres d'Arbitrage")
    filtre_decision = st.sidebar.multiselect("Filtrer par Décision IA", options=df['Decision_IA'].unique())
    filtre_emplacement = st.sidebar.text_input("Filtrer par Emplacement / Alley (ex: A-01)")

    df_filtered = df.copy()
    if filtre_decision:
        df_filtered = df_filtered[df_filtered['Decision_IA'].isin(filtre_decision)]
    if filtre_emplacement:
        df_filtered = df_filtered[df_filtered['Emplacement'].str.contains(filtre_emplacement, case=False, na=False)]

    cols_view = ['Nom', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Jours_en_stock', 'Emplacement', 'Decision_IA']

    st.subheader("📋 Liste des Moteurs & Instructions d'Arbitrage")
    st.dataframe(df_filtered[cols_view], use_container_width=True)

    # --- EXPORTation OPÉRATIONNELLE ---
    st.markdown("### 📥 Télécharger les Ordres de Mission")
    c_exp1, c_exp2 = st.columns(2)
    
    with c_exp1:
        csv_recyclage = df_recyclage[cols_view].to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button(
            label="📄 Télécharger la Liste des Moteurs à Recycler (Pour Démonteurs)",
            data=csv_recyclage,
            file_name=f"ordres_recyclage_vhu_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    with c_exp2:
        csv_pepites = df_pepites[cols_view].to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button(
            label="📄 Télécharger la Liste des Pépites à Auditer sur Opisto",
            data=csv_pepites,
            file_name=f"audit_opisto_pepites_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Erreur d'analyse des données : {e}")
