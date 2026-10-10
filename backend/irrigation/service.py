"""
Irrigation AI Service
AgriShield Platform
====================
Loads the trained RandomForestClassifier and provides:
  predict_irrigation(crop_name, crop_days, soil_moisture, soil_temperature,
                     temperature, humidity, rainfall) -> IrrigationResult
"""
import json
import pickle
from pathlib import Path
from typing import Optional, List

import numpy as np

# ─── Model paths ─────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent.parent
_MODEL_PATH    = _ROOT / "ml" / "models" / "irrigation_model.pkl"
_ENCODERS_PATH = _ROOT / "ml" / "models" / "irrigation_label_encoders.pkl"
_META_PATH     = _ROOT / "ml" / "models" / "irrigation_metadata.json"

_model     = None
_encoders  = None
_meta      = None


def _load():
    global _model, _encoders, _meta
    if _model is None:
        with open(_MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(_ENCODERS_PATH, "rb") as f:
            _encoders = pickle.load(f)
        with open(_META_PATH) as f:
            _meta = json.load(f)


# ─── Crop-specific irrigation thresholds (% VWC) ──────────────────────
_CROP_THRESHOLDS = {
    "Rice":      {"critical": 15.0, "optimal": 30.0, "max": 42.0},
    "Wheat":     {"critical": 18.0, "optimal": 28.0, "max": 38.0},
    "Cotton":    {"critical": 16.0, "optimal": 26.0, "max": 36.0},
    "Maize":     {"critical": 17.0, "optimal": 27.0, "max": 38.0},
    "Soybean":   {"critical": 18.0, "optimal": 28.0, "max": 38.0},
    "Groundnut": {"critical": 14.0, "optimal": 24.0, "max": 34.0},
    "Sugarcane": {"critical": 17.0, "optimal": 28.0, "max": 40.0},
    "Tomato":    {"critical": 20.0, "optimal": 30.0, "max": 40.0},
    "Potato":    {"critical": 22.0, "optimal": 32.0, "max": 42.0},
}

_DEFAULT_THRESHOLD = {"critical": 17.0, "optimal": 27.0, "max": 38.0}

# ─── Irrigation method recommendations ────────────────────────────────
_IRRIGATION_METHODS = {
    "Rice":      "Basin / Flood Irrigation",
    "Wheat":     "Furrow / Sprinkler",
    "Cotton":    "Drip Irrigation",
    "Maize":     "Furrow / Sprinkler",
    "Soybean":   "Sprinkler / Drip",
    "Groundnut": "Drip / Furrow",
    "Sugarcane": "Drip / Furrow",
    "Tomato":    "Drip Irrigation",
    "Potato":    "Drip / Sprinkler",
}

# ─── Water quantity guides (litre/plant or litre/m²) ──────────────────
_WATER_GUIDE = {
    "Rice":      {"low": "30–40 mm depth", "medium": "40–60 mm depth", "high": "60–80 mm depth"},
    "Wheat":     {"low": "25–35 mm",       "medium": "35–50 mm",       "high": "50–65 mm"},
    "Cotton":    {"low": "3–4 L/plant",    "medium": "4–6 L/plant",    "high": "6–8 L/plant"},
    "Maize":     {"low": "25–35 mm",       "medium": "35–50 mm",       "high": "50–70 mm"},
    "Soybean":   {"low": "20–30 mm",       "medium": "30–45 mm",       "high": "45–60 mm"},
    "Groundnut": {"low": "20–30 mm",       "medium": "30–45 mm",       "high": "45–60 mm"},
    "Sugarcane": {"low": "35–50 mm",       "medium": "50–70 mm",       "high": "70–90 mm"},
    "Tomato":    {"low": "2–3 L/plant",    "medium": "3–5 L/plant",    "high": "5–7 L/plant"},
    "Potato":    {"low": "20–30 mm",       "medium": "30–45 mm",       "high": "45–60 mm"},
}


def _risk_category(probability: float) -> str:
    if probability >= 0.70:
        return "High"
    elif probability >= 0.40:
        return "Medium"
    return "Low"


def _water_stress_level(soil_moisture: float, crop_name: str) -> str:
    thresh = _CROP_THRESHOLDS.get(crop_name, _DEFAULT_THRESHOLD)
    if soil_moisture < thresh["critical"]:
        return "Severe"
    elif soil_moisture < thresh["optimal"]:
        return "Moderate"
    elif soil_moisture > thresh["max"]:
        return "Waterlogged"
    return "Optimal"


from .email_service import send_irrigation_alert_email


def predict_irrigation(
    crop_name: str,
    crop_days: float,
    soil_moisture: float,
    soil_temperature: float,
    temperature: float,
    humidity: float,
    rainfall: float,
    plant_name: Optional[str] = None,
    field_position: Optional[str] = None,
    irrigation_frequency: Optional[str] = None,
    irrigation_hours: Optional[float] = None,
    to_email: Optional[str] = None,
    farmer_name: Optional[str] = None,
    send_email: bool = False,
) -> dict:
    """
    Returns a structured irrigation prediction dict with:
      irrigation_needed (bool), probability, risk, water_stress,
      recommended_method, water_quantity, advisory, field_position,
      irrigation_frequency (times needed), irrigation_hours (hours needed),
      and optional automatic email alert dispatch.
    """
    _load()

    le_crop = _encoders["crop"]
    supported = le_crop.classes_.tolist()

    # Normalise crop name
    crop_clean = crop_name.strip().title()
    if crop_clean not in supported:
        # Fuzzy fallback to closest
        import difflib
        matches = difflib.get_close_matches(crop_clean, supported, n=1)
        crop_clean = matches[0] if matches else "Rice"

    crop_encoded    = le_crop.transform([crop_clean])[0]
    heat_index      = temperature * humidity / 100.0
    evap_potential  = round(temperature - soil_moisture * 0.1, 2)
    moisture_deficit = max(0.0, 25.0 - soil_moisture)

    X = np.array([[
        crop_encoded, crop_days, soil_moisture, soil_temperature,
        temperature, humidity, rainfall,
        heat_index, evap_potential, moisture_deficit,
    ]])

    proba        = float(_model.predict_proba(X)[0][1])
    pred_label   = int(_model.predict(X)[0])
    risk         = _risk_category(proba)
    water_stress = _water_stress_level(soil_moisture, crop_clean)

    # Override: if rainfall is high (>15mm) and soil is wet -> no irrigation
    if rainfall > 15.0 and soil_moisture > 30.0:
        pred_label = 0
        proba = min(proba, 0.25)
        risk = "Low"

    # Water quantity guide
    wg = _WATER_GUIDE.get(crop_clean, _WATER_GUIDE["Rice"])
    if risk == "High":
        qty = wg["high"]
    elif risk == "Medium":
        qty = wg["medium"]
    else:
        qty = wg["low"]

    # Advisory notes
    advisory_lines = []
    thresh = _CROP_THRESHOLDS.get(crop_clean, _DEFAULT_THRESHOLD)
    if soil_moisture < thresh["critical"]:
        advisory_lines.append(
            f"Critical moisture deficit! Soil moisture ({soil_moisture:.1f}% VWC) is below critical threshold ({thresh['critical']}%). Irrigate immediately."
        )
    elif soil_moisture > thresh["max"]:
        advisory_lines.append(
            f"Soil is saturated ({soil_moisture:.1f}% VWC > {thresh['max']}%). Do not irrigate. Improve field drainage."
        )
    elif pred_label == 1:
        advisory_lines.append(
            f"Soil moisture ({soil_moisture:.1f}% VWC) is below optimal ({thresh['optimal']}%). Irrigation recommended."
        )
    else:
        advisory_lines.append(
            f"Soil moisture ({soil_moisture:.1f}% VWC) is within optimal range ({thresh['optimal']}%). No irrigation needed."
        )

    if rainfall > 5.0:
        advisory_lines.append(f"Recent/forecast rainfall ({rainfall:.1f} mm) reduces irrigation requirement.")
    if temperature > 35.0:
        advisory_lines.append("High temperature detected — irrigate in early morning (6–9 AM) to reduce evaporation loss.")
    timing_advice = "Irrigate in early morning (6 AM – 9 AM) or late evening (5 PM – 7 PM) to minimise evaporation."
    if temperature > 38.0:
        timing_advice = "CRITICAL: Temperatures extremely high. Irrigate only at night or before sunrise."
    elif rainfall > 10.0:
        timing_advice = "Rain recently observed — wait 24–48 hours before next irrigation cycle."

    # Compute smart frequency if not specified
    if not irrigation_frequency:
        if risk == "High" or soil_moisture < thresh["critical"]:
            calc_freq = "2 times daily (Morning & Late Evening)"
        elif risk == "Medium" or pred_label == 1:
            calc_freq = "Once daily"
        else:
            calc_freq = "2–3 times per week"
    else:
        calc_freq = irrigation_frequency

    # Compute runtime hours if not specified
    if irrigation_hours is None or irrigation_hours <= 0:
        if soil_moisture < thresh["critical"]:
            calc_hours = 3.0
        elif risk == "High":
            calc_hours = 2.5
        elif pred_label == 1:
            calc_hours = 2.0
        else:
            calc_hours = 1.0
    else:
        calc_hours = round(float(irrigation_hours), 1)

    target_plant_name = plant_name or f"{crop_clean} Plant"
    target_pos = field_position or "Primary Field Zone"

    email_status = None
    if bool(pred_label == 1) and send_email and to_email:
        email_status = send_irrigation_alert_email(
            to_email=to_email,
            farmer_name=farmer_name or "Farmer",
            plant_name=target_plant_name,
            crop_type=crop_clean,
            field_position=target_pos,
            irrigation_frequency=calc_freq,
            irrigation_hours=calc_hours,
            soil_moisture=soil_moisture,
            water_quantity=qty,
            timing_advice=timing_advice,
            advisories=advisory_lines,
        )

    return {
        "crop":                 crop_clean,
        "plant_name":           target_plant_name,
        "field_position":       target_pos,
        "irrigation_frequency": calc_freq,
        "irrigation_hours":     calc_hours,
        "irrigation_needed":    bool(pred_label == 1),
        "probability":          round(proba, 4),
        "risk_level":           risk,
        "water_stress":         water_stress,
        "recommended_method":   _IRRIGATION_METHODS.get(crop_clean, "Standard Furrow / Basin"),
        "water_quantity":       qty,
        "advisory":             advisory_lines,
        "timing_advice":        timing_advice,
        "email_alert":          email_status,
        "input_summary": {
            "soil_moisture":    round(soil_moisture, 2),
            "soil_temperature": round(soil_temperature, 1),
            "temperature":      round(temperature, 1),
            "humidity":         round(humidity, 1),
            "rainfall":         round(rainfall, 1),
            "crop_days":        int(crop_days),
        },
        "thresholds": thresh,
        "supported_crops": supported,
    }


def get_supported_crops() -> list[str]:
    """Returns list of crops supported by the irrigation model."""
    _load()
    return _encoders["crop"].classes_.tolist()


def get_model_metadata() -> dict:
    """Returns model metadata/metrics."""
    _load()
    return _meta or {}
