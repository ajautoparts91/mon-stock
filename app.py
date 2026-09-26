import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Direction - Stock & Trésorerie", 
    layout="wide", 
    page_icon="📊"
)

# En-tête de l'application
st.title("📈 Tableau de Bord Stratégique — Optimisation Stock & Trésorerie")
st.caption("Version Direction Générale — Analyse en temps réel et déstockage intelligent")

@st.cache_data
def load_data():
    df = pd.read_csv("inventaire_pieces_26092026_674.csv", sep=';')
    df['Date_creation_dt'] = pd.to_datetime(df['Date creation'], format='%d/%m/%Y', errors='coerce')
    
    ref_date = datetime.now()
    df['Jours_en_stock'] = (ref_date - df['Date_creation_dt']).dt.days.fillna(0).astype(int)
    
    def tranche_age(jours):
        if jours <= 90:
            return '1. Fresh (< 3 mois)'
        elif jours <= 180:
            return '2. Normal (3 à 6 mois)'
        elif jours <= 365:
            return '3. Dormant (6 à 12 mois)'
        else:
            return '4. Critique (> 1 an)'

    df['Tranche_Age'] = df['Jours_en_stock'].apply(tranche_age)
    return df

try:
    df = load_data()

    # Barre latérale : Simulateur dynamique
    st.sidebar.header("🎯 Simulateur de Stratégie")
    st.sidebar.subheader("Ajustement des Remises")
    remise_6m = st.sidebar.slider("Remise Stock Dormant (6 à 12 mois)", 0, 30, 10, help="% de remise pour accélérer la vente")
    remise_1y = st.sidebar.slider("Remise Stock Critique (> 1 an)", 0, 50, 20, help="% de remise pour déstocker en urgence")

    # Calculs personnalisés selon le simulateur
    def calculer_prix(row):
        prix = row['PrixTotalTTC']
        jours = row['Jours_en_stock']
        if jours > 365:
            return round(prix * (1 - remise_1y / 100), 2)
        elif jours > 180:
            return round(prix * (1 - remise_6m / 100), 2)
        return prix

    def recommandation(row):
        jours = row['Jours_en_stock']
        if jours > 365:
            return f"🔴 Urgent : Baisse -{remise_1y}% (> 1 an)"
        elif jours > 180:
            return f"🟠 Promotion : Baisse -{remise_6m}% (> 6 mois)"
        return "🟢 Prix Normal"

    df['Prix_Suggere_TTC'] = df.apply(calculer_prix, axis=1)
    df['Action_Recommandee'] = df.apply(recommandation, axis=1)

    # Indicateurs Financiers (KPIs)
    st.subheader("📌 Indicateurs Clés de Trésorerie (KPIs)")
    valeur_totale = df['PrixTotalTTC'].sum()
    total_pieces = len(df)
    
    stock_6m = df[df['Jours_en_stock'] > 180]
    valeur_6m = stock_6m['PrixTotalTTC'].sum()
    
    stock_1y = df[df['Jours_en_stock'] > 365]
    valeur_1y = stock_1y['PrixTotalTTC'].sum()
    
    cash_liberable = stock_6m['Prix_Suggere_TTC'].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Valeur Totale du Stock", f"{valeur_totale:,.0f} €".replace(',', ' '), f"{total_pieces} pièces")
    c2.metric("Trésorerie Immobilisée (> 6 mois)", f"{valeur_6m:,.0f} €".replace(',', ' '), f"{(valeur_6m/valeur_totale*100):.1f}% du stock", delta_color="inverse")
    c3.metric("Trésorerie Critique (> 1 an)", f"{valeur_1y:,.0f} €".replace(',', ' '), f"{(valeur_1y/valeur_totale*100):.1f}% du stock", delta_color="inverse")
    c4.metric("Cash Potentiel Récupérable", f"{cash_liberable:,.0f} €".replace(',', ' '), "Objectif 30-60 jours")

    st.markdown("---")

    # Synthèse Décisionnelle pour le Grand Patron
    st.subheader("💡 Synthèse Décisionnelle (Rapport Direction)")
    st.info(f"""
    **Analyse de la situation :**
    * Le stock analysé compte **{total_pieces} pièces** représentant un capital de **{valeur_totale:,.2f} € TTC**.
    * **{(valeur_6m/valeur_totale*100):.1f}%** de ce capital (**{valeur_6m:,.2f} €**) ne tourne plus depuis plus de 6 mois.
    * **Plan d'Action Proposé :** En appliquant la simulation choisie dans le menu latéral (-{remise_6m}% sur le stock dormant et -{remise_1y}% sur le stock critique), l'entreprise peut débloquer jusqu'à **{cash_liberable:,.2f} €** de liquidités immédiates.
    """)

    # Visualisations Visuelles
    st.subheader("📊 Graphiques de Répartition")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.write("**Valeur Immobilisée par Ancienneté du Stock (€)**")
        chart_age = df.groupby('Tranche_Age')['PrixTotalTTC'].sum()
        st.bar_chart(chart_age)

    with col_g2:
        st.write("**Top 7 Marques à Fort Capital Immobilisé (> 6 mois)**")
        chart_marque = stock_6m.groupby('Marque')['PrixTotalTTC'].sum().sort_values(ascending=False).head(7)
        st.bar_chart(chart_marque)

    st.markdown("---")

    # Filtres & Table Opérationnelle
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtres d'Analyse")
    recherche = st.sidebar.text_input("Recherche (Code Moteur, Modèle, Emplacement)")
    marques_sel = st.sidebar.multiselect("Filtrer par Marque", options=sorted(df['Marque'].dropna().unique()))
    actions_sel = st.sidebar.multiselect("Filtrer par Statut", options=df['Action_Recommandee'].unique())

    df_filtered = df.copy()
    if recherche:
        df_filtered = df_filtered[
            df_filtered['Moteur'].str.contains(recherche, case=False, na=False) |
            df_filtered['Modele'].str.contains(recherche, case=False, na=False) |
            df_filtered['Emplacement'].str.contains(recherche, case=False, na=False)
        ]
    if marques_sel:
        df_filtered = df_filtered[df_filtered['Marque'].isin(marques_sel)]
    if actions_sel:
        df_filtered = df_filtered[df_filtered['Action_Recommandee'].isin(actions_sel)]

    cols_display = ['Nom', 'Marque', 'Modele', 'Moteur', 'PrixTotalTTC', 'Prix_Suggere_TTC', 'Jours_en_stock', 'Action_Recommandee', 'Emplacement']
    
    st.subheader("📋 Inventaire Détaillé & Recommandations de Prix")
    st.dataframe(df_filtered[cols_display], use_container_width=True)

    # Bouton d'exportation
    st.markdown("### 📥 Exporter les données")
    csv_data = df_filtered[cols_display].to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button(
        label="📄 Télécharger le Rapport d'Action (Format Excel / CSV)",
        data=csv_data,
        file_name=f"rapport_destockage_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Erreur de chargement des données. Détail : {e}")
