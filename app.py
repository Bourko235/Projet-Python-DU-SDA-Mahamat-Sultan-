import streamlit as st
import pandas as pd
import joblib
import os

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Prédiction Immo King County",
    page_icon="🏠",
    layout="wide"
)

# --- Chargement du Modèle ---
MODEL_FILE = 'models/model_pipeline.joblib'

@st.cache_resource
def load_model(model_path):
    """Charge le pipeline de modèle depuis le fichier .joblib."""
    if not os.path.exists(model_path):
        st.error(f"Erreur : Fichier modèle '{model_path}' non trouvé.")
        st.error("Veuillez d'abord exécuter 'python train_model.py' pour créer le modèle.")
        return None
    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle : {e}")
        return None

model_pipeline = load_model(MODEL_FILE)

# Si le modèle n'est pas chargé, on arrête l'app
if model_pipeline is None:
    st.stop()

# --- Interface Utilisateur ---
st.title("🏠 Estimateur de Prix Immobilier (King County, USA)")
st.markdown("""
Cette application prédit le prix d'une maison dans la région de King County (Seattle, USA)
en utilisant un modèle de Machine Learning (Random Forest).
""")
st.image("https://tse1.mm.bing.net/th/id/OIP.1prYVhepJaQm6qSLbEQV6wHaD4?w=600&h=314&rs=1&pid=ImgDetMain&o=7&rm=3", use_container_width=True)

# --- Barre Latérale pour les Entrées ---
st.sidebar.header("Caractéristiques de la Maison")

# --- Inputs Numériques ---
sqft_living = st.sidebar.number_input(
    "Surface habitable (en sqft)", 
    min_value=500, 
    max_value=10000, 
    value=1500
)
bedrooms = st.sidebar.slider(
    "Nombre de chambres", 
    min_value=1, 
    max_value=10, 
    value=3
)
bathrooms = st.sidebar.slider(
    "Nombre de salles de bain", 
    min_value=1.0, 
    max_value=8.0, 
    value=2.0, 
    step=1.0
)
floors = st.sidebar.slider(
    "Nombre d'étages", 
    min_value=1.0, 
    max_value=4.0, 
    value=1.0, 
    step=1.0
)

# --- Inputs Catégoriels ---
# (Répond à l'exigence "Listes déroulantes")
waterfront = st.sidebar.selectbox(
    "Vue sur l'eau ?", 
    options=[0, 1], 
    format_func=lambda x: "Oui" if x == 1 else "Non"
)

# Nous simplifions les options pour l'utilisateur
# Le mapping correspond aux valeurs du dataset (1-5)
condition_map = {
    "Mauvais": 1,
    "Moyen": 3,
    "Bon": 4,
    "Très Bon": 5
}
condition_label = st.sidebar.selectbox(
    "État de la maison", 
    options=["Mauvais", "Moyen", "Bon", "Très Bon"],
    index=1 # Défaut sur "Moyen"
)
# Traduire le label en valeur numérique pour le modèle
condition = condition_map[condition_label]


# --- Logique de Prédiction ---
if st.sidebar.button("Prédire le Prix", use_container_width=True, type="primary"):
    
    # 1. Préparer les données d'entrée pour le modèle
    # Le pipeline s'attend à un DataFrame avec les bons noms de colonnes
    # et les bons types (ex: 'condition' doit être un str car le pipeline l'encode)
    
    input_data = pd.DataFrame(
        data=[[
            sqft_living, 
            bedrooms, 
            bathrooms, 
            floors,
            waterfront,
            str(condition) # Important: str() pour correspondre à l'entraînement
        ]],
        columns=['sqft_living', 'bedrooms', 'bathrooms', 'floors', 'waterfront', 'condition']
    )
    
    # 2. Faire la prédiction
    try:
        prediction = model_pipeline.predict(input_data)
        predicted_price = prediction[0]
        
        # 3. Afficher le résultat
        st.subheader("Résultat de la Prédiction")
        st.success(f"Le prix estimé pour cette maison est de :")
        
        st.metric(label="Prix Estimé", value=f"${predicted_price:,.2f}")
        
        st.balloons()
        
    except Exception as e:
        st.error(f"Une erreur est survenue lors de la prédiction : {e}")

else:

    st.info("Veuillez saisir les caractéristiques dans la barre latérale et cliquer sur 'Prédire le Prix'.")
