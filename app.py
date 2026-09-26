import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="VHU Executive · Gestion Moteurs",
    page_icon="🚗",
    layout="wide"
)

# --- 2. CHARGEMENT AUTOMATIQUE DU FICHIER DEPUIS GITHUB ---
@st.cache_data
def load_data():
    # Le fichier doit se trouver dans le même dossier sur GitHub
    file_path = "stock 9-2023.xlsx" 
    df = pd.read_excel(file_path)
    return df

try:
    df_user = load_data()
except Exception as e:
    st.error(f"Erreur : Impossible de charger le fichier 'stock 9-2023.xlsx' depuis GitHub. Assurez-vous qu'il est bien présent à la racine du dépôt. ({e})")
    df_user = None

# --- 3. BARRE LATÉRALE (FILTRES INTERNES SIMPLES) ---
with st.sidebar:
    st.markdown("### 📂 Source : GitHub")
    st.success("Fichier `stock 9-2023.xlsx` synchronisé.")
    
    st.markdown("---")
    st.markdown("### ⚡ Filtres & Pilotage")
    
    vue_strategique = st.selectbox(
        "🎯 Mode d'affichage",
        [
            "Vue Globale (Tout afficher)", 
            "🟢 Rotation Rapide", 
            "🟠 Pépites à Auditer (Forte Demande)", 
            "🔴 Capital Bloqué > 1 An", 
            "♻️ À Recycler / Baisser Prix"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Ancienneté en Stock")
    seuil_anciennete = st.slider(
        "Filtrer par ancienneté minimum (jours)", 
        min_value=0, 
        max_value=1000, 
        value=0, 
        step=30
    )
    
    st.markdown("---")
    st.markdown("🤖 **Agent IA :** Connecté")

# --- 4. TRAITEMENT DES DONNÉES ET CALCULS ---
if df_user is not None and not df_user.empty:
    if 'Date creation' in df_user.columns:
        df_user['Date creation'] = pd.to_datetime(df_user['Date creation'])
        ref_date = df_user['Date creation'].max()
        df_user['Anciennete_Jours'] = (ref_date - df_user['Date creation']).dt.days
    else:
        df_user['Anciennete_Jours'] = 0

    # Attribution des statuts et émojis météo
    def assign_statut(row):
        age = row.get('Anciennete_Jours', 0)
        prix = row.get('PrixTotalTTC', 0)
        
        if age > 365 and prix < 500:
            return '♻️ À Recycler / Baisser Prix'
        elif age > 365:
            return '🔴 Capital Bloqué > 1 An'
        elif prix > 1000 and age > 180:
            return '🟠 Pépites à Auditer (Forte Demande)'
        elif age <= 90:
            return '🟢 Rotation Rapide'
        else:
            return 'Standard'

    df_user['Statut_IA'] = df_user.apply(assign_statut, axis=1)

    # Calculs pour les KPIs du haut
    total_val = df_user['PrixTotalTTC'].sum() if 'PrixTotalTTC' in df_user.columns else 0
    total_unites = len(df_user)
    
    recyclage_df = df_user[df_user['Statut_IA'] == '♻️ À Recycler / Baisser Prix']
    recyclage_count = len(recyclage_df)
    recyclage_val = recyclage_df['PrixTotalTTC'].sum() if 'PrixTotalTTC' in df_user.columns else 0
    
    pepites_df = df_user[df_user['Statut_IA'] == '🟠 Pépites à Auditer (Forte Demande)']
    pepites_count = len(pepites_df)
    pepites_val = pepites_df['PrixTotalTTC'].sum() if 'PrixTotalTTC' in df_user.columns else 0
    
    bloque_df = df_user[df_user['Statut_IA'] == '🔴 Capital Bloqué > 1 An']
    bloque_count = len(bloque_df)
    bloque_val = bloque_df['PrixTotalTTC'].sum() if 'PrixTotalTTC' in df_user.columns else 0

    # --- 5. EN-TÊTE PRINCIPAL ---
    st.title("📊 Arbitrage Financier & Gestion de Parc Moteurs")
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    # --- 6. INDICATEURS HAUT DE PAGE (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Stock Total Moteurs",
            value=f"{total_val:,.0f} €".replace(',', ' '),
            delta=f"↑ {total_unites} unités"
        )

    with col2:
        st.metric(
            label="Moteurs À Recycler / Baisser Prix",
            value=f"{recyclage_count} unités",
            delta=f"Valorisation: {recyclage_val:,.0f} €".replace(',', ' '),
            delta_color="off"
        )

    with col3:
        st.metric(
            label="Pépites à Auditer",
            value=f"{pepites_count} unités",
            delta=f"Trésorerie: {pepites_val:,.0f} €".replace(',', ' '),
            delta_color="normal"
        )

    with col4:
        st.metric(
            label="Capital Bloqué > 1 An",
            value=f"{bloque_val:,.0f} €".replace(',', ' '),
            delta=f"{bloque_count} moteurs",
            delta_color="inverse"
        )

    st.markdown("---")

    # --- 7. FILTRAGE ET AFFICHAGE DU TABLEAU ---
    filtered_df = df_user.copy()
    
    if vue_strategique != "Vue Globale (Tout afficher)":
        filtered_df = filtered_df[filtered_df['Statut_IA'] == vue_strategique]
        
    if seuil_anciennete > 0:
        filtered_df = filtered_df[filtered_df['Anciennete_Jours'] >= seuil_anciennete]

    st.subheader(f"📋 Inventaire Détaillé ({len(filtered_df)} moteurs affichés)")
    
    display_cols = [c for c in ['Id', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Anciennete_Jours', 'Emplacement', 'Statut_IA'] if c in filtered_df.columns]
    if not display_cols:
        display_cols = filtered_df.columns.tolist()

    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
