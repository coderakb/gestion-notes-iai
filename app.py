import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image

# Configuration de la page pour mobile/PC
st.set_page_config(page_title="Calculateur de Notes IA", layout="wide")

st.title("📊 Scanner & Classement Automatique")
st.write("Téléchargez vos documents pour calculer les résultats des 1000 étudiants.")

# Liste des matières (Coeff 1)
matieres = [
    "Physique", "Maths stats", "Informatique", "Embryologie", 
    "Chimie organique", "Chimie générale", "Biophysique générale", "Biologie cellulaire"
]

uploaded_file = st.file_uploader("Choisir un fichier (Image ou CSV)", type=['png', 'jpg', 'csv'])

if uploaded_file is not None:
    # Si c'est un CSV (données déjà extraites)
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        # Si c'est une image, on utilise l'IA OCR
        image = Image.open(uploaded_file)
        st.image(image, caption='Document scanné', width=300)
        # Extraction de texte (simulation simplifiée)
        texte = pytesseract.image_to_string(image)
        st.info("Texte extrait par l'IA en cours de traitement...")
        # Ici, vous devriez ajouter une logique pour transformer le texte en tableau
        # Pour cet exemple, on suppose que df est créé
        
    # LOGIQUE DE CALCUL (Votre règle : Somme / 2)
    if all(m in df.columns for m in matieres):
        df['Somme'] = df[matieres].sum(axis=1)
        df['Moyenne_Speciale'] = df['Somme'] / 2
        
        # Classement
        df = df.sort_values(by='Moyenne_Speciale', ascending=False).reset_index(drop=True)
        df['Rang'] = df.index + 1
        
        st.success("Calculs terminés !")
        st.dataframe(df) # Tableau interactif et responsive
        
        # Bouton de téléchargement gratuit
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger le Classement Général (CSV)", csv, "classement.csv", "text/csv")
