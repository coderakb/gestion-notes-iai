import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import pdfplumber
import io

# Configuration de la page
st.set_page_config(page_title="IAI-Togo : Gestionnaire de Notes", layout="wide")

st.title("🎓 Système Automatisé de Résultats")
st.markdown("""
    **Logiciel de calcul et classement pour 1000 étudiants** *Supporte : Excel, PDF, CSV et Scans d'images* *Règle : Somme des 8 matières (coeff 1) divisée par 2*
""")

# Liste officielle des matières
MATIERES = [
    "Physique", "Maths stats", "Informatique", "Embryologie", 
    "Chimie organique", "Chimie générale", "Biophysique générale", "Biologie cellulaire"
]

def traiter_donnees(df):
    """Nettoie les données et applique la règle de calcul (Somme / 2)"""
    try:
        # Conversion forcée en numérique pour éviter les erreurs de texte
        for m in MATIERES:
            if m in df.columns:
                df[m] = pd.to_numeric(df[m], errors='coerce').fillna(0)
            else:
                df[m] = 0.0 # Crée la colonne si elle manque

        # Calcul selon votre consigne
        df['Total_Points'] = df[MATIERES].sum(axis=1)
        df['Moyenne_Speciale'] = df['Total_Points'] / 2
        
        # Classement par moyenne décroissante
        df = df.sort_values(by='Moyenne_Speciale', ascending=False).reset_index(drop=True)
        df.insert(0, 'Rang', df.index + 1)
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du calcul : {e}")
        return None

# Interface de téléchargement
uploaded_file = st.file_uploader("Déposez votre document ici", type=['xlsx', 'xls', 'pdf', 'csv', 'png', 'jpg', 'jpeg'])

if uploaded_file:
    df_result = None
    extension = uploaded_file.name.split('.')[-1].lower()

    # --- LECTURE EXCEL ---
    if extension in ['xlsx', 'xls']:
        df_result = pd.read_excel(uploaded_file)
        st.success("✅ Fichier Excel lu avec succès.")

    # --- LECTURE CSV ---
    elif extension == 'csv':
        df_result = pd.read_csv(uploaded_file)
        st.success("✅ Fichier CSV lu avec succès.")

    # --- LECTURE PDF (Conversion IA/Tableau) ---
    elif extension == 'pdf':
        with st.spinner("Analyse du PDF en cours..."):
            with pdfplumber.open(uploaded_file) as pdf:
                all_data = []
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        all_data.extend(table)
                
                if all_data:
                    # Utilise la première ligne du PDF comme en-tête
                    df_result = pd.DataFrame(all_data[1:], columns=all_data[0])
                    st.success("✅ Tableaux extraits du PDF et convertis.")
                else:
                    st.error("Aucun tableau structuré n'a été trouvé dans ce PDF.")

    # --- LECTURE IMAGE (OCR) ---
    else:
        with st.spinner("Lecture de l'image (OCR)..."):
            img = Image.open(uploaded_file)
            st.image(img, caption="Aperçu du document", width=300)
            texte = pytesseract.image_to_string(img)
            # Pour l'OCR gratuit, on affiche le texte pour vérification
            st.info("Texte extrait détecté. Pour 1000 étudiants, préférez l'import Excel/PDF pour plus de précision.")
            st.text_area("Données lues", texte, height=150)

    # --- AFFICHAGE ET TÉLÉCHARGEMENT ---
    if df_result is not None:
        final_df = traiter_donnees(df_result)
        
        if final_df is not None:
            st.write("### 🏆 Classement Final")
            st.dataframe(final_df, use_container_width=True)

            # Exportation vers Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Classement')
            
            st.download_button(
                label="📥 Télécharger le Classement Final (Excel)",
                data=buffer.getvalue(),
                file_name="resultats_complets_iai.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
