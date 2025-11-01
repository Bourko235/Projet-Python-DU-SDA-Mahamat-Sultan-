# Projet-Python-DU-SDA-Mahamat-Sultan-
Projet Python DU SDA Mahamat Sultan 

# GlucoSuivi - Application de Suivi de Diabète (Projet Streamlit)

Ce projet est une application web locale développée en Python avec Streamlit, conçue pour aider les patients diabétiques à suivre leur glycémie et leur apport nutritionnel.

1. Objectif du Projet

L'objectif de GlucoSuivi est de fournir une application complète et sécurisée permettant aux patients de :
Créer un compte personnel et s'y connecter de manière sécurisée.
Enregistrer leurs mesures de glycémie et leurs repas quotidiens.
Recevoir des conseils immédiats basés sur leurs niveaux de glycémie.
Visualiser leur historique pour mieux comprendre l'impact de leur nutrition sur leur glycémie.
L'application est conçue pour être utilisée localement, en centralisant les données dans des fichiers CSV pour une éventuelle analyse par un investigateur.

2. Fonctionnalités Principales

Piliers de l'Application (Inputs, Traitement, Dashboard)
Inputs - Une Interface Sécurisée et Complète
Système d'Authentification :
Inscription : Les nouveaux utilisateurs peuvent créer un compte. Les mots de passe sont hashés (en utilisant hashlib SHA-256) et stockés dans un fichier user_db.csv, garantissant qu'aucun mot de passe n'est sauvegardé en clair.
Connexion : Les utilisateurs existants se connectent avec leur ID Patient et mot de passe.
Saisie de Données (Sidebar) :
Suivi Glycémie : Saisie du taux de glycémie (mg/dL) et du moment de la mesure (à jeun, post-repas, etc.).
Suivi Repas : Sélection d'un aliment depuis une base de données intégrée ou ajout d'un aliment "Autre" avec ses propres macros (glucides).
Calcul de Glucides : L'application calcule automatiquement le total de glucides pour le repas saisi en fonction de la quantité.
Traitement - Une Logique de Conseil
Analyse en Temps Réel : L'application analyse chaque nouvelle entrée de glycémie et la compare à des seuils prédéfinis (hypoglycémie, optimal, élevé).
Conseils Contextuels : Un message (delta) et un conseil clair sont générés et affichés à l'utilisateur (ex: "Hypoglycémie", "Mangez 15g de sucre...").
Persistance des Données :
user_db.csv : Stocke les informations des utilisateurs (ID et hash de mot de passe).
diabete_master_data.csv : Stocke toutes les entrées de données (glycémie, repas) de tous les utilisateurs, les rendant disponibles pour une analyse centrale.

Dashboard - Une Visualisation Claire
Flash Info Glycémie : Affiche la dernière mesure de glycémie, le diagnostic (ex: "Optimal") et le conseil associé.
Résumé Nutritionnel : Une carte st.metric affiche le total des glucides consommés pour la journée en cours.
Historique de Glycémie : Un graphique en ligne (Altair) montre l'évolution de la glycémie de l'utilisateur dans le temps.
Journal de Bord : Un tableau (st.dataframe) affiche les 20 dernières entrées de l'utilisateur (glycémie et repas) pour un suivi détaillé.
3. Comment Lancer l'Application
Ce projet est une application locale et ne nécessite aucun déploiement.
Prérequis
Python 3.x
pip (le gestionnaire de paquets Python)
1. Cloner ou Télécharger le Dépôt
Assurez-vous d'avoir le fichier app.py dans un dossier.
2. (Recommandé) Créer un Environnement Virtuel
Ouvrez un terminal dans le dossier du projet et exécutez :
# Créer l'environnement
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\activate
# ou (Mac/Linux)
source venv/bin/activate


3. Installer les Dépendances
Installez les bibliothèques nécessaires :
pip install streamlit pandas altair


4. Lancer l'Application
Toujours dans le terminal, exécutez :
streamlit run app.py

L'application s'ouvrira automatiquement dans votre navigateur par défaut.

Projet réalisé par Mahamat Sultan dans le cadre du cours Python du DU Sorbonne Data Analytics.

