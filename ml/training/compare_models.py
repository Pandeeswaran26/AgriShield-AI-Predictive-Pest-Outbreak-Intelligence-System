from pathlib import Path
import json
import time

import numpy as np
import pandas as pd

from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "master_dataset_features.csv"
MODEL_COMPARISON_PATH = PROJECT_ROOT / "ml" / "reports" / "model_comparison.csv"
MODEL_COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)

TARGET_COLUMN = "Pest Value"

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv(DATA_PATH)

# -----------------------------
# Target clipping for the comparison run (same as training)
# -----------------------------
y = df[TARGET_COLUMN]
y = y.clip(lower=0, upper=y.quantile(0.99))

df[TARGET_COLUMN] = y

# -----------------------------
# Encode categorical columns exactly like the main training script
# -----------------------------
encoders = {}
categorical_columns = ["Crop", "Pest_Name", "Location", "Rainfall_Category"]
for col in categorical_columns:
    encoder = LabelEncoder()
    df[col] = encoder.fit_transform(df[col].astype(str))
    encoders[col] = encoder

# -----------------------------
# Features and Target
# -----------------------------
X = df.drop(columns=[TARGET_COLUMN], errors="ignore")
y = df[TARGET_COLUMN]

# -----------------------------
# Time-aware validation split
# -----------------------------
if "Observation Year" in X.columns:
    unique_years = sorted(X["Observation Year"].dropna().unique())
    cutoff = unique_years[int(np.floor(len(unique_years) * 0.8))]
    train_mask = X["Observation Year"] <= cutoff
    test_mask = X["Observation Year"] > cutoff
    X_train = X.loc[train_mask]
    X_test = X.loc[test_mask]
    y_train = y.loc[train_mask]
    y_test = y.loc[test_mask]
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

# -----------------------------
# Models
# -----------------------------
models = {
    "Random Forest": RandomForestRegressor(random_state=42, n_estimators=200, n_jobs=-1),
    "Extra Trees": ExtraTreesRegressor(random_state=42, n_estimators=250, n_jobs=-1),
    "Gradient Boosting": GradientBoostingRegressor(random_state=42, n_estimators=120),
}

# Optional third-party models can be added when installed.
try:
    from xgboost import XGBRegressor
    models["XGBoost"] = XGBRegressor(random_state=42, objective="reg:squarederror", n_estimators=200)
except Exception:
    pass

try:
    from lightgbm import LGBMRegressor
    models["LightGBM"] = LGBMRegressor(random_state=42, n_estimators=150)
except Exception:
    pass

try:
    from catboost import CatBoostRegressor
    models["CatBoost"] = CatBoostRegressor(verbose=0, random_state=42, iterations=250)
except Exception:
    pass

results = []

print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

# -----------------------------
# Train Every Model
# -----------------------------
for name, model in models.items():
    print(f"\nTraining {name}...")
    start = time.time()
    model.fit(X_train, y_train)
    end = time.time()

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)

    training_time = round(end - start, 2)

    results.append({
        "Model": name,
        "MAE": round(mae, 3),
        "RMSE": round(rmse, 3),
        "R2": round(r2, 3),
        "Training Time (sec)": training_time,
    })

# -----------------------------
# Display Results
# -----------------------------
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="R2", ascending=False)

print("\n")
print(results_df)

# -----------------------------
# Save Results
# -----------------------------
results_df.to_csv(MODEL_COMPARISON_PATH, index=False)

print("\nComparison report saved successfully!")