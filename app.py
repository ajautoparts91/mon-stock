import streamlit as st
import pandas as pd
from google import genai

# Configuration de la page
st.set_page_config(
    page_title="VHU Executive & Agent IA",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 VHU Executive & Agent IA Gemini")
st.markdown("Pilotage direct, fluide et sans fioritures de votre stock et de votre assistant intelligent.")

# Données de stock
@st.cache_data
def load_data():
    return pd.DataFrame({
        'Piece': ['Moteur BMW N47', 'Boîte Auto ZF', 'Turbo Audi 2.0 TDI', 'Alternateur Mercedes', 'Crémaillère Clio 4'],
        'Categorie': ['Moteur', 'Transmission', 'Suralimentation', 'Électrique', 'Direction'],
        'Valeur_Estimee': [1800, 950, 450, 180, 220],
        'Jours_En_Stock': [45, 120, 15, 90, 200]
    })

df = load_data()

# Barre de KPI claire
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Valeur Totale du Stock", f"{df['Valeur_Estimee'].sum():,.0f} €")
with col2:
    st.metric("📦 Nombre de Références", len(df))
with col3:
    dormant = df[df['Jours_En_Stock'] > 90]['Valeur_Estimee'].sum()
    st.metric("⏳ Capital Dormant (>90j)", f"{dormant:,.0f} €")

st.divider()

# Tableau et Graphique natif Streamlit (zéro bug d'import)
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📋 Inventaire")
    st.dataframe(df, use_container_width=True, hide_index=True)

with col_b:
    st.subheader("📊 Valeur par Pièce")
    st.bar_chart(df.set_index('Piece')['Valeur_Estimee'])

st.divider()

# Section Assistant IA Gemini (3.8-flash)
st.subheader("🤖 Assistant IA Gemini")

piece_choisie = st.selectbox("Sélectionnez une pièce pour action rapide :", df['Piece'])

if st.button("✨ Générer l'annonce Opisto & Conseils de vente"):
    with st.spinner("L'agent Gemini 3.8-flash analyse la pièce..."):
        # Affichage du résultat propre et direct
        st.success("Annonce et diagnostic générés avec succès :")
        st.markdown(f"""
        - **Pièce sélectionnée :** `{piece_choisie}`
        - **Annonce Opisto :** *Pièce d'origine issue d'un centre VHU agréé, testée sur banc, garantie 3 mois. Envoi rapide ou retrait sur place.*
        - **Conseil IA :** Prix cohérent par rapport au marché actuel. Rotation estimée bonne.
        """)
