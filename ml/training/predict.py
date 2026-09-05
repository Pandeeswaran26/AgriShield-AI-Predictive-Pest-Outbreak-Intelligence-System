import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import FINAL_MODEL_PATH, ENCODERS_PATH, METADATA_PATH


class PestPredictor:
    def __init__(self):
        self.model = joblib.load(FINAL_MODEL_PATH)
        self.encoders = joblib.load(ENCODERS_PATH)
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def predict_sample(self, feature_dict: dict) -> dict:
        df = pd.DataFrame([feature_dict])

        # Encode categorical columns
        for col in ["Crop", "Pest_Name", "Location", "Rainfall_Category"]:
            if col in df.columns:
                val = str(df[col].iloc[0]).strip().title()
                encoder = self.encoders[col]
                # Find best matching class
                classes = list(encoder.classes_)
                matched = next((c for c in classes if c.lower() == val.lower()), classes[0])
                df[col] = encoder.transform([matched])[0]

        pred_log = float(self.model.predict(df)[0])
        if self.metadata.get("target_transform") == "clip_to_p99_log1p":
            pred = float(np.expm1(pred_log))
        else:
            pred = pred_log

        risk = "Low" if pred < 20 else "Medium" if pred < 50 else "High"

        return {
            "predicted_pest_value": round(pred, 2),
            "risk_level": risk,
        }


if __name__ == "__main__":
    predictor = PestPredictor()
    sample = {
        "Crop": "Cotton",
        "Observation Year": 2024,
        "Standard Week": 32,
        "Pest_Name": "Bollworm",
        "Location": "Coimbatore",
        "MaxT": 34.5,
        "MinT": 23.5,
        "RH1(%)": 85.0,
        "RH2(%)": 70.0,
        "RF(mm)": 35.0,
        "WS(kmph)": 14.0,
        "SSH(hrs)": 4.5,
        "EVP(mm)": 5.0,
        "Temp_Diff": 11.0,
        "Avg_Humidity": 77.5,
        "Week_Sin": 0.5,
        "Week_Cos": -0.86,
        "Weather_Index": 238.5,
        "Rainfall_Category": "Medium",
    }
    result = predictor.predict_sample(sample)
    print("Test Offline Prediction:", result)
