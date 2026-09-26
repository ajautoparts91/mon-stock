import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="VHU Executive · Pilotage Parc",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)

# --- 2. CHARGEMENT FACTUEL ET NORMALISATION ---
@st.cache_data
def load_and_clean_data():
    file_path = "stock 9-2023.xlsx"
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Erreur technique : Impossible de lire '{file_path}'. Détail : {e}")
        return None

    # Normalisation stricte selon l'audit de données
    df['Date creation'] = pd.to_datetime(df['Date creation'], errors='coerce')
    df['Date inventaire'] = pd.to_datetime(df['Date inventaire'], errors='coerce')
    df['PrixTotalTTC'] = pd.to_numeric(df['PrixTotalTTC'], errors='coerce').fillna(0)
    
    # L'ancienneté est calculée par rapport à la VRAIE date du jour
    today = pd.Timestamp.today()
    df['Anciennete_Jours'] = (today - df['Date creation']).dt.days
    
    return df

df_stock = load_and_clean_data()

if df_stock is not None and not df_stock.empty:
    
    # --- 3. CALCUL DES KPI STRICTS ---
    total_unites = len(df_stock)
    ca_potentiel_ttc = df_stock['PrixTotalTTC'].sum()
    age_moyen = df_stock['Anciennete_Jours'].mean()
    moteurs_sans_inventaire = df_stock['Date inventaire'].isna().sum()
    stock_dormant = len(df_stock[df_stock['Anciennete_Jours'] > 365])
    
    # --- 4. TABLEAU DE BORD (AUCUNE INTERPRÉTATION, QUE DES FAITS) ---
    st.title("📊 Pilotage Opérationnel VHU")
    st.markdown("### Indicateurs de Parc (Temps Réel)")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Volume Total", f"{total_unites} unités")
    c2.metric("CA Potentiel TTC", f"{ca_potentiel_ttc:,.0f} €".replace(',', ' '))
    c3.metric("Âge Moyen du Stock", f"{age_moyen:.0f} Jours" if pd.notna(age_moyen) else "N/A")
    c4.metric("Stock > 1 An", f"{stock_dormant} unités")
    c5.metric("⚠️ Alertes Inventaire", f"{moteurs_sans_inventaire} unités", help="Nombre de moteurs n'ayant aucune Date d'inventaire.")

    st.markdown("---")

    # --- 5. LOGISTIQUE FLUIDE : FILTRES AVANCÉS ---
    st.markdown("### 🔍 Moteur de Recherche Opérationnel")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    marques_uniques = ["Toutes"] + sorted(df_stock['Marque'].dropna().unique().tolist())
    emplacements_uniques = ["Tous"] + sorted(df_stock['Emplacement'].dropna().unique().tolist())
    
    marque_filtre = col_f1.selectbox("1. Filtrer par Marque", marques_uniques)
    emp_filtre = col_f2.selectbox("2. Filtrer par Zone (Emplacement)", emplacements_uniques)
    recherche = col_f3.text_input("3. 🔍 Code Moteur ou Référence Constructeur", "")
    
    # Filtrage du DataFrame
    df_filtered = df_stock.copy()
    if marque_filtre != "Toutes":
        df_filtered = df_filtered[df_filtered['Marque'] == marque_filtre]
    if emp_filtre != "Tous":
        df_filtered = df_filtered[df_filtered['Emplacement'] == emp_filtre]
        
    # Recherche textuelle optimisée et sécurisée en mémoire
    if recherche:
        mask = df_filtered['Moteur'].astype(str).str.contains(recherche, case=False, na=False) | \
               df_filtered['Ref constr'].astype(str).str.contains(recherche, case=False, na=False)
        df_filtered = df_filtered[mask]
        
    st.dataframe(
        df_filtered[['Id', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Emplacement', 'Date creation', 'Date inventaire']],
        use_container_width=True, hide_index=True
    )
    
    st.markdown("---")

    # --- 6. OPTIMISATION DES RESSOURCES PHYSIQUES ---
    st.markdown("### 🗺️ Cartographie du Magasin (Densité de Stockage)")
    st.caption("Permet d'identifier les zones de stockage saturées pour optimiser les flux logistiques.")
    
    # Regroupement des moteurs par Emplacement
    df_emplacement = df_stock.groupby('Emplacement').size().reset_index(name='Volume')
    # Tri décroissant pour lisibilité
    df_emplacement = df_emplacement.sort_values(by='Volume', ascending=False)
    
    st.bar_chart(df_emplacement.set_index('Emplacement'))

else:
    st.error("Aucune donnée exploitable trouvée dans le fichier source.")
