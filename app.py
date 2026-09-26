import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="VHU Executive - Spécial Moteurs",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ VHU Executive · Spécial Moteurs & Agent IA")
st.markdown("Pilotage de l'inventaire dédié exclusivement aux moteurs et optimisation des annonces.")

# Données de stock recentrées uniquement sur les MOTEURS
@st.cache_data
def load_data():
    return pd.DataFrame({
        'Reference': ['MOT-BMW-N47', 'MOT-PEG-DV6', 'MOT-AUD-20T', 'MOT-REN-15DC', 'MOT-VW-20T', 'MOT-FRD-16TC'],
        'Piece': ['Moteur BMW N47', 'Moteur Peugeot 1.6 HDi', 'Moteur Audi 2.0 TDI', 'Moteur Renault 1.5 dCi', 'Moteur VW 2.0 TDI', 'Moteur Ford 1.6 TDCi'],
        'Kilometrage': ['142 000 km', '110 000 km', '165 000 km', '190 000 km', '130 000 km', '145 000 km'],
        'Valeur_Estimee': [1800, 1300, 1450, 950, 1600, 1100],
        'Jours_En_Stock': [45, 30, 60, 120, 15, 75],
        'Statut': ['Rapide', 'Rapide', 'Standard', 'Dormant', 'Pépite', 'Standard']
    })

df = load_data()

# Barre de KPI claire
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Valeur Totale des Moteurs", f"{df['Valeur_Estimee'].sum():,.0f} €")
with col2:
    st.metric("📦 Moteurs en Stock", len(df))
with col3:
    dormant = df[df['Jours_En_Stock'] > 90]['Valeur_Estimee'].sum()
    st.metric("⏳ Capital Dormant (>90j)", f"{dormant:,.0f} €")

st.divider()

# Tableau et Graphique natif Streamlit
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📋 Inventaire des Moteurs")
    st.dataframe(df, use_container_width=True, hide_index=True)

with col_b:
    st.subheader("📊 Valeur par Moteur (€)")
    st.bar_chart(df.set_index('Piece')['Valeur_Estimee'])

st.divider()

# Section Assistant IA Gemini (3.8-flash)
st.subheader("🤖 Assistant IA Gemini (Spécial Moteurs)")

piece_choisie = st.selectbox("Sélectionnez un moteur pour action rapide :", df['Piece'])

if st.button("✨ Générer l'annonce Opisto & Fiche Technique"):
    with st.spinner("L'agent Gemini 3.8-flash analyse le moteur..."):
        st.success("Fiche technique et annonce générées avec succès :")
        st.markdown(f"""
        - **Moteur sélectionné :** `{piece_choisie}`
        - **Annonce Opisto optimisée :** *Moteur d'occasion certifié VHU, testé sur banc, compressions vérifiées. Vendu nu ou avec accessoires selon arrivage. Garantie 3 mois incluse. Idéal échange standard.*
        - **Conseil IA :** Prix aligné sur le marché actuel, rotation optimale.
        """)
