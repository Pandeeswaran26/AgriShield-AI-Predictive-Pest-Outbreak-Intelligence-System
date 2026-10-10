"""
Crop Irrigation AI - Model Training Script
AgriShield Platform
============================================
Trains a RandomForestClassifier on the extended multi-crop irrigation
dataset (758 records, 9 crops) and saves:
  ml/models/irrigation_model.pkl
  ml/models/irrigation_metadata.json
  ml/models/irrigation_label_encoders.pkl
"""
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

ROOT = Path(__file__).resolve().parent.parent.parent  # ml/training -> ml -> AgriShield-AI
DATA_PROC = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "ml" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

print("=" * 60)
print("CROP IRRIGATION AI - MODEL TRAINING")
print("=" * 60)

# ─── 1. Load Extended Dataset ─────────────────────────────────────────
ext_path = DATA_PROC / "multi_crop_irrigation_extended.csv"
if not ext_path.exists():
    # Fall back to original
    ext_path = DATA_PROC / "multi_crop_irrigation.csv"
    print(f"[!] Extended dataset not found, using original: {ext_path}")

df = pd.read_csv(ext_path)
print(f"\n[1] Dataset loaded: {len(df)} rows, {df['crop_name'].nunique()} crops")
print(df["crop_name"].value_counts().to_string())

# ─── 2. Feature Engineering ───────────────────────────────────────────
# Encode crop_name
le_crop = LabelEncoder()
df["crop_encoded"] = le_crop.fit_transform(df["crop_name"])

# Derived agrometeorological features
df["heat_index"]    = df["temperature"] * df["humidity"] / 100.0
df["evap_potential"] = (df["temperature"] - df["soil_moisture"] * 0.1).round(2)
df["moisture_deficit"] = np.maximum(0, 25.0 - df["soil_moisture"])

FEATURE_COLS = [
    "crop_encoded",
    "crop_days",
    "soil_moisture",
    "soil_temperature",
    "temperature",
    "humidity",
    "rainfall",
    "heat_index",
    "evap_potential",
    "moisture_deficit",
]

X = df[FEATURE_COLS].values
y = df["irrigation"].values

print(f"\n[2] Feature matrix: {X.shape}")
print(f"    Label balance: 0={sum(y==0)}, 1={sum(y==1)}")

# ─── 3. Load splits ──────────────────────────────────────────────────
def _add_features(d):
    d = d.copy()
    d["crop_encoded"]    = le_crop.transform(d["crop_name"])
    d["heat_index"]      = d["temperature"] * d["humidity"] / 100.0
    d["evap_potential"]  = (d["temperature"] - d["soil_moisture"] * 0.1).round(2)
    d["moisture_deficit"]= np.maximum(0, 25.0 - d["soil_moisture"])
    return d

train_path = DATA_PROC / "train_ext.csv"
val_path   = DATA_PROC / "val_ext.csv"
test_path  = DATA_PROC / "test_ext.csv"

if train_path.exists():
    df_train = _add_features(pd.read_csv(train_path))
    df_val   = _add_features(pd.read_csv(val_path))
    df_test  = _add_features(pd.read_csv(test_path))
    X_train, y_train = df_train[FEATURE_COLS].values, df_train["irrigation"].values
    X_val,   y_val   = df_val[FEATURE_COLS].values,   df_val["irrigation"].values
    X_test,  y_test  = df_test[FEATURE_COLS].values,  df_test["irrigation"].values
    print(f"\n[3] Splits: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")
else:
    from sklearn.model_selection import train_test_split
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=RANDOM_SEED, stratify=y)
    X_val,   X_test, y_val,   y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=RANDOM_SEED, stratify=y_temp)
    print(f"\n[3] Auto-split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

# ─── 4. Train Model ──────────────────────────────────────────────────
clf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=RANDOM_SEED,
    n_jobs=-1,
)
clf.fit(X_train, y_train)
print("\n[4] RandomForestClassifier trained.")

# ─── 5. Evaluate ─────────────────────────────────────────────────────
def evaluate(name, X_eval, y_eval):
    preds = clf.predict(X_eval)
    proba = clf.predict_proba(X_eval)[:, 1]
    metrics = {
        "accuracy":  round(accuracy_score(y_eval, preds), 4),
        "precision": round(precision_score(y_eval, preds, zero_division=0), 4),
        "recall":    round(recall_score(y_eval, preds, zero_division=0), 4),
        "f1":        round(f1_score(y_eval, preds, zero_division=0), 4),
        "roc_auc":   round(roc_auc_score(y_eval, proba), 4),
        "confusion_matrix": confusion_matrix(y_eval, preds).tolist(),
    }
    print(f"\n    [{name}] acc={metrics['accuracy']} | f1={metrics['f1']} | auc={metrics['roc_auc']}")
    return metrics

metrics = {
    "train": evaluate("Train", X_train, y_train),
    "val":   evaluate("Val",   X_val,   y_val),
    "test":  evaluate("Test",  X_test,  y_test),
}
print()

# ─── 6. Feature Importance ────────────────────────────────────────────
importances = dict(zip(FEATURE_COLS, clf.feature_importances_.round(4).tolist()))
print("[5] Feature importances:")
for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
    print(f"    {feat:25s}: {imp:.4f}")

# ─── 7. Save artifacts ───────────────────────────────────────────────
model_path = MODELS_DIR / "irrigation_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(clf, f)

encoders_path = MODELS_DIR / "irrigation_label_encoders.pkl"
with open(encoders_path, "wb") as f:
    pickle.dump({"crop": le_crop}, f)

meta = {
    "model_type": "RandomForestClassifier",
    "n_estimators": 300,
    "max_depth": 12,
    "feature_cols": FEATURE_COLS,
    "crop_classes": le_crop.classes_.tolist(),
    "total_training_rows": int(len(X_train)),
    "test_metrics": metrics["test"],
    "val_metrics":  metrics["val"],
    "feature_importances": importances,
    "dataset": "multi_crop_irrigation_extended.csv",
    "version": "2.0",
}
meta_path = MODELS_DIR / "irrigation_metadata.json"
with open(meta_path, "w") as f:
    json.dump(meta, f, indent=2)

print(f"\n[6] Saved:")
print(f"    Model      -> {model_path}")
print(f"    Encoders   -> {encoders_path}")
print(f"    Metadata   -> {meta_path}")
print("\nIrrigation AI Training Complete!")
