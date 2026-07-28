import re
import numpy as np
import pandas as pd
from fastapi import HTTPException

from .model_loader import model, encoders
from .utils import calculate_risk


# --------------------------------------------------
# Robust label normalization
# --------------------------------------------------
def normalize_label(label: str) -> str:
    """
    Normalize labels so they always match LabelEncoder classes.
    """

    if label is None:
        return ""

    label = str(label)

    # Replace unicode spaces
    label = label.replace("\u00A0", " ")

    # Collapse multiple spaces
    label = re.sub(r"\s+", " ", label)

    # Lowercase
    label = label.lower()

    return label.strip()


# --------------------------------------------------
# Encode categorical value safely
# --------------------------------------------------
def encode_value(encoder, value, field_name):

    mapping = {
        normalize_label(cls): cls
        for cls in encoder.classes_
    }

    key = normalize_label(value)

    if key not in mapping:

        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Unknown {field_name}",
                "received": value,
                "available_values": sorted(mapping.keys())
            }
        )

    return encoder.transform([mapping[key]])[0]


# --------------------------------------------------
# Prediction
# --------------------------------------------------
def predict(data):

    # Encode categorical features
    crop = encode_value(encoders["Crop"], data.Crop, "Crop")

    pest = encode_value(
        encoders["Pest_Name"],
        data.Pest_Name,
        "Pest_Name"
    )

    location = encode_value(
        encoders["Location"],
        data.Location,
        "Location"
    )

    # Rainfall Category
    if data.RF < 10:
        rainfall_category = "Low"
    elif data.RF < 50:
        rainfall_category = "Medium"
    else:
        rainfall_category = "High"

    rainfall = encode_value(
        encoders["Rainfall_Category"],
        rainfall_category,
        "Rainfall_Category"
    )

    # Feature Engineering
    temp_diff = data.MaxT - data.MinT

    avg_humidity = (data.RH1 + data.RH2) / 2

    week_sin = np.sin(
        2 * np.pi * data.Standard_Week / 52
    )

    week_cos = np.cos(
        2 * np.pi * data.Standard_Week / 52
    )

    weather_index = (
        data.MaxT
        + data.MinT
        + data.RH1
        + data.RH2
        + data.RF
        + data.WS
    )

    # Model input
    X = pd.DataFrame([{

        "Crop": crop,

        "Observation Year": data.Observation_Year,

        "Standard Week": data.Standard_Week,

        "Pest_Name": pest,

        "Location": location,

        "MaxT": data.MaxT,

        "MinT": data.MinT,

        "RH1(%)": data.RH1,

        "RH2(%)": data.RH2,

        "RF(mm)": data.RF,

        "WS(kmph)": data.WS,

        "SSH(hrs)": data.SSH,

        "EVP(mm)": data.EVP,

        "Temp_Diff": temp_diff,

        "Avg_Humidity": avg_humidity,

        "Week_Sin": week_sin,

        "Week_Cos": week_cos,

        "Weather_Index": weather_index,

        "Rainfall_Category": rainfall

    }])

    # Predict
    prediction = float(model.predict(X)[0])

    return {
        "predicted_pest_value": round(prediction, 2),
        "risk_level": calculate_risk(prediction),
        "status": "Prediction Successful"
    }