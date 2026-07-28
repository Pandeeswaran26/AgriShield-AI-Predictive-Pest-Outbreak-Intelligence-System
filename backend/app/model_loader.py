from pathlib import Path
import joblib

# Project root: AgriShield-AI
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ml" / "models" / "final_pest_prediction_model.pkl"
ENCODER_PATH = BASE_DIR / "ml" / "models" / "label_encoders.pkl"

print(f"Loading model from: {MODEL_PATH}")
print(f"Loading encoders from: {ENCODER_PATH}")

model = joblib.load(MODEL_PATH)
encoders = joblib.load(ENCODER_PATH)

print("✅ AI Model Loaded")
print("✅ Label Encoders Loaded")