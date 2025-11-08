# Projet WebApp de Prédiction - Prix Immobiliers (King County)
## 1. Objectif du Projet
L'objectif de ce projet est de construire une application web locale avec Streamlit qui prédit le prix d'une maison individuelle dans la région de King County, USA (région de Seattle).
L'application utilise un modèle de Machine Learning (Régression) pour effectuer les prédictions.
## 2. Structure du Projet
  ●	train_model.py: Script Python pour :
    1.	Télécharger le dataset "King County House Sales".
    2.	Sélectionner les features pertinentes.
    3.	Définir un pipeline de prétraitement avancé (ColumnTransformer).
    4.	Entraîner un modèle RandomForestRegressor.
    5.	Créer un dossier models/ et y sauvegarder le pipeline complet (model_pipeline.joblib).
  ●	app.py: Application Streamlit qui charge models/model_pipeline.joblib. Elle fournit une interface utilisateur ergonomique (sliders, listes déroulantes) pour saisir les caractéristiques de la maison et obtenir une prédiction de prix.
  ●	models/model_pipeline.joblib: Fichier binaire du modèle, généré par train_model.py.
  ●	requirements.txt: La liste des dépendances Python.
  ●	README.md: Ce document.
## 3. Dataset et Modèle
  ### Dataset
Nous utilisons le "King County House Sales Dataset". Nous avons sélectionné 6 caractéristiques (features) pour leur pertinence auprès de l'utilisateur final :
  ●	Numériques :
  ○	sqft_living: Surface habitable (en pieds carrés).
  ○	bedrooms: Nombre de chambres.
  ○	bathrooms: Nombre de salles de bain.
  ○	floors: Nombre d'étages.
  ●	Catégorielles :
  ○	waterfront: Vue sur l'eau (0 pour Non, 1 pour Oui).
  ○	condition: État de la maison (sur une échelle de 1 à 5).
  La cible (target) est le price (prix de vente) de la maison.
  ### Modèle
Nous utilisons un Pipeline scikit-learn avancé pour gérer les différents types de données.
  ●	Un ColumnTransformer est utilisé pour appliquer les bonnes transformations aux bonnes colonnes.
    1.	Pour les features numériques : Un SimpleImputer (stratégie median) suivi d'un StandardScaler.
    2.	Pour les features catégorielles : Un SimpleImputer (stratégie most_frequent) suivi d'un OneHotEncoder.
  ●	Ces features prétraitées sont ensuite envoyées à un régresseur RandomForestRegressor (100 arbres) pour la prédiction finale.
  Cette structure est robuste et garantit que les données saisies par l'utilisateur dans l'application subissent exactement le même traitement que les données d'entraînement.
## 4. Comment Lancer le Projet (Localement)
Suivez ces étapes dans votre terminal :
 ### 1. Installer les dépendances :
# (Recommandé) Créez un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sur Windows

# Installez les bibliothèques requises
pip install -r requirements.txt

 ### 2. Entraîner le modèle (Étape unique) :
Cette commande va télécharger les données, créer un dossier models/, et y sauvegarder le fichier model_pipeline.joblib.
python train_model.py

Vous devriez voir des messages de confirmation, incluant le score R² et le chemin de sauvegarde.
 ### 3. Lancer l'application Streamlit :
Une fois le modèle entraîné, lancez l'application web.
streamlit run app.py

Votre navigateur s'ouvrira automatiquement et affichera votre application.
Projet réalisé par : 
-	MAHAMAT SULTAN.
-	Moustapha MEMDY
