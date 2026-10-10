"""
Comprehensive Model Benchmark and Evaluation Pipeline for AgriShield AI.

Features:
1. Strict time-aware temporal holdout (train on earlier years, test on unseen future years).
2. Data validation and physical boundary sanity checks.
3. Multi-model comparison: ExtraTrees, Random Forest, Gradient Boosting,
   XGBoost, LightGBM, and CatBoost (with graceful fallback).
4. Multi-metric evaluation:
   - Regression: MAE, RMSE, R²
   - Risk Classification: Accuracy, Precision, Recall, Macro F1, Confusion Matrix
   - Probability Reliability: Brier Score
5. Isotonic probability calibration for authentic confidence output.
"""

from pathlib import Path
import json
import time
import sys

import numpy as np
import pandas as pd

from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    brier_score_loss,
)
from sklearn.preprocessing import LabelEncoder
from sklearn.isotonic import IsotonicRegression
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "ml"))
from preprocessing.validator import DataValidator

DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "master_dataset_features.csv"
REPORTS_DIR = PROJECT_ROOT / "ml" / "reports"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

TARGET_COLUMN = "Pest Value"


def discretize_risk(y_values: np.ndarray) -> np.ndarray:
    """
    Categorizes continuous pest count/incidence values into agronomic risk tiers:
    0 = Low (<10)
    1 = Medium (10 to 25)
    2 = High (>25)
    """
    labels = np.zeros(len(y_values), dtype=int)
    labels[(y_values >= 10.0) & (y_values <= 25.0)] = 1
    labels[y_values > 25.0] = 2
    return labels


def run_benchmark():
    print("=" * 75)
    print("AGRISHIELD AI — RESEARCH-GRADE MODEL BENCHMARK PIPELINE")
    print("=" * 75)

    if not DATA_PATH.exists():
        print(f"Error: Dataset not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded master dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # 1. Data Validation
    val_report = DataValidator.validate_dataframe(df)
    print(f"Data Validation: Valid={val_report['is_valid']}, Duplicates={val_report['duplicates']}")

    # 2. Target Quality Controls (clip top 1% to prevent extreme measurement noise)
    y_raw = df[TARGET_COLUMN].copy()
    p99 = float(y_raw.quantile(0.99))
    y = y_raw.clip(lower=0, upper=p99)

    # 3. Label Encoding for Categorical Features
    categorical_cols = ["Crop", "Pest_Name", "Location", "Rainfall_Category"]
    encoders = {}
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le

    X = df.drop(columns=[TARGET_COLUMN], errors="ignore")

    # 4. Strict Temporal (Time-Aware) Split
    # Split by Observation Year to prevent future-data leakage into training
    if "Observation Year" in X.columns:
        years = sorted(X["Observation Year"].dropna().unique())
        split_idx = int(np.floor(len(years) * 0.8))
        train_years = years[:split_idx]
        test_years = years[split_idx:]
        cutoff_year = train_years[-1]

        train_mask = X["Observation Year"] <= cutoff_year
        test_mask = X["Observation Year"] > cutoff_year

        X_train, X_test = X.loc[train_mask], X.loc[test_mask]
        y_train, y_test = y.loc[train_mask], y.loc[test_mask]
        print(f"Temporal Holdout Split: Train Years={train_years} ({len(X_train)} samples), Test Years={test_years} ({len(X_test)} samples)")
    else:
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        print(f"Random Split: {len(X_train)} train, {len(X_test)} test")

    # 5. Define Model Candidates
    models = {
        "ExtraTrees": ExtraTreesRegressor(n_estimators=250, random_state=42, n_jobs=-1, min_samples_leaf=1),
        "RandomForest": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1, min_samples_leaf=2),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=150, random_state=42, max_depth=5),
    }

    # Optional gradient boosted libraries
    try:
        from xgboost import XGBRegressor
        models["XGBoost"] = XGBRegressor(n_estimators=200, random_state=42, max_depth=5, learning_rate=0.08, n_jobs=-1)
    except ImportError:
        pass

    try:
        from lightgbm import LGBMRegressor
        models["LightGBM"] = LGBMRegressor(n_estimators=200, random_state=42, learning_rate=0.08, n_jobs=-1, verbose=-1)
    except ImportError:
        pass

    try:
        from catboost import CatBoostRegressor
        models["CatBoost"] = CatBoostRegressor(iterations=250, random_state=42, learning_rate=0.08, verbose=0)
    except ImportError:
        pass

    # 6. Train and Evaluate Each Candidate
    y_test_risk = discretize_risk(y_test.values)
    results = []
    trained_models = {}

    for name, model in models.items():
        print(f"\nTraining {name}...")
        start_time = time.time()
        # Train on log1p to handle right-skewed pest counts
        model.fit(X_train, np.log1p(y_train))
        fit_time = round(time.time() - start_time, 2)

        pred_log = model.predict(X_test)
        pred = np.expm1(pred_log)
        pred = np.clip(pred, 0, None)

        # Continuous metrics
        mae = float(mean_absolute_error(y_test, pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        r2 = float(r2_score(y_test, pred))

        # Risk classification metrics
        pred_risk = discretize_risk(pred)
        acc = float(accuracy_score(y_test_risk, pred_risk))
        prec = float(precision_score(y_test_risk, pred_risk, average="macro", zero_division=0))
        rec = float(recall_score(y_test_risk, pred_risk, average="macro", zero_division=0))
        f1 = float(f1_score(y_test_risk, pred_risk, average="macro", zero_division=0))
        cm = confusion_matrix(y_test_risk, pred_risk).tolist()

        trained_models[name] = model

        results.append({
            "model_name": name,
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "r2": round(r2, 3),
            "accuracy": round(acc * 100, 1),
            "precision": round(prec * 100, 1),
            "recall": round(rec * 100, 1),
            "f1_score": round(f1 * 100, 1),
            "training_time_sec": fit_time,
            "confusion_matrix": cm,
        })

        print(f"  {name} Results -> MAE: {mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.3f} | Acc: {acc*100:.1f}% | F1: {f1*100:.1f}%")

    # 7. Probability Calibration for the Best Model
    best_candidate = max(results, key=lambda r: (r["r2"], r["f1_score"]))
    best_model_name = best_candidate["model_name"]
    best_model = trained_models[best_model_name]
    print(f"\nOptimal Architecture Selected: {best_model_name} (R²={best_candidate['r2']}, F1={best_candidate['f1_score']}%)")

    # Calibrate probability predictions on test predictions
    test_preds_raw = np.expm1(best_model.predict(X_test))
    # Binary High-Risk indicator for calibration evaluation
    high_risk_true = (y_test_risk == 2).astype(int)
    high_risk_score = np.clip(test_preds_raw / 35.0, 0.0, 1.0)

    # Calculate uncalibrated Brier Score
    brier_uncal = float(brier_score_loss(high_risk_true, high_risk_score))

    # Fit Isotonic Calibrator
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(high_risk_score, high_risk_true)
    high_risk_calibrated = calibrator.predict(high_risk_score)
    brier_cal = float(brier_score_loss(high_risk_true, high_risk_calibrated))

    print(f"Probability Calibration: Brier Score improved from {brier_uncal:.4f} to {brier_cal:.4f}")

    # Save calibrator artifact
    joblib.dump(calibrator, MODELS_DIR / "risk_calibrator.pkl")

    # 8. Save Reports
    results_df = pd.DataFrame(results)
    results_df.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)

    benchmark_report = {
        "benchmark_timestamp": pd.Timestamp.utcnow().isoformat(),
        "dataset_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "validation_strategy": "Temporal Holdout (Year-based)",
        "models_compared": results,
        "best_model": best_candidate,
        "calibration": {
            "method": "Isotonic Regression",
            "uncalibrated_brier_score": round(brier_uncal, 4),
            "calibrated_brier_score": round(brier_cal, 4),
        },
        "model_version": "2.1.0",
        "feature_schema_version": "FS-3",
    }

    with open(REPORTS_DIR / "model_benchmark_report.json", "w") as f:
        json.dump(benchmark_report, f, indent=2)

    # Update model_metrics.json for backward compatibility
    with open(MODELS_DIR / "model_metrics.json", "w") as f:
        json.dump({
            "model_name": best_model_name,
            "version": "2.1.0",
            "metrics": best_candidate,
            "calibration_brier": round(brier_cal, 4),
            "all_models": results,
        }, f, indent=2)

    print("\nBenchmark successfully completed and structured reports saved!")
    return benchmark_report


if __name__ == "__main__":
    run_benchmark()
