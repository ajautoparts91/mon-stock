import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="VHU Executive · Gestion Moteurs",
    page_icon="🚗",
    layout="wide"
)

# Masquer la barre latérale par CSS
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. CHARGEMENT AUTOMATIQUE DU FICHIER DEPUIS GITHUB ---
@st.cache_data
def load_data():
    file_path = "stock 9-2023.xlsx" 
    df = pd.read_excel(file_path)
    return df

try:
    df_user = load_data()
except Exception as e:
    st.error(f"Erreur : Impossible de charger le fichier 'stock 9-2023.xlsx' depuis GitHub ({e})")
    df_user = None

if df_user is not None and not df_user.empty:
    if 'Date creation' in df_user.columns:
        df_user['Date creation'] = pd.to_datetime(df_user['Date creation'])
        ref_date = df_user['Date creation'].max()
        df_user['Anciennete_Jours'] = (ref_date - df_user['Date creation']).dt.days
    else:
        df_user['Anciennete_Jours'] = 0

    # Tranches d'ancienneté claires pour les filtres
    def get_tranche_age(jours):
        if jours <= 90:
            return "Moins de 3 mois (Récent)"
        elif jours <= 180:
            return "3 à 6 mois"
        elif jours <= 365:
            return "6 mois à 1 an"
        else:
            return "Plus de 1 an (Dormant)"

    df_user['Tranche_Age'] = df_user['Anciennete_Jours'].apply(get_tranche_age)

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

    # --- 3. CALCULS POUR LES KPIs PERTINENTS ---
    total_val = df_user['PrixTotalTTC'].sum() if 'PrixTotalTTC' in df_user.columns else 0
    total_unites = len(df_user)
    prix_moyen = total_val / total_unites if total_unites > 0 else 0
    
    age_moyen = df_user['Anciennete_Jours'].mean() if 'Anciennete_Jours' in df_user.columns else 0
    
    bloque_df = df_user[df_user['Anciennete_Jours'] > 365]
    bloque_count = len(bloque_df)
    bloque_val = bloque_df['PrixTotalTTC'].sum() if 'PrixTotalTTC' in df_user.columns else 0
    bloque_pct = (bloque_val / total_val * 100) if total_val > 0 else 0

    # --- 4. EN-TÊTE PRINCIPAL ---
    st.title("📊 Arbitrage Financier & Gestion de Parc Moteurs")
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    # --- 5. TABLEAU DE BORD DES KPIs (6 Indicateurs Clés) ---
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.metric("Valeur Totale Stock", f"{total_val:,.0f} €".replace(',', ' '))
    with c2:
        st.metric("Volume Total", f"{total_unites} unités")
    with c3:
        st.metric("Prix Moyen / Moteur", f"{prix_moyen:,.0f} €".replace(',', ' '))
    with c4:
        st.metric("Âge Moyen en Stock", f"{age_moyen:.0f} jours")
    with c5:
        st.metric("Stock > 1 An (Valeur)", f"{bloque_val:,.0f} €".replace(',', ' '), delta=f"{bloque_pct:.1f}% du parc", delta_color="inverse")
    with c6:
        st.metric("Moteurs Dormants", f"{bloque_count} unités", delta="À brader / recycler", delta_color="off")

    st.markdown("---")

    # --- 6. FILTRES HAUT DE TABLEAU SIMPLIFIÉS ET STRATÉGIQUES ---
    st.markdown("### 🔍 Filtres & Sélection de Parc")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        tranche_filtre = st.selectbox(
            "Filtrer par Ancienneté",
            ["Tous les âges", "Moins de 3 mois (Récent)", "3 à 6 mois", "6 mois à 1 an", "Plus de 1 an (Dormant)"]
        )
        
    with f_col2:
        statut_filtre = st.selectbox(
            "Filtrer par Statut / Météo",
            ["Tous les statuts", "🟢 Rotation Rapide", "🟠 Pépites à Auditer (Forte Demande)", "🔴 Capital Bloqué > 1 An", "♻️ À Recycler / Baisser Prix"]
        )

    with f_col3:
        # Recherche textuelle pour Code Moteur ou Marque/Modèle
        recherche_texte = st.text_input("🔍 Rechercher (Code moteur, marque, modèle...)", "")

    # Application des filtres
    filtered_df = df_user.copy()
    
    if tranche_filtre != "Tous les âges":
        filtered_df = filtered_df[filtered_df['Tranche_Age'] == tranche_filtre]
        
    if statut_filtre != "Tous les statuts":
        filtered_df = filtered_df[filtered_df['Statut_IA'] == statut_filtre]
        
    if recherche_texte:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(recherche_texte, case=False)).any(axis=1)
        filtered_df = filtered_df[mask]

    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
    
    # --- 7. TABLEAU DÉTAILLÉ (AVEC CODE MOTEUR, MARQUE ET COMPATIBILITÉS) ---
    st.subheader(f"📋 Inventaire Détaillé ({len(filtered_df)} moteurs correspondants)")
    
    # Colonnes orientées code moteur, marque, modèle et compatibilité description
    default_cols = ['Id', 'Marque', 'Modele', 'Moteur', 'Annee', 'PrixTotalTTC', 'Anciennete_Jours', 'Emplacement', 'Description', 'Statut_IA']
    display_cols = [c for c in default_cols if c in filtered_df.columns]

    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- 8. ANALYSE ET RECOMMANDATIONS EN BAS DE TABLEAU ---
    st.subheader("💡 Analyse & Recommandations Opérationnelles")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        <div style="background-color: #fef2f2; border-left: 5px solid #ef4444; padding: 15px; border-radius: 6px;">
            <h4 style="color: #991b1b; margin-top:0;">🔴 Actions sur le Stock Dormant (> 1 An)</h4>
            <p style="font-size: 13px; color: #334155;">
                Ce stock immobilise de la trésorerie et de l'espace physique. 
                <b>Stratégie :</b> Vérifiez les descriptions pour lister toutes les affectations véhicules secondaires (compatibilités croisées) et appliquez une baisse de prix incitative sur les plateformes pour libérer les emplacements de stockage.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_b:
        st.markdown("""
        <div style="background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 15px; border-radius: 6px;">
            <h4 style="color: #166534; margin-top:0;">🟢 / 🟠 Optimisation des Pépites & Rotation</h4>
            <p style="font-size: 13px; color: #334155;">
                Les moteurs récents ou à forte valeur font vivre la marge. 
                <b>Stratégie :</b> S'assurer que le code moteur exact et les références constructeurs (`Ref constr`) sont bien mis en avant pour capter les recherches multi-marques des clients professionnels et particuliers.
            </p>
        </div>
        """, unsafe_allow_html=True)
