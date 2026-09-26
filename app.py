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
    st.text("Importer le dernier export CSV Opisto")
    
    uploaded_file = st.file_uploader("Upload", type=["csv"], label_visibility="collapsed")
    st.caption("200MB per file · CSV")
    
    st.markdown("---")
    st.markdown("### 🔍 Filtres d'Arbitrage")
    
    decisions_ia = st.multiselect(
        "Filtrer par Décision IA",
        ["Recyclage / Ferraille", "Pépites à Auditer", "Capital Bloqué (>1 an)", "Rotation Rapide"],
        default=[]
    )
    
    emplacement_filter = st.text_input("Filtrer par Emplacement / Alley (ex: A-01)", "")
    
    st.markdown("---")
    st.markdown("🤖 **Agent IA :** `gemini-3.8-flash`")
    st.markdown("🟢 **Statut :** Connecté")

# --- 3. EN-TÊTE PRINCIPAL ---
st.title("📊 Arbitrage Financier & Gestion de Parc")
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# --- 4. BARRE DE KPI FINANCIERS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Stock Total Moteurs",
        value="215 180 €",
        delta="↑ 165 unités"
    )

with col2:
    st.metric(
        label="Moteurs A Recycler/Ferraille",
        value="2 unités",
        delta="Valorisation catalogue: 589 €",
        delta_color="off"
    )

with col3:
    st.metric(
        label="Pépites Opisto à Auditer",
        value="15 unités",
        delta="Trésorerie: 29,177 €",
        delta_color="normal"
    )

with col4:
    st.metric(
        label="Capital Bloqué > 1 An",
        value="25 818 €",
        delta="12.0% du parc",
        delta_color="inverse"
    )

st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# --- 5. RECOMMANDATIONS STRATÉGIQUES IA ---
st.subheader("🧠 Recommandations Stratégiques IA")

col_rec1, col_rec2 = st.columns(2)

with col_rec1:
    st.markdown("""
    <div style="background-color: #fdf2f2; border-left: 5px solid #ef4444; padding: 20px; border-radius: 8px; height: 100%;">
        <h4 style="color: #991b1b; margin-top:0;">♻️ ORDRE DE DÉSTOCKAGE / RECYCLAGE</h4>
        <p style="font-size: 14px; color: #334155;">
            <b>2 moteurs</b> ont dépassé 1 an en stock avec un prix unitaires faible. 
            Leur maintien en rack coûte plus cher en surface de stockage que leur valeur nette.
        </p>
        <p style="font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 5px;">
            Top Emplacements à libérer en priorité :
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Petit tableau interne pour les emplacements à libérer
    df_emp = pd.DataFrame({
        'Emplacement': ['MAG R2/A9/E0', 'MAG R1/B4/C2'],
        'count': [1, 1]
    })
    st.dataframe(df_emp, use_container_width=True, hide_index=True)

with col_rec2:
    st.markdown("""
    <div style="background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 20px; border-radius: 8px; height: 100%;">
        <h4 style="color: #1e40af; margin-top:0;">🔍 AUDIT QUALITÉ OPISTO (Booster la Visibilité Web)</h4>
        <p style="font-size: 14px; color: #334155;">
            <b>15 moteurs à forte valeur (>1000€)</b> dorment depuis plus de 6 mois. Ils ont un fort potentiel de vente sur Opisto.
        </p>
        <hr style="border: 0; border-top: 1px solid #cbd5e1; margin: 15px 0;">
        <p style="font-size: 13px; color: #1e293b; margin: 0;">
            <b>Actions Ventes :</b> Vérifier que les codes moteurs OEM originaux sont saisis et rajouter 3 à 4 photos de qualité pour déclencher l'achat en ligne.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 6. TABLEAU DE DONNÉES DÉTAILLÉ (Dynamique si CSV uploadé) ---
st.subheader("📋 Inventaire Détaillé des Moteurs")

if uploaded_file is not None:
    # Lecture du fichier CSV uploadé par l'utilisateur
    df_user = pd.read_csv(uploaded_file)
    st.dataframe(df_user, use_container_width=True, hide_index=True)
else:
    # Données par défaut si aucun fichier n'est encore uploadé
    df_default = pd.DataFrame({
        'Référence': ['MOT-BMW-N47', 'MOT-AUD-20T', 'MOT-PEG-DV6', 'MOT-REN-15DCI'],
        'Intitulé': ['Moteur BMW N47 2.0d', 'Moteur Audi 2.0 TDI', 'Moteur Peugeot 1.6 HDi', 'Moteur Renault 1.5 dCi'],
        'Emplacement': ['MAG R2/A9/E0', 'MAG R1/B2/A1', 'MAG R3/C4/E5', 'MAG R2/A5/B3'],
        'Valeur (€)': [1800, 1450, 1300, 950],
        'Ancienneté (jours)': [420, 190, 45, 120],
        'Statut IA': ['Capital Bloqué > 1 An', 'Pépite à Auditer', 'Rotation Rapide', 'Recyclage / Ferraille']
    })
    st.dataframe(df_default, use_container_width=True, hide_index=True)
