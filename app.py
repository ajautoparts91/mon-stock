import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="VHU Executive · Arbitrage & Gestion de Parc",
    page_icon="🚗",
    layout="wide"
)

# --- 2. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 📂 Mise à jour de l'inventaire Opisto")
    
    uploaded_file = st.file_uploader("Importer le dernier export CSV Opisto", type=["csv", "txt"], label_visibility="collapsed")
    st.caption("200MB per file · CSV")
    
    st.markdown("---")
    st.markdown("### 🔍 Filtres d'Arbitrage")
    
    emplacement_filter = st.text_input("Filtrer par Emplacement / Alley (ex: A-01)", "")
    
    st.markdown("---")
    st.markdown("🤖 **Agent IA :** `gemini-3.8-flash`")
    st.markdown("🟢 **Statut :** Connecté")

# --- 3. EN-TÊTE PRINCIPAL ---
st.title("📊 Arbitrage Financier & Gestion de Parc")
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# --- 4. CHARGEMENT INTELLIGENT DU FICHIER OPISTO ---
df_user = None

if uploaded_file is not None:
    try:
        # Détection automatique du séparateur (virgule, point-virgule, tabulation)
        df_user = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
    except Exception:
        try:
            uploaded_file.seek(0)
            df_user = pd.read_csv(uploaded_file, sep=';', encoding='latin1')
        except Exception as e:
            st.error(f"Erreur de lecture du fichier CSV : {e}")

# --- 5. AFFICHAGE DES DONNÉES ---
if df_user is not None and not df_user.empty:
    st.success(f"✅ Fichier Opisto chargé avec succès : **{len(df_user)} moteurs / lignes** détectés.")
    
    # Application du filtre d'emplacement si renseigné
    if emplacement_filter:
        loc_cols = [c for c in df_user.columns if 'emplacement' in c.lower() or 'rack' in c.lower() or 'lieu' in c.lower() or 'zone' in c.lower()]
        if loc_cols:
            df_user = df_user[df_user[loc_cols[0]].astype(str).str.contains(emplacement_filter, case=False, na=False)]

    st.subheader("📋 Inventaire Complet des Moteurs (Votre Export Réel)")
    st.dataframe(df_user, use_container_width=True, hide_index=True)

else:
    # Affichage par défaut si aucun fichier n'est encore uploadé
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Stock Total Moteurs", value="215 180 €", delta="↑ 165 unités")
    with col2:
        st.metric(label="Moteurs A Recycler/Ferraille", value="2 unités", delta="Valorisation catalogue: 589 €", delta_color="off")
    with col3:
        st.metric(label="Pépites Opisto à Auditer", value="15 unités", delta="Trésorerie: 29,177 €", delta_color="normal")
    with col4:
        st.metric(label="Capital Bloqué > 1 An", value="25 818 €", delta="12.0% du parc", delta_color="inverse")

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    st.subheader("🧠 Recommandations Stratégiques IA")

    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        st.markdown("""
        <div style="background-color: #fdf2f2; border-left: 5px solid #ef4444; padding: 20px; border-radius: 8px;">
            <h4 style="color: #991b1b; margin-top:0;">♻️ ORDRE DE DÉSTOCKAGE / RECYCLAGE</h4>
            <p style="font-size: 14px; color: #334155;">
                Veuillez importer votre fichier CSV Opisto dans la barre latérale pour analyser l'intégralité de vos moteurs en stock.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_rec2:
        st.markdown("""
        <div style="background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 20px; border-radius: 8px;">
            <h4 style="color: #1e40af; margin-top:0;">🔍 AUDIT QUALITÉ OPISTO</h4>
            <p style="font-size: 14px; color: #334155;">
                En attente de votre fichier pour détecter les pépites à forte valeur (>1000€) dormant en stock.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Inventaire Détaillé des Moteurs (Exemple d'affichage)")
    
    df_default = pd.DataFrame({
        'Référence': ['MOT-BMW-N47', 'MOT-AUD-20T', 'MOT-PEG-DV6', 'MOT-REN-15DCI'],
        'Intitulé': ['Moteur BMW N47 2.0d', 'Moteur Audi 2.0 TDI', 'Moteur Peugeot 1.6 HDi', 'Moteur Renault 1.5 dCi'],
        'Emplacement': ['MAG R2/A9/E0', 'MAG R1/B2/A1', 'MAG R3/C4/E5', 'MAG R2/A5/B3'],
        'Valeur (€)': [1800, 1450, 1300, 950],
        'Ancienneté (jours)': [420, 190, 45, 120],
        'Statut IA': ['Capital Bloqué > 1 An', 'Pépite à Auditer', 'Rotation Rapide', 'Recyclage / Ferraille']
    })
    st.dataframe(df_default, use_container_width=True, hide_index=True)
