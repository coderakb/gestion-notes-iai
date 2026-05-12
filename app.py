import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import io

# Configuration de l'interface
st.set_page_config(page_title="IAI - Gestion des Notes", layout="wide")

st.title("📊 Système de Classement Automatisé (1000 Étudiants)")
st.subheader("Règle de calcul : Somme des coefficients 1, divisée par 2")

# Liste officielle des matières
MATIERES = [
    "Physique", "Maths stats", "Informatique", "Embryologie", 
    "Chimie organique", "Chimie générale", "Biophysique générale", "Biologie cellulaire"
]

# Zone de téléchargement
uploaded_file = st.file_uploader("Télécharger un scan (Image) ou un tableau (CSV)", type=['csv', 'png', 'jpg', 'jpeg'])

def calculer_resultats(dataframe):
    """Applique la logique de calcul et de classement"""
    try:
        # Conversion des notes en numérique (au cas où l'OCR lit du texte)
        for m in MATIERES:
            dataframe[m] = pd.to_numeric(dataframe[m], errors='coerce').fillna(0)
        
        # Calcul de la somme et de la moyenne spéciale (Somme / 2)
        dataframe['Total_Points'] = dataframe[MATIERES].sum(axis=1)
        dataframe['Moyenne_Speciale'] = dataframe['Total_Points'] / 2
        
        # Classement général
        dataframe = dataframe.sort_values(by='Moyenne_Speciale', ascending=False).reset_index(drop=True)
        dataframe.index += 1 # Pour commencer le rang à 1
        dataframe.insert(0, 'Rang', dataframe.index)
        
        return dataframe
    except Exception as e:
        st.error(f"Erreur de calcul : {e}")
        return None

if uploaded_file is not None:
    df = None
    
    # CAS 1 : LE FICHIER EST UN CSV
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        st.info("Fichier CSV chargé avec succès.")

    # CAS 2 : LE FICHIER EST UNE IMAGE (SCAN)
    else:
        with st.spinner("L'IA lit le document..."):
            image = Image.open(uploaded_file)
            st.image(image, caption="Aperçu du scan", width=400)
            
            # Utilisation de l'OCR Tesseract
            texte_brut = pytesseract.image_to_string(image)
            
            # Note : Pour transformer du texte brut en tableau propre sans budget,
            # l'idéal est de s'assurer que le scan est bien structuré.
            st.warning("L'extraction via scan gratuit nécessite des documents très clairs.")
            # Simulation d'un DataFrame pour l'exemple (à adapter selon tes colonnes)
            st.text_area("Texte extrait par l'IA", texte_brut, height=150)

    # TRAITEMENT DES DONNÉES
    if df is not None:
        # Vérification des colonnes
        if all(m in df.columns for m in MATIERES):
            resultats = calculer_resultats(df)
            
            if resultats is not None:
                st.success("✅ Traitement terminé !")
                
                # Affichage des classements
                st.write("### Classement Général")
                st.dataframe(resultats)
                
                # Exportation
                csv_result = resultats.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Télécharger le classement (CSV)",
                    data=csv_result,
                    file_name="classement_final.csv",
                    mime="text/csv"
                )
        else:
            st.error(f"Le fichier doit contenir exactement ces colonnes : {', '.join(MATIERES)}")

else:
    st.info("En attente d'un document pour commencer le classement.")
