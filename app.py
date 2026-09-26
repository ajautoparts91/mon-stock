import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai
import os

st.set_page_config(
    page_title="VHU Executive & Agent IA Gemini", 
    layout="wide", 
    page_icon="🚘"
)

st.title("🚘 VHU Direction — Arbitrage Stock & Assistant IA Gemini")
st.caption("Pilotage du BFR, libération d'emplacements et analyse intelligente par IA")

# --- INITIALISATION CLIENT GEMINI ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# --- MODULE D'IMPORTATION OPISTO ---
st.sidebar.header("📂 Importation Inventaire")
uploaded_file = st.sidebar.file_uploader("Importer le dernier export CSV Opisto", type=['csv'])

@st.cache_data
def process_data(file_source):
    df = pd.read_csv(file_source, sep=';')
    df['Date_creation_dt'] = pd.to_datetime(df['Date creation'], format='%d/%m/%Y', errors='coerce')
    
    ref_date = datetime.now()
    df['Jours_en_stock'] = (ref_date - df['Date_creation_dt']).dt.days.fillna(0).astype(int)
    
    def classifier_moteur(row):
        prix = row['PrixTotalTTC']
        jours = row['Jours_en_stock']
        
        if jours > 365 and prix < 400:
            return "♻️ RECYCLAGE (Ferraille)"
        elif jours > 365 and prix >= 400:
            return "🚨 CRITIQUE (-30% Opisto)"
        elif 180 < jours <= 365 and prix >= 1000:
            return "⭐ PÉPITE DORMANTE (Audit Fiche)"
        elif 180 < jours <= 365:
            return "🟠 PROMOTION (-15% Opisto)"
        elif jours <= 90 and prix >= 1200:
            return "🔥 TOP VENTE OPISTO"
        return "🟢 STOCK NORMAL"

    df['Decision_IA'] = df.apply(classifier_moteur, axis=1)
    return df

try:
    if uploaded_file is not None:
        df = process_data(uploaded_file)
        st.sidebar.success("✅ Fichier Opisto chargé !")
    else:
        df = process_data("inventaire_pieces_26092026_674.csv")

    # --- KPIS PRINCIPAUX ---
    valeur_totale = df['PrixTotalTTC'].sum()
    total_moteurs = len(df)
    df_recyclage = df[df['Decision_IA'].str.contains("RECYCLAGE")]
    df_pepites = df[df['Decision_IA'].str.contains("PÉPITE")]
    df_critique = df[df['Jours_en_stock'] > 365]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Stock Total Moteurs", f"{valeur_totale:,.0f} €".replace(',', ' '), f"{total_moteurs} unités")
    k2.metric("A Recycler / Ferraille", f"{len(df_recyclage)} unités", f"Val: {df_recyclage['PrixTotalTTC'].sum():,.0f} €", delta_color="inverse")
    k3.metric("Pépites à Auditer", f"{len(df_pepites)} unités", f"Trésorerie: {df_pepites['PrixTotalTTC'].sum():,.0f} €")
    k4.metric("Capital Bloqué > 1 An", f"{df_critique['PrixTotalTTC'].sum():,.0f} €".replace(',', ' '), f"{(df_critique['PrixTotalTTC'].sum()/valeur_totale*100):.1f}% du parc", delta_color="inverse")

    st.markdown("---")

    # --- AGENT IA CONVERSATIONNEL GEMINI ---
    st.subheader("🤖 Assistant IA Gemini — Expert VHU & Opisto")
    
    if not api_key:
        st.warning("⚠️ Clé API Gemini non détectée dans les Secrets Streamlit (`GEMINI_API_KEY`). Veuillez ajouter votre clé pour activer l'assistant.")
    else:
        question_user = st.text_input(
            "Posez une question sur votre stock ou demandez une stratégie :",
            placeholder="Ex : Propose une annonce LeBonCoin pour un moteur K9K ou liste les emplacements à vider."
        )
        
        if st.button("💬 Analyser avec Gemini"):
            if question_user:
                with st.spinner("Analyse par l'IA en cours..."):
                    # Contexte réduit du stock pour l'IA
                    context_summary = f"""
                    Voici les données résumées du stock moteur VHU :
                    - Nombre total de moteurs : {total_moteurs}
                    - Valeur totale : {valeur_totale:.2f} €
                    - Moteurs à recycler (dormants > 1 an, <400€) : {len(df_recyclage)}
                    - Moteurs pépites (>1000€, dormants 6-12 mois) : {len(df_pepites)}
                    
                    Exemples de pièces en stock :
                    {df[['Nom', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Emplacement', 'Decision_IA']].head(15).to_string()}
                    """
                    
                    prompt = f"""
                    Tu es un expert en gestion de pièces automobiles usagées (VHU) et ventes en ligne sur Opisto/LeBonCoin.
                    Réponds à la question suivante en te basant sur le contexte du stock fourni.
                    
                    Contexte :
                    {context_summary}
                    
                    Question de l'utilisateur : {question_user}
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt,
                    )
                    st.success("Analyse terminée :")
                    st.write(response.text)

    st.markdown("---")

    # --- TABLEAU ET FILTRES ---
    st.subheader("📋 Inventaire Détaillé")
    filtre_decision = st.sidebar.multiselect("Filtrer par Décision", options=df['Decision_IA'].unique())
    
    df_filtered = df.copy()
    if filtre_decision:
        df_filtered = df_filtered[df_filtered['Decision_IA'].isin(filtre_decision)]

    cols_view = ['Nom', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Jours_en_stock', 'Emplacement', 'Decision_IA']
    st.dataframe(df_filtered[cols_view], use_container_width=True)

except Exception as e:
    st.error(f"Erreur lors du traitement des données : {e}")
