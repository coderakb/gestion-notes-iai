import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import pdfplumber
import io

# Configuration
st.set_page_config(page_title="IAI - Gestionnaire Multi-Formats", layout="wide")

st.title("📊 Lecteur de Notes (Excel, PDF, Image)")
st.subheader("Règle : (Somme des 8 matières) / 2")

MATIERES = [
    "Physique", "Maths stats", "Informatique", "Embryologie", 
    "Chimie organique", "Chimie générale", "Biophysique générale", "Biologie cellulaire"
]

def calculer_et_classer(df):
    """Calcule la moyenne et génère le rang"""
    for m in MATIERES:
        if m in df.columns:
            df[m] = pd.to_numeric(df[m], errors='coerce').fillna(0)
        else:
            df[m] = 0
            
    df['Total_Points'] = df[MATIERES].sum(axis=1)
    df['Moyenne_Speciale'] = df['Total_Points'] / 2
    
    # Classement
    df = df.sort_values(by='Moyenne_Speciale', ascending=False).reset_index(drop=True)
    df.insert(0, 'Rang', df.index + 1)
    return df

# Zone de téléchargement
uploaded_file = st.file_uploader("Charger un fichier (Excel, PDF, PNG, JPG)", type=['xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    df_final = None
    file_type = uploaded_file.name.split('.')[-1].lower()

    # --- LECTURE EXCEL ---
    if file_type in ['xlsx', 'xls']:
        df_final = pd.read_excel(uploaded_file)
        st.success("Fichier Excel chargé.")

    # --- LECTURE PDF ---
    elif file_type == 'pdf':
        with pdfplumber.open(uploaded_file) as pdf:
            # On extrait les tableaux du PDF
            all_tables = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_tables.extend(table)
            
            if all_tables:
                # Transformation en DataFrame (on prend la 1ère ligne comme entête)
                df_final = pd.DataFrame(all_tables[1:], columns=all_tables[0])
                st.success("Tableaux extraits du PDF.")
            else:
                st.error("Aucun tableau structuré trouvé dans le PDF.")

    # --- LECTURE IMAGE (OCR) ---
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Aperçu du scan", width=300)
        with st.spinner("Lecture de l'image..."):
            texte_extrait = pytesseract.image_to_string(image)
            st.text_area("Texte détecté", texte_extrait)
            st.warning("Note : Pour les images, l'import CSV/Excel reste préférable pour 1000 lignes.")

    # --- TRAITEMENT ET AFFICHAGE ---
    if df_final is not None:
        resultats = calculer_et_classer(df_final)
        
        st.write("### Résultats et Classement")
        st.dataframe(resultats, use_container_width=True)

        # Exportation
        towrite = io.BytesIO()
        resultats.to_excel(towrite, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Télécharger le Classement Final (Excel)",
            data=towrite.getvalue(),
            file_name="classement_iai_togo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
