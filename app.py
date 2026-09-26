import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="VHU Executive · Arbitrage & Gestion de Parc",
    page_icon="🚗",
    layout="wide"
)

# --- 2. BARRE LATÉRALE (SIDEBAR & OUTILS INTERNES) ---
with st.sidebar:
    st.markdown("### 📂 Fichier & Inventaire")
    
    uploaded_file = st.file_uploader(
        "Importer votre fichier Excel (.xlsx)", 
        type=["xlsx", "xls", "csv"], 
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### ⚡ Actions Rapides & Pilotage")
    
    # Sélecteur de vue stratégique (Filtre intelligent pré-paramétré)
    vue_strategique = st.selectbox(
        "🎯 Mode d'analyse interne",
        [
            "Vue Globale (Tout afficher)", 
            "🟠 Pépites à Booster (>1000€ & >6 mois)", 
            "♻️ À Brader / Recycler (>1 an & <500€)", 
            "📦 Filtrer par Rayon / Emplacement"
        ]
    )
    
    # Filtre dynamique selon le mode choisi
    emplacement_filter = ""
    if vue_strategique == "📦 Filtrer par Rayon / Emplacement":
        emplacement_filter = st.text_input("🔍 Taper l'emplacement (ex: MAG R2)", "")

    st.markdown("---")
    st.markdown("### 📊 Paramètres de Rotation")
    seuil_anciennete = st.slider(
        "Filtrer par ancienneté minimum (jours)", 
        min_value=0, 
        max_value=1000, 
        value=0, 
        step=30,
        help="Cibler uniquement les moteurs stockés depuis X jours."
    )
    
    st.markdown("---")
    st.markdown("🤖 **Agent IA :** `gemini-3.8-flash`")
    st.markdown("🟢 **Statut :** Connecté sur GitHub")

# --- 3. CHARGEMENT ET TRAITEMENT DES DONNÉES ---
df_user = None

if uploaded_file is not None:
    try:
        file_name = uploaded_file.name.lower()
        if file_name.endswith(('.xlsx', '.xls')):
            df_user = pd.read_excel(uploaded_file)
        else:
            df_user = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")

if df_user is not None and not df_user.empty:
    # Calcul de l'ancienneté en jours
    if 'Date creation' in df_user.columns:
        df_user['Date creation'] = pd.to_datetime(df_user['Date creation'])
        ref_date = df_user['Date creation'].max()
        df_user['Anciennete_Jours'] = (ref_date - df_user['Date creation']).dt.days
    else:
        df_user['Anciennete_Jours'] = 0

    # Fonction d'attribution des statuts et émojis météo
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
    bloque_pct = (bloque_val / total_val * 100) if total_val > 0 else 0

    # --- 4. EN-TÊTE PRINCIPAL ---
    st.title("📊 Arbitrage Financier & Gestion de Parc Moteurs")
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    # --- 5. BARRE DE KPI FINANCIERS HAUT DE PAGE ---
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
            delta=f"{bloque_pct:.1f}% du parc",
            delta_color="inverse"
        )

    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # --- 6. APPLICATION DES FILTRES DE LA SIDEBAR ---
    filtered_df = df_user.copy()
    
    # Application du mode stratégique choisi dans la sidebar
    if vue_strategique == "🟠 Pépites à Booster (>1000€ & >6 mois)":
        filtered_df = filtered_df[filtered_df['Statut_IA'] == '🟠 Pépites à Auditer (Forte Demande)']
    elif vue_strategique == "♻️ À Brader / Recycler (>1 an & <500€)":
        filtered_df = filtered_df[filtered_df['Statut_IA'] == '♻️ À Recycler / Baisser Prix']
    elif vue_strategique == "📦 Filtrer par Rayon / Emplacement" and emplacement_filter:
        loc_cols = [c for c in filtered_df.columns if 'emplacement' in c.lower() or 'lieu' in c.lower()]
        if loc_cols:
            filtered_df = filtered_df[filtered_df[loc_cols[0]].astype(str).str.contains(emplacement_filter, case=False, na=False)]
            
    if seuil_anciennete > 0:
        filtered_df = filtered_df[filtered_df['Anciennete_Jours'] >= seuil_anciennete]

    # --- 7. TABLEAU DE DONNÉES DÉTAILLÉ ---
    st.subheader(f"📋 Inventaire Détaillé & Analyse ({len(filtered_df)} moteurs affichés)")
    
    display_cols = [c for c in ['Id', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Anciennete_Jours', 'Emplacement', 'Statut_IA'] if c in filtered_df.columns]
    if not display_cols:
        display_cols = filtered_df.columns.tolist()

    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

else:
    st.title("📊 Arbitrage Financier & Gestion de Parc Moteurs")
    st.warning("⚠️ Veuillez importer votre fichier Excel (`.xlsx`) via la barre latérale à gauche pour lancer l'analyse automatique.")
