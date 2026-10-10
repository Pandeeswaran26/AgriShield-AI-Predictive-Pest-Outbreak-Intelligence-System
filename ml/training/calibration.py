"""
AgriShield AI — Probability Calibration Pipeline.

Implements isotonic regression calibration for the ExtraTrees pest risk predictor.
Calibrates raw predicted pest values → calibrated High-Risk probability scores.
Outputs:
  - ml/models/risk_calibrator.pkl   (IsotonicRegression fitted object)
  - ml/reports/calibration_report.json

Usage:
    python ml/training/calibration.py
"""

from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import joblib

from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import cross_val_score

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

from preprocessing.validator import DataValidator

DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "master_dataset_features.csv"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
REPORTS_DIR = PROJECT_ROOT / "ml" / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_MODEL_PATH = MODELS_DIR / "final_pest_prediction_model.pkl"
CALIBRATOR_OUTPUT = MODELS_DIR / "risk_calibrator.pkl"
REPORT_OUTPUT = REPORTS_DIR / "calibration_report.json"

TARGET_COLUMN = "Pest Value"

# Risk thresholds matching the main prediction pipeline
LOW_THRESHOLD = 10.0
HIGH_THRESHOLD = 25.0


def discretize_high_risk(y_values: np.ndarray) -> np.ndarray:
    """Binary label: 1 = High risk (>25), 0 = Low/Medium."""
    return (y_values > HIGH_THRESHOLD).astype(int)


def run_calibration():
    print("=" * 70)
    print("AGRISHIELD AI — PROBABILITY CALIBRATION PIPELINE")
    print("=" * 70)

    # ── 1. Load Dataset ────────────────────────────────────────────────────
    if not DATA_PATH.exists():
        print(f"[ERROR] Dataset not found: {DATA_PATH}")
        print("Run ml/preprocessing/create_master_dataset.py first.")
        return

    if not PRIMARY_MODEL_PATH.exists():
        print(f"[ERROR] Primary model not found: {PRIMARY_MODEL_PATH}")
        print("Run ml/training/train_final_model.py first.")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset: {df.shape[0]} rows × {df.shape[1]} columns")

    # ── 2. Validate Data ───────────────────────────────────────────────────
    val_report = DataValidator.validate_dataframe(df)
    print(f"Validation: valid={val_report['is_valid']} | duplicates={val_report['duplicates']}")

    # ── 3. Load Trained Model ──────────────────────────────────────────────
    model = joblib.load(PRIMARY_MODEL_PATH)
    print(f"Loaded model: {type(model).__name__}")

    # ── 4. Temporal Split (same as training) ──────────────────────────────
    from sklearn.preprocessing import LabelEncoder

    y_raw = df[TARGET_COLUMN].copy()
    p99 = float(y_raw.quantile(0.99))
    y = y_raw.clip(lower=0, upper=p99)

    categorical_cols = ["Crop", "Pest_Name", "Location", "Rainfall_Category"]
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))

    X = df.drop(columns=[TARGET_COLUMN], errors="ignore")

    if "Observation Year" in X.columns:
        years = sorted(X["Observation Year"].dropna().unique())
        split_idx = int(np.floor(len(years) * 0.8))
        cutoff_year = years[split_idx - 1]
        train_mask = X["Observation Year"] <= cutoff_year
        test_mask = X["Observation Year"] > cutoff_year
        X_train, X_test = X.loc[train_mask], X.loc[test_mask]
        y_train, y_test = y.loc[train_mask], y.loc[test_mask]
        print(f"Temporal split: {len(X_train)} train / {len(X_test)} test")
    else:
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # ── 5. Generate Raw Predictions ────────────────────────────────────────
    pred_log = model.predict(X_test)
    pred = np.expm1(pred_log)
    pred = np.clip(pred, 0, None)

    # Convert raw pest value to a probability proxy for high-risk
    # Sigmoid-like mapping: p(high) = pred / (HIGH_THRESHOLD * 1.5)
    raw_prob = np.clip(pred / (HIGH_THRESHOLD * 1.5), 0.0, 1.0)

    y_binary = discretize_high_risk(y_test.values)

    # ── 6. Uncalibrated Brier Score ────────────────────────────────────────
    brier_uncal = float(brier_score_loss(y_binary, raw_prob))
    print(f"Uncalibrated Brier Score: {brier_uncal:.4f}")

    # ── 7. Fit Isotonic Regression Calibrator ─────────────────────────────
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(raw_prob, y_binary)
    cal_prob = calibrator.predict(raw_prob)

    brier_cal = float(brier_score_loss(y_binary, cal_prob))
    improvement_pct = round((brier_uncal - brier_cal) / max(brier_uncal, 1e-9) * 100, 1)
    print(f"Calibrated Brier Score:   {brier_cal:.4f}  (Δ={improvement_pct}% improvement)")

    # ── 8. Save Calibrator ─────────────────────────────────────────────────
    joblib.dump(calibrator, CALIBRATOR_OUTPUT)
    print(f"Calibrator saved → {CALIBRATOR_OUTPUT}")

    # ── 9. Generate Calibration Report ────────────────────────────────────
    # Build reliability diagram data (10 bins)
    n_bins = 10
    bin_edges = np.linspace(0, 1, n_bins + 1)
    reliability_data = []
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = (cal_prob >= lo) & (cal_prob < hi)
        if mask.sum() > 0:
            mean_pred = float(np.mean(cal_prob[mask]))
            mean_true = float(np.mean(y_binary[mask]))
            reliability_data.append({
                "bin_lower": round(lo, 2),
                "bin_upper": round(hi, 2),
                "count": int(mask.sum()),
                "mean_predicted_prob": round(mean_pred, 3),
                "fraction_positives": round(mean_true, 3),
            })

    report = {
        "calibration_timestamp": pd.Timestamp.utcnow().isoformat(),
        "method": "Isotonic Regression",
        "target": "High Risk Binary (pest_value > 25)",
        "test_samples": int(len(X_test)),
        "uncalibrated_brier_score": round(brier_uncal, 4),
        "calibrated_brier_score": round(brier_cal, 4),
        "brier_improvement_pct": improvement_pct,
        "reliability_diagram": reliability_data,
        "calibrator_path": str(CALIBRATOR_OUTPUT),
        "notes": (
            "Isotonic calibration maps raw predicted pest-value probability proxies "
            "to empirically verified high-risk probabilities. "
            "The Brier score measures the mean squared error of probabilistic predictions."
        ),
    }

    with open(REPORT_OUTPUT, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Calibration report saved → {REPORT_OUTPUT}")
    print("\nCalibration pipeline completed successfully.")
    return report


if __name__ == "__main__":
    run_calibration()
