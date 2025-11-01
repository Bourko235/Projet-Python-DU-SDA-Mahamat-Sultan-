import streamlit as st
import pandas as pd
import altair as alt # Pour les graphiques
import os # Pour vérifier l'existence du fichier
import datetime # Pour horodater les entrées
import hashlib # NOUVEAU: Pour le hashage des mots de passe

# --- Configuration de la Page ---
st.set_page_config(
    page_title="GlucoSuivi",
    page_icon="🩸",
    layout="wide"
)

# --- Constantes ---
DATA_FILE = "diabete_master_data.csv"
USER_DB_FILE = "user_db.csv" # NOUVEAU: Fichier pour les utilisateurs

# Seuils de glycémie (en mg/dL) - CE SONT DES EXEMPLES
SEUILS = {
    "hypo": 70,
    "optimal_max_ajeun": 100,
    "optimal_max_postrepas": 140,
    "eleve": 180
}

# --- BASE DE DONNÉES ALIMENTAIRE (Inchangée) ---
@st.cache_data
def get_food_db():
    """Charge la base de données des aliments."""
    data = {
        'Food': ["Avocat", "Poulet", "Riz", "Saumon", "Œuf", "Pain", "Pâtes", "Lait", "Fromage", "Pomme", "Banane", "Beurre", "Yaourt", "Bœuf", "Poisson blanc", "Lentilles", "Chocolat noir", "Amandes", "Carottes", "Tomates"],
        'Lipids_per_100g': [15, 3, 1, 13, 11, 1, 1.5, 3.5, 20, 0.3, 0.3, 82, 3, 15, 2, 0.8, 42, 49, 0.2, 0.2],
        'Carbs_per_100g': [2, 0, 28, 0, 1, 50, 72, 5, 2, 11, 22, 0.6, 4.5, 0, 0, 20, 30, 9, 9, 3],
        'Proteins_per_100g': [2, 27, 3, 20, 13, 9, 12, 3.4, 25, 0.3, 1.3, 0.8, 4.2, 26, 19, 9, 7, 21, 1, 1]
    }
    return pd.DataFrame(data)

FOOD_DB = get_food_db()
FOOD_CHOICES = ["(Aucun)"] + FOOD_DB['Food'].tolist() + ["Autre"]


# =============================================================================
# --- Fonctions de Logique (Backend) - Authentification (NOUVEAU) ---
# =============================================================================

def hash_password(password):
    """Hashe un mot de passe en utilisant SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, provided_password):
    """Vérifie si le mot de passe fourni correspond au hash stocké."""
    return stored_hash == hash_password(provided_password)

def load_user_db(file_path):
    """Charge la base de données des utilisateurs."""
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            pass
    return pd.DataFrame(columns=["ID Patient", "PasswordHash"])

def save_user_db(df, file_path):
    """Sauvegarde la base de données des utilisateurs."""
    try:
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        st.error(f"Erreur de sauvegarde base utilisateurs: {e}")
        return False

def handle_login(patient_id, password, user_df):
    """Gère la logique de connexion."""
    if patient_id in user_df["ID Patient"].values:
        user_data = user_df[user_df["ID Patient"] == patient_id].iloc[0]
        if verify_password(user_data["PasswordHash"], password):
            st.session_state.logged_in = True
            st.session_state.current_user = patient_id
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    else:
        st.error("Identifiant Patient non trouvé.")

def handle_register(patient_id, password, confirm_password, user_df):
    """Gère la logique d'inscription."""
    if not patient_id:
        st.error("L'identifiant ne peut pas être vide.")
        return
    if patient_id in user_df["ID Patient"].values:
        st.error("Cet Identifiant Patient existe déjà.")
        return
    if password != confirm_password:
        st.error("Les mots de passe ne correspondent pas.")
        return
    if len(password) < 6:
        st.error("Le mot de passe doit contenir au moins 6 caractères.")
        return
    
    # Tout est bon, on crée l'utilisateur
    hashed_password = hash_password(password)
    new_user = pd.DataFrame({
        "ID Patient": [patient_id],
        "PasswordHash": [hashed_password]
    })
    
    user_df = pd.concat([user_df, new_user], ignore_index=True)
    if save_user_db(user_df, USER_DB_FILE):
        st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")

# =============================================================================
# --- Fonctions de Logique (Backend) - Données (Modifiées) ---
# =============================================================================

def load_data(file_path):
    """Charge les données patient, ou crée un DataFrame vide."""
    expected_columns = [
        "ID Patient", "Date/Heure", "Glycémie (mg/dL)", 
        "Moment", "Aliment", "Quantité (g)", "Total Glucides (g)", 
        "Commentaires"
    ]
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, parse_dates=['Date/Heure'])
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                st.toast(f"Mise à jour du fichier de données. Ajout de: {missing_cols}", icon="🔄")
                for col in missing_cols:
                    if col == 'Total Glucides (g)' or col == 'Quantité (g)':
                        df[col] = 0.0
                    else:
                        df[col] = None
            df = df.reindex(columns=expected_columns)
            return df
        except (pd.errors.EmptyDataError, Exception):
            pass # Gère les fichiers vides ou corrompus
            
    return pd.DataFrame(columns=expected_columns)

def save_data(df, file_path):
    """Sauvegarde le DataFrame principal dans le fichier CSV."""
    try:
        df.to_csv(file_path, index=False)
        st.sidebar.success("Entrée sauvegardée !")
    except Exception as e:
        st.sidebar.error(f"Erreur lors de la sauvegarde: {e}")

# ... (les fonctions get_glycemie_advice et handle_add_entry restent INCHANGÉES) ...
def get_glycemie_advice(glycemie, moment):
    """Fournit un message et un conseil basés sur la glycémie et le moment."""
    # (Logique inchangée, car elle est basée sur la glycémie)
    if glycemie == 0: # 0 est la valeur par défaut
        return "Info", "Saisissez votre glycémie pour un conseil."
    
    if glycemie < SEUILS["hypo"]:
        message = "Hypoglycémie"
        conseil = "Mangez 15g de sucre rapide (jus de fruit, 3 sucres). Contrôlez à nouveau dans 15 minutes."
        return message, conseil
        
    if moment == "Au réveil (à jeun)":
        if glycemie <= SEUILS["optimal_max_ajeun"]:
            message = "Optimal (à jeun)"
            conseil = "Excellent ! Votre glycémie à jeun est dans l'objectif."
        elif glycemie < SEUILS["eleve"]:
            message = "Élevé (à jeun)"
            conseil = "Votre glycémie est un peu haute. Avez-vous bien pris votre traitement hier soir ? Parlez-en à votre médecin."
        else:
            message = "Très élevé (à jeun)"
            conseil = "Votre glycémie est très élevée. Contactez votre équipe soignante si cela persiste."
    
    elif "Après repas" in moment:
        if glycemie <= SEUILS["optimal_max_postrepas"]:
            message = "Optimal (post-repas)"
            conseil = "Parfait ! Votre corps gère bien le repas."
        elif glycemie < SEUILS["eleve"]:
            message = "Élevé (post-repas)"
            conseil = "Glycémie élevée. Essayez d'analyser les glucides de ce repas pour ajuster la prochaine fois."
        else:
            message = "Très élevé (post-repas)"
            conseil = "Glycémie très élevée. Avez-vous oublié votre insuline ? Notez-le et surveillez attentivement."
    
    else: # Pour "Avant repas", "Avant coucher", "Autre"
        if glycemie <= 130: # Seuil générique
            message = "Correct"
            conseil = "Bon contrôle. Continuez comme ça."
        else:
            message = "Élevé"
            conseil = "Glycémie élevée. Préparez votre plan d'action (insuline, hydratation) en conséquence."

    return message, conseil

def handle_add_entry(patient_id, glycemie, moment, aliment, quantite_g, 
                     autre_aliment, autre_glucides, commentaires):
    """Logique d'ajout d'une nouvelle entrée (glycémie + repas)."""
    
    total_glucides = 0
    aliment_nom = aliment
    
    if aliment == "Autre":
        if not autre_aliment:
            st.sidebar.error("Veuillez entrer un nom pour l'aliment 'Autre'.")
            return
        if autre_glucides < 0:
            st.sidebar.error("Les glucides de 'Autre' ne peuvent être négatifs.")
            return
        
        aliment_nom = autre_aliment
        total_glucides = (quantite_g / 100) * autre_glucides
        
    elif aliment != "(Aucun)":
        try:
            selected_food = FOOD_DB[FOOD_DB['Food'] == aliment].iloc[0]
            total_glucides = (quantite_g / 100) * selected_food['Carbs_per_100g']
        except IndexError:
            st.sidebar.error("Erreur lors de la sélection de l'aliment.")
            return

    # Si la glycémie est 0 (non saisie), on met None (ou 0)
    glycemie_a_stocker = glycemie if glycemie > 0 else None

    new_entry = pd.DataFrame({
        "ID Patient": [patient_id],
        "Date/Heure": [datetime.datetime.now()],
        "Glycémie (mg/dL)": [glycemie_a_stocker],
        "Moment": [moment],
        "Aliment": [aliment_nom],
        "Quantité (g)": [quantite_g],
        "Total Glucides (g)": [total_glucides],
        "Commentaires": [commentaires]
    })
    
    # Concaténer avec les données existantes
    st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
    
    # Sauvegarder dans le fichier CSV
    save_data(st.session_state.data, DATA_FILE)
    
    # Rafraîchir l'application pour mettre à jour le dashboard
    st.rerun()

# =============================================================================
# --- Fonctions d'Affichage (Frontend) - (Modifiées) ---
# =============================================================================

def render_login_page(user_df):
    """Affiche l'écran de connexion et d'inscription."""
    st.title("🩸 Bienvenue sur GlucoSuivi")
    st.image("https://placehold.co/800x300/E8F5E9/4CAF50?text=GlucoSuivi", use_container_width=True)
    
    mode = st.radio(
        "Veuillez choisir une action :",
        ["Se Connecter", "S'inscrire (Première connexion)"],
        horizontal=True
    )
    
    st.markdown("---")

    if mode == "Se Connecter":
        st.subheader("Connexion")
        with st.form("login_form"):
            patient_id = st.text_input("Identifiant Patient")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
            
            if submitted:
                handle_login(patient_id, password, user_df)
                
    elif mode == "S'inscrire (Première connexion)":
        st.subheader("Créer un nouveau compte")
        with st.form("register_form"):
            patient_id = st.text_input("Choisissez votre Identifiant Patient")
            password = st.text_input("Nouveau Mot de passe (min. 6 caractères)", type="password")
            confirm_password = st.text_input("Confirmez le mot de passe", type="password")
            submitted = st.form_submit_button("S'inscrire")
            
            if submitted:
                handle_register(patient_id, password, confirm_password, user_df)

# ... (les fonctions render_sidebar et render_main_dashboard restent INCHANGÉES) ...
def render_sidebar(patient_id):
    """Affiche la barre latérale de saisie des données."""
    st.sidebar.title(f"Bonjour, {patient_id} 👋")
    st.sidebar.markdown("---")
    st.sidebar.header("📝 Nouvelle Entrée")
    
    st.sidebar.subheader("🩺 Suivi Glycémie")
    glycemie = st.sidebar.number_input("Glycémie (mg/dL):", min_value=0, value=0, help="Laissez à 0 si non mesurée.")
    moment = st.sidebar.selectbox("Moment de la mesure:", [
        "Au réveil (à jeun)", 
        "Avant repas", 
        "Après repas (2h)", 
        "Avant coucher", 
        "Autre (ex: sport, symptôme)"
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🍽️ Suivi Repas")
    
    aliment = st.sidebar.selectbox("Aliment principal:", FOOD_CHOICES)
    
    # --- Logique conditionnelle pour "Autre" ---
    autre_aliment = None
    autre_glucides = 0
    
    if aliment == "Autre":
        autre_aliment = st.sidebar.text_input("Nom de l'aliment:")
        autre_glucides = st.sidebar.number_input("Glucides (g/100g):", min_value=0.0, format="%.1f")
    
    quantite_g = st.sidebar.number_input("Quantité (g):", min_value=0, value=100)
    
    st.sidebar.markdown("---")
    commentaires = st.sidebar.text_area("Commentaires (symptômes, activité...):")

    if st.sidebar.button("Ajouter l'entrée", use_container_width=True, type="primary"):
        # On ajoute l'entrée (repas ou glycémie ou les deux)
        handle_add_entry(st.session_state.current_user, glycemie, moment, aliment, quantite_g, 
                         autre_aliment, autre_glucides, commentaires)
            
    st.sidebar.markdown("---")
    if st.sidebar.button("Se déconnecter", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

def render_main_dashboard(patient_id):
    """Affiche le dashboard principal avec les graphiques et conseils."""
    
    # Appeler la sidebar pour qu'elle s'affiche toujours
    render_sidebar(patient_id)
    
    st.title(f"📊 Dashboard de {patient_id}")
    
    # Récupérer les données du patient connecté
    patient_data = st.session_state.data[st.session_state.data['ID Patient'] == patient_id].copy()
    
    if patient_data.empty:
        st.info("Bienvenue ! Ajoutez votre première mesure (glycémie et/ou repas) dans la barre latérale pour commencer le suivi.")
        return

    # --- 1. Flash Info (Le rappel et le conseil glycémique) ---
    st.header("⚡ Flash Info Glycémie")
    
    # Récupérer la dernière entrée AVEC une glycémie
    last_glycemie_data = patient_data.dropna(subset=['Glycémie (mg/dL)'])
    
    if not last_glycemie_data.empty:
        last_entry = last_glycemie_data.iloc[-1]
        last_glycemie = last_entry['Glycémie (mg/dL)']
        last_moment = last_entry['Moment']
        
        message, conseil = get_glycemie_advice(last_glycemie, last_moment)
        
        st.metric(
            label=f"Dernier Relevé ({last_moment})", 
            value=f"{last_glycemie} mg/dL",
            delta=message
        )
        
        if "Optimal" in message or "Correct" in message:
            st.success(f"**Conseil :** {conseil}")
        elif "Hypoglycémie" in message:
            st.error(f"**Conseil :** {conseil}")
        else: # Élevé
            st.warning(f"**Conseil :** {conseil}")
    else:
        st.info("Aucune donnée de glycémie trouvée. Ajoutez votre premier relevé.")

    # --- 2. Résumé Nutritionnel (NOUVEAU) ---
    st.header("🥗 Résumé Nutritionnel (Aujourd'hui)")
    
    # Filtrer les données pour aujourd'hui
    today = datetime.date.today()
    patient_data['Date'] = patient_data['Date/Heure'].dt.date
    data_today = patient_data[patient_data['Date'] == today]
    
    total_glucides_today = data_today['Total Glucides (g)'].sum()
    
    st.metric(
        label="Glucides Consommés (Aujourd'hui)",
        value=f"{total_glucides_today:.1f} g"
    )
    
    # --- 3. Graphique d'Évolution ---
    st.header("📈 Historique de Glycémie")
    
    if not last_glycemie_data.empty:
        line_chart = alt.Chart(last_glycemie_data).mark_line(point=True).encode(
            x=alt.X('Date/Heure:T', title='Date et Heure'),
            y=alt.Y('Glycémie (mg/dL):Q', title='Glycémie (mg/dL)', scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip('Date/Heure:T', format='%d/%m/%Y %H:%M'), 
                'Glycémie (mg/dL)', 
                'Moment'
            ]
        ).interactive()
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.info("Aucun graphique de glycémie à afficher pour le moment.")

    # --- 4. Journal de Bord ---
    st.header("📓 Journal de Suivi (Dernières 20 entrées)")
    st.dataframe(
        patient_data.sort_values(by="Date/Heure", ascending=False).head(20), 
        use_container_width=True,
        hide_index=True
    )

# =============================================================================
# --- Exécution Principale de l'Application (avec "Login") ---
# =============================================================================

def main():
    # Initialiser le session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.current_user = None
    
    # Charger les bases de données
    user_df = load_user_db(USER_DB_FILE)
    st.session_state.data = load_data(DATA_FILE) # Charger les données pour tous

    # Afficher la page de login OU l'application principale
    if not st.session_state.logged_in:
        render_login_page(user_df) # Passer la DB utilisateur
    else:
        # Re-charger les données pour être sûr d'avoir la dernière version
        st.session_state.data = load_data(DATA_FILE)
        render_main_dashboard(st.session_state.current_user)

if __name__ == "__main__":
    main()

