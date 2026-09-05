import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "master_dataset_features.csv"
MODEL_DIR = PROJECT_ROOT / "ml" / "models"
METRICS_PATH = MODEL_DIR / "model_metrics.json"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

TARGET_COLUMN = "Pest Value"
TARGET_CAP_HIGH = 0.99
TARGET_CAP_LOW = 0.01

# ==========================
# Load Dataset
# ==========================

df = pd.read_csv(DATA_PATH)

print("Dataset Shape:", df.shape)

# Basic target diagnostics for the R2/RMSE story.
y = df[TARGET_COLUMN]
print("Target summary:")
print(y.describe())
print(f"Target std: {y.std(ddof=1):.2f}")
print(f"Target quantile 99%: {y.quantile(0.99):.2f}")
print(f"Target quantile 95%: {y.quantile(0.95):.2f}")
print(f"Target outliers (above 99th percentile): {(y > y.quantile(0.99)).sum()}")
print(f"Target outliers (below 1st percentile): {(y < y.quantile(0.01)).sum()}")

# ==========================
# Target quality controls
# ==========================

# High-end outliers are silently dominating the regression.
# Clip to the 99th percentile so the training objective is not dominated
# by a handful of impossible extreme values.
y_clip = y.clip(lower=0, upper=y.quantile(TARGET_CAP_HIGH))
# Keep a copy for reporting; store the original summary in metrics.

y_mean = float(y.mean())
y_std = float(y.std(ddof=1))
y_p01 = float(y.quantile(TARGET_CAP_LOW))
y_p99 = float(y.quantile(TARGET_CAP_HIGH))

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

X = df.drop(columns=[TARGET_COLUMN], errors="ignore")
y = y_clip

# ==========================
# Time-aware validation split
# ==========================
# Prefer a year-aware holdout over the previous random split which can leak
# future-year rows into training. This is a realistic business split.
if "Observation Year" in X.columns:
    unique_years = sorted(X["Observation Year"].dropna().unique())
    if len(unique_years) > 1:
        # train on the lower 80%, test on the upper 20% by Observation Year
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
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

print("Training Samples :", X_train.shape[0])
print("Testing Samples  :", X_test.shape[0])

# ==========================
# Train Model
# ==========================
# Train the regressor on a log-transformed target. This is a practical
# simulation-friendly improvement because the raw Pest Value is heavily right skewed.
# The API prediction pipeline stores the reverse-expansion contract so live
# responses are reported on the original scale.

model = ExtraTreesRegressor(
    n_estimators=250,
    random_state=42,
    n_jobs=-1,
    min_samples_leaf=1,
)

model.fit(X_train, np.log1p(y_train))

# ==========================
# Prediction
# ==========================

train_pred_log = model.predict(X_train)
test_pred_log = model.predict(X_test)

train_pred = np.expm1(train_pred_log)
test_pred = np.expm1(test_pred_log)

# ==========================
# Evaluation
# ==========================

metrics = {
    "dataset_shape": list(df.shape),
    "train_samples": int(X_train.shape[0]),
    "test_samples": int(X_test.shape[0]),
    "timestamp": pd.Timestamp.utcnow().isoformat(),
    "target_column": TARGET_COLUMN,
    "target_transform": "clip_to_p99_log1p",
    "target_inverse_transform": "expm1",
    "split_strategy": "year_aware_holdout",
}

metrics["train_mae"] = float(mean_absolute_error(y_train, train_pred))
metrics["train_rmse"] = float(mean_squared_error(y_train, train_pred) ** 0.5)
metrics["train_r2"] = float(r2_score(y_train, train_pred))
metrics["test_mae"] = float(mean_absolute_error(y_test, test_pred))
metrics["test_rmse"] = float(mean_squared_error(y_test, test_pred) ** 0.5)
metrics["test_r2"] = float(r2_score(y_test, test_pred))

metrics["target_summary"] = {
    "mean": y_mean,
    "std": y_std,
    "min": float(y.min()),
    "max": float(y.max()),
    "median": float(y.median()),
    "p01": y_p01,
    "p99": y_p99,
    "n_outliers_above_p99": int((y > y_p99).sum()),
    "n_outliers_below_p01": int((y < y_p01).sum()),
    "clipped_high_to_p99": y_p99,
    "train_test_split_year_cutoff": int(cutoff) if "cutoff" in locals() else None,
}

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print(f"TRAIN MAE  : {metrics['train_mae']:.4f}")
print(f"TRAIN RMSE : {metrics['train_rmse']:.4f}")
print(f"TRAIN R²   : {metrics['train_r2']:.4f}")
print(f"TEST MAE   : {metrics['test_mae']:.4f}")
print(f"TEST RMSE  : {metrics['test_rmse']:.4f}")
print(f"TEST R²    : {metrics['test_r2']:.4f}")

# ==========================
# Feature Importance
# ==========================

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False,
)

print("\nTop 10 Important Features:\n")
print(importance.head(10))

# ==========================
# Save Model
# ==========================

MODEL_DIR.mkdir(parents=True, exist_ok=True)

joblib.dump(model, MODEL_DIR / "final_pest_prediction_model.pkl")
joblib.dump(encoders, MODEL_DIR / "label_encoders.pkl")

metadata = {
    "target_transform": "clip_to_p99_log1p",
    "inverse_transform": "expm1",
    "feature_columns": list(X.columns),
    "target_column": TARGET_COLUMN,
}

with METADATA_PATH.open("w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

with METRICS_PATH.open("w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print("\nModel Saved Successfully!")
print(f"Metrics saved to: {METRICS_PATH}")
print(f"Model metadata saved to: {METADATA_PATH}")