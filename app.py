import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="VHU Executive · Arbitrage & Gestion de Parc",
    page_icon="🚗",
    layout="wide"
)

# --- 2. BARRE LATÉRALE (SIDEBAR & FILTRES) ---
with st.sidebar:
    st.markdown("### 📂 Mise à jour de l'inventaire")
    
    uploaded_file = st.file_uploader(
        "Importer votre fichier Excel (.xlsx)", 
        type=["xlsx", "xls", "csv"], 
        label_visibility="collapsed"
    )
    st.caption("Formats acceptés : .xlsx, .xls")
    
    st.markdown("---")
    st.markdown("### 🔍 Filtres Stratégiques (Interne)")
    
    # Filtre par statut d'arbitrage
    statut_filter = st.selectbox(
        "Filtrer par Statut / Action",
        ["Tous", "🟢 Rotation Rapide", "🟠 Pépites à Auditer (Forte Demande)", "🔴 Capital Bloqué > 1 An", "♻️ À Recycler / Baisser Prix"]
    )
    
    # Filtre par ancienneté (Jours en stock)
    max_jours = st.slider("Ancienneté max en stock (jours)", min_value=0, max_value=1200, value=1200, step=30)
    
    emplacement_filter = st.text_input("Filtrer par Emplacement (ex: R2/A9)", "")
    
    st.markdown("---")
    st.markdown("🤖 **Agent IA :** `gemini-3.8-flash`")
    st.markdown("🟢 **Statut :** Connecté")

# --- 3. CHARGEMENT DES DONNÉES ---
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

# Si aucun fichier n'est chargé, on prend une base vide ou de démo, mais si le fichier du user est là on le traite :
if df_user is not None and not df_user.empty:
    # Calcul de l'ancienneté en jours (basé sur la date de création par rapport à la date max du fichier ou d'aujourd'hui)
    if 'Date creation' in df_user.columns:
        df_user['Date creation'] = pd.to_datetime(df_user['Date creation'])
        ref_date = df_user['Date creation'].max() # Date la plus récente du fichier
        df_user['Anciennete_Jours'] = (ref_date - df_user['Date creation']).dt.days
    else:
        df_user['Anciennete_Jours'] = 0

    # Fonction d'attribution des statuts et recommandations de prix
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

    # Calculs pour les KPIs du haut (exactement comme dans votre maquette)
    total_val = df_user['PrixTotalTTC'].sum() if 'PrixTotalTTC' in df_user.columns else 0
    total_unites = len(df_user)
    
    recyclage_df = df_user[df_user['Statut_IA'] == '♻️ À Recycler / Baisser Prix']
    recyclage_count = len(recyclage_df)
    recyclage_val = recyclage_df['PrixTotalTTC'].sum() if 'PrixTotalTTC' in recyclage_df.columns else 0
    
    pepites_df = df_user[df_user['Statut_IA'] == '🟠 Pépites à Auditer (Forte Demande)']
    pepites_count = len(pepites_df)
    pepites_val = pepites_df['PrixTotalTTC'].sum() if 'PrixTotalTTC' in pepites_df.columns else 0
    
    bloque_df = df_user[df_user['Statut_IA'] == '🔴 Capital Bloqué > 1 An']
    bloque_count = len(bloque_df)
    bloque_val = bloque_df['PrixTotalTTC'].sum() if 'PrixTotalTTC' in bloque_df.columns else 0
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
            label="Moteurs À Recycler / Ferraille",
            value=f"{recyclage_count} unités",
            delta=f"Valorisation: {recyclage_val:,.0f} €".replace(',', ' '),
            delta_color="off"
        )

    with col3:
        st.metric(
            label="Pépites Opisto à Auditer",
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

    # --- 6. RECOMMANDATIONS STRATÉGIQUES IA & COMPARATIF DEMANDE ---
    st.subheader("🧠 Recommandations Stratégiques & Analyse de la Demande")

    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        st.markdown(f"""
        <div style="background-color: #fdf2f2; border-left: 5px solid #ef4444; padding: 20px; border-radius: 8px;">
            <h4 style="color: #991b1b; margin-top:0;">♻️ FAIBLE DEMANDE / BAISSE DE PRIX RECOMMANDÉE</h4>
            <p style="font-size: 14px; color: #334155;">
                <b>{recyclage_count} moteurs</b> ont plus d'un an en stock avec une faible valeur. Leur immobilisation coûte plus cher en espace de stockage. 
                <i>Action interne :</i> Revoir le prix à la baisse ou basculer en recyclage/ferraille.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_rec2:
        st.markdown(f"""
        <div style="background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 20px; border-radius: 8px;">
            <h4 style="color: #1e40af; margin-top:0;">🔥 FORTE DEMANDE / PÉPITES À BOOSTER</h4>
            <p style="font-size: 14px; color: #334155;">
                <b>{pepites_count} moteurs à forte valeur (>1000€)</b> présentent un excellent potentiel de vente en ligne. 
                <i>Action interne :</i> Vérifier la présence des références constructeur (OEM) et ajouter 3 à 4 photos sur Opisto pour accélérer la rotation.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- 7. APPLICATION DES FILTRES SUR LE TABLEAU ---
    filtered_df = df_user.copy()
    
    if statut_filter != "Tous":
        filtered_df = filtered_df[filtered_df['Statut_IA'] == statut_filter]
        
    if max_jours < 1200:
        filtered_df = filtered_df[filtered_df['Anciennete_Jours'] <= max_jours]
        
    if emplacement_filter:
        loc_cols = [c for c in filtered_df.columns if 'emplacement' in c.lower() or 'lieu' in c.lower()]
        if loc_cols:
            filtered_df = filtered_df[filtered_df[loc_cols[0]].astype(str).str.contains(emplacement_filter, case=False, na=False)]

    # --- 8. TABLEAU DE DONNÉES DÉTAILLÉ ---
    st.subheader(f"📋 Inventaire Détaillé & Analyse ({len(filtered_df)} moteurs affichés)")
    
    # Colonnes clés à afficher en priorité pour l'interne
    display_cols = [c for c in ['Id', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Anciennete_Jours', 'Emplacement', 'Statut_IA'] if c in filtered_df.columns]
    if not display_cols:
        display_cols = filtered_df.columns.tolist()

    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

else:
    # État initial si aucun fichier n'est uploadé
    st.title("📊 Arbitrage Financier & Gestion de Parc Moteurs")
    st.warning("⚠️ Veuillez importer votre fichier Excel (`stock 9-2023.xlsx`) via le bouton dans la barre latérale à gauche pour lancer l'analyse automatique.")
