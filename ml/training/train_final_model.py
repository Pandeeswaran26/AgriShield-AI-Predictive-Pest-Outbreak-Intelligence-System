import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# ==========================
# Load Dataset
# ==========================

df = pd.read_csv("datasets/processed/master_dataset_features.csv")

print("Dataset Shape:", df.shape)

# ==========================
# Encode Categorical Columns
# ==========================

encoders = {}

categorical_columns = [
    "Crop",
    "Pest_Name",
    "Location",
    "Rainfall_Category"
]

for col in categorical_columns:
    encoder = LabelEncoder()
    df[col] = encoder.fit_transform(df[col].astype(str))
    encoders[col] = encoder

# ==========================
# Features & Target
# ==========================

X = df.drop(columns=["Pest Value"])
y = df["Pest Value"]

# ==========================
# Train Test Split
# ==========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Training Samples :", X_train.shape[0])
print("Testing Samples  :", X_test.shape[0])

# ==========================
# Train Model
# ==========================

model = ExtraTreesRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ==========================
# Prediction
# ==========================

pred = model.predict(X_test)

# ==========================
# Evaluation
# ==========================

mae = mean_absolute_error(y_test, pred)
rmse = mean_squared_error(y_test, pred) ** 0.5
r2 = r2_score(y_test, pred)

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")

# ==========================
# Feature Importance
# ==========================

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print("\nTop 10 Important Features:\n")
print(importance.head(10))

# ==========================
# Save Model
# ==========================

os.makedirs("ml/models", exist_ok=True)

joblib.dump(model, "ml/models/final_pest_prediction_model.pkl")
joblib.dump(encoders, "ml/models/label_encoders.pkl")

print("\nModel Saved Successfully!")