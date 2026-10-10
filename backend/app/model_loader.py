import json
from pathlib import Path

import joblib

# Project root: AgriShield-AI
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ml" / "models" / "final_pest_prediction_model.pkl"
ENCODER_PATH = BASE_DIR / "ml" / "models" / "label_encoders.pkl"
METADATA_PATH = BASE_DIR / "ml" / "models" / "model_metadata.json"
CALIBRATOR_PATH = BASE_DIR / "ml" / "models" / "risk_calibrator.pkl"

print(f"Loading model from: {MODEL_PATH}")
print(f"Loading encoders from: {ENCODER_PATH}")
print(f"Loading metadata from: {METADATA_PATH}")

model = joblib.load(MODEL_PATH)
encoders = joblib.load(ENCODER_PATH)

with METADATA_PATH.open("r", encoding="utf-8") as f:
    model_metadata = json.load(f)

risk_calibrator = None
if CALIBRATOR_PATH.exists():
    try:
        risk_calibrator = joblib.load(CALIBRATOR_PATH)
        print("Risk Calibrator Loaded")
    except Exception as e:
        print(f"Notice: Calibrator load deferred: {e}")

print("AI Model Loaded")
print("Label Encoders Loaded")
print("Model Metadata Loaded")