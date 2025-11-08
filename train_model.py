import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import r2_score
import joblib
import os

print("🚀 Script d'entraînement démarré...")

# ============================================================
# 1. Chargement des données
# ============================================================

# Option 1 : Télécharger automatiquement avec kagglehub
try:
    import kagglehub
    print("Téléchargement du dataset depuis KaggleHub...")
    path = kagglehub.dataset_download("shivachandel/kc-house-data")
    data_path = os.path.join(path, "kc_house_data.csv")
    data = pd.read_csv(data_path)
    print(f"Données chargées depuis : {data_path}")
except Exception as e:
    print(f"⚠️ Échec du téléchargement via KaggleHub ({e}).")
    print("➡️ Assurez-vous d’avoir téléchargé manuellement le fichier 'kc_house_data.csv'")
    exit(1)

print(f"✅ Données chargées avec succès : {data.shape[0]} lignes, {data.shape[1]} colonnes.")

# ============================================================
# 2. Sélection des Features et définition X / y
# ============================================================

TARGET = 'price'
NUMERIC_FEATURES = ['sqft_living', 'bedrooms', 'bathrooms', 'floors']
CATEGORICAL_FEATURES = ['waterfront', 'condition']

selected_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET]

# Vérification des colonnes présentes
missing_cols = [col for col in selected_columns if col not in data.columns]
if missing_cols:
    raise ValueError(f"Colonnes manquantes dans le dataset : {missing_cols}")

data_subset = data[selected_columns].copy()

# 'condition' est traitée comme catégorie
data_subset['condition'] = data_subset['condition'].astype(str)

X = data_subset.drop(columns=[TARGET])
y = data_subset[TARGET]

# ============================================================
# 3. Séparation des données
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"✅ Données divisées : {X_train.shape[0]} train / {X_test.shape[0]} test")

# ============================================================
# 4. Définition du pipeline de prétraitement
# ============================================================

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(transformers=[
    ('num', numeric_transformer, NUMERIC_FEATURES),
    ('cat', categorical_transformer, CATEGORICAL_FEATURES)
])

# ============================================================
# 5. Création du pipeline complet (prétraitement + modèle)
# ============================================================

model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    ))
])

# ============================================================
# 6. Entraînement
# ============================================================

print("🧠 Entraînement du pipeline complet...")
model_pipeline.fit(X_train, y_train)
print("✅ Entraînement terminé.")

# ============================================================
# 7. Évaluation
# ============================================================

print("📊 Évaluation du modèle...")
y_pred = model_pipeline.predict(X_test)
score = r2_score(y_test, y_pred)
print(f"🎯 Score R² sur le jeu de test : {score:.4f}")

# ============================================================
# 8. Sauvegarde du modèle
# ============================================================

os.makedirs("models", exist_ok=True)
MODEL_FILE = os.path.join("models", "model_pipeline.joblib")

joblib.dump(model_pipeline, MODEL_FILE)
print(f"💾 Pipeline sauvegardé sous : {MODEL_FILE}")

print("✅ Script d'entraînement terminé avec succès.")
