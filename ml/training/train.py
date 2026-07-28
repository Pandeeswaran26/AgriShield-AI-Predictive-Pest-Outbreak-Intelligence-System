import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# -----------------------------
# Load Dataset
# -----------------------------
DATA_PATH = "datasets/processed/book2_features.csv"

df = pd.read_csv(DATA_PATH)

# -----------------------------
# Features & Target
# -----------------------------
X = df.drop(columns=["Pest Value"])
y = df["Pest Value"]

# -----------------------------
# Train/Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

# -----------------------------
# Model
# -----------------------------
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

# -----------------------------
# Prediction
# -----------------------------
predictions = model.predict(X_test)

# -----------------------------
# Evaluation
# -----------------------------
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = mse ** 0.5
r2 = r2_score(y_test, predictions)

print("=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")

# -----------------------------
# Save Model
# -----------------------------
os.makedirs("ml/models", exist_ok=True)

joblib.dump(model, "ml/models/pest_prediction_model.pkl")

print("\nModel saved successfully!")