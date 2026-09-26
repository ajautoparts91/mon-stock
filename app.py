import streamlit as st
import plotly.express as px
import pandas as pd
from google import genai

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="VHU Executive & Agent IA",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DESIGN SYSTEM & CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    /* Fond général et police */
    .main {
        background-color: #f8fafc;
    }
    
    /* Style des cartes KPI */
    div.metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease;
    }
    div.metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    
    /* En-têtes de sections */
    h3 {
        color: #1e293b;
        font-weight: 600;
        letter-spacing: -0.025em;
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT DES DONNÉES (Exemple VHU) ---
@st.cache_data
def load_vhu_data():
    data = {
        'Reference': ['MOT-BMW-N47', 'BOX-ZF-8HP', 'TUR-AUD-20T', 'ALT-MER-180', 'CRE-CLI-04', 'MOT-PEG-DV6', 'PAR-GOL-701'],
        'Piece': ['Moteur BMW N47', 'Boîte Auto ZF 8 rapports', 'Turbo Audi 2.0 TDI', 'Alternateur Mercedes Classe C', 'Crémaillère Clio 4', 'Moteur Peugeot 1.6 HDi', 'Pare-chocs Golf 7'],
        'Categorie': ['Moteur', 'Transmission', 'Suralimentation', 'Électrique', 'Direction', 'Moteur', 'Carrosserie'],
        'Valeur_Estimee': [1800, 950, 450, 180, 220, 1300, 250],
        'Jours_En_Stock': [45, 120, 15, 90, 200, 30, 10],
        'Statut': ['Pépite', 'Dormant', 'Rapide', 'Dormant', 'Critique', 'Rapide', 'Rapide']
    }
    return pd.DataFrame(data)

df = load_vhu_data()

# --- 4. BARRE LATÉRALE (FILTRES & NAVIGATION) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/car--v1.png", width=64)
    st.title("VHU Executive")
    st.markdown("---")
    
    st.subheader("🔍 Filtres d'inventaire")
    selected_category = st.selectbox("Catégorie de pièce", ["Toutes"] + list(df['Categorie'].unique()))
    selected_status = st.selectbox("Statut stratégique", ["Tous"] + list(df['Statut'].unique()))
    
    # Application des filtres
    filtered_df = df.copy()
    if selected_category != "Toutes":
        filtered_df = filtered_df[filtered_df['Categorie'] == selected_category]
    if selected_status != "Tous":
        filtered_df = filtered_df[filtered_df['Statut'] == selected_status]

    st.markdown("---")
    st.markdown("⚙️ **Agent IA :** `gemini-3.8-flash`")
    st.markdown("🟢 **Statut :** Connecté & Opérationnel")

# --- 5. EN-TÊTE PRINCIPAL ---
st.title("🚗 Tableau de Bord VHU & Intelligence Opérationnelle")
st.markdown("Pilotez la valorisation de vos pièces, suivez le capital dormant et optimisez vos ventes en direct.")

# --- 6. BARRE DE KPI VISUELLE ---
col1, col2, col3, col4 = st.columns(4)

total_val = filtered_df['Valeur_Estimee'].sum()
total_refs = len(filtered_df)
dormant_val = filtered_df[filtered_df['Jours_En_Stock'] > 90]['Valeur_Estimee'].sum()
rotation_rate = "78.4%"

with col1:
    st.metric(label="💰 Valeur Totale du Stock", value=f"{total_val:,.0f} €", delta="+4.2% vs M-1")
with col2:
    st.metric(label="📦 Références Filtrées", value=f"{total_refs} unités", delta="Actives")
with col3:
    st.metric(label="⏳ Capital Dormant (>90j)", value=f"{dormant_val:,.0f} €", delta="-12%", delta_color="inverse")
with col4:
    st.metric(label="🔄 Indice de Rotation Global", value=rotation_rate, delta="+2.1%")

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# --- 7. GRAPHIQUES PLOTLY HAUT DE GAMME ---
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("📊 Répartition de la Valeur par Catégorie")
    fig_cat = px.bar(
        filtered_df, x='Categorie', y='Valeur_Estimee', color='Categorie',
        text_auto='.2s', color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_cat.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_c2:
    st.subheader("⏳ Matrice Ancienneté vs Valeur (Risque BFR)")
    fig_scatter = px.scatter(
        filtered_df, x='Jours_En_Stock', y='Valeur_Estimee', size='Valeur_Estimee', color='Statut',
        hover_name='Piece', color_discrete_map={
            'Pépite': '#10b981', 'Dormant': '#ef4444', 'Rapide': '#3b82f6', 'Critique': '#f59e0b'
        }
    )
    fig_scatter.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- 8. TABLEAU DE DONNÉES STYLISÉ ---
st.subheader("📋 Inventaire Détaillé")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# --- 9. SECTION ASSISTANT IA GEMINI (3.8-flash) ---
st.markdown("---")
st.subheader("🤖 Assistant IA Gemini · Actions Stratégiques & Commerciales")

selected_piece_name = st.selectbox("Sélectionnez une référence pour action immédiate :", filtered_df['Piece'])
current_piece_data = filtered_df[filtered_df['Piece'] == selected_piece_name].iloc[0]

ai_col1, ai_col2 = st.columns(2)

with ai_col1:
    if st.button("✨ Générer l'annonce de vente Opisto optimisée", use_container_width=True):
        with st.spinner("L'agent Gemini 3.8-flash rédige votre annonce..."):
            # Simulation d'appel API Gemini avec le modèle à jour
            prompt = f"Rédige une annonce percutante pour la pièce automobile suivante : {current_piece_data['Piece']}, Catégorie : {current_piece_data['Categorie']}, Prix : {current_piece_data['Valeur_Estimee']}€, Ancienneté : {current_piece_data['Jours_En_Stock']} jours."
            
            # Exemple de rendu visuel propre
            st.success("Annonce générée avec succès :")
            st.markdown(f"""
            > **Titre :** `{current_piece_data['Piece']} - Original / Certifié VHU / Garantie 3 mois`
            > **Description :** Pièce contrôlée, testée sur banc et démontée par un centre VHU agréé. Idéal remplacement direct. Envoi rapide ou retrait sur place.
            > **Prix conseillé :** **{current_piece_data['Valeur_Estimee']} € TTC**
            """)

with ai_col2:
    if st.button("📈 Lancer l'analyse de déstockage & BFR", use_container_width=True):
        with st.spinner("Analyse des tendances en cours..."):
            st.info(f"""
            **Diagnostic IA pour {selected_piece_name} :**
            - **Ancienneté :** {current_piece_data['Jours_En_Stock']} jours en stock.
            - **Recommandation :** {'⚠️ Solder à -15% pour libérer du BFR' if current_piece_data['Jours_En_Stock'] > 90 else '✅ Rotation saine, maintenir le prix actuel'}.
            """)
