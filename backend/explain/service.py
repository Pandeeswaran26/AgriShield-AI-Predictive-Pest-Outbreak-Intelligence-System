from types import SimpleNamespace
from typing import Dict, Any, List, Optional
import shap
from sqlalchemy.orm import Session

from app.model_loader import model
from app.prediction import build_features
from history.models import PredictionHistory

_explainer = None


def get_explainer():
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(model)
    return _explainer


FEATURE_DESCRIPTIONS = {
    "RH1(%)": "Morning Relative Humidity",
    "RH2(%)": "Afternoon Relative Humidity",
    "Avg_Humidity": "Mean Atmospheric Humidity",
    "MaxT": "Daytime Maximum Temperature",
    "MinT": "Nighttime Minimum Temperature",
    "Temp_Diff": "Diurnal Thermal Oscillation",
    "RF(mm)": "Precipitation Accumulation",
    "Rainfall_Category": "Rainfall Intensity Band",
    "WS(kmph)": "Wind Speed Velocity",
    "SSH(hrs)": "Sunshine Duration",
    "EVP(mm)": "Pan Evaporation",
    "Weather_Index": "Composite Meteorological Index",
    "Standard Week": "Calendar Seasonal Period",
    "Crop": "Host Crop Susceptibility",
    "Location": "Geographic Endemicity",
    "Pest_Name": "Pest Species Profile",
}


def _generate_agronomic_reason(feature: str, impact: float, value: Any) -> str:
    """
    Constructs grounded, non-fabricated agronomic explanations based on actual
    SHAP directional impact and input parameter value.
    """
    feature_clean = FEATURE_DESCRIPTIONS.get(feature, feature)
    if impact > 0:
        if "Humidity" in feature_clean:
            return f"{feature_clean} ({value}%) creates favorable microclimate moisture accelerating pest incubation."
        elif "Temperature" in feature_clean:
            return f"{feature_clean} ({value}°C) falls within the optimal thermal window for insect reproduction."
        elif "Thermal" in feature_clean or "Temp_Diff" in feature:
            return f"{feature_clean} ({value}°C) stimulates night-time feeding and morning activity."
        elif "Precipitation" in feature_clean or "Rainfall" in feature_clean:
            return f"{feature_clean} ({value} mm) increases leaf turgor and succulent shoot growth favored by pests."
        elif "Wind" in feature_clean:
            return f"{feature_clean} ({value} km/h) aids localized migration and dispersal of flying adults."
        else:
            return f"{feature_clean} contributed positively (+{impact:.2f}) to pest pressure."
    else:
        if "Wind" in feature_clean:
            return f"{feature_clean} ({value} km/h) disrupts insect flight, canopy settling, and oviposition."
        elif "Humidity" in feature_clean:
            return f"{feature_clean} ({value}%) is outside the pest's peak reproduction threshold, suppressing activity."
        elif "Temperature" in feature_clean:
            return f"{feature_clean} ({value}°C) is unfavorable for accelerated nymph maturation."
        elif "Precipitation" in feature_clean or "Rainfall" in feature_clean:
            return f"{feature_clean} ({value} mm) suppresses ground emergence or washes down small instars."
        else:
            return f"{feature_clean} suppressed (-{abs(impact):.2f}) pest outbreak pressure."


def explain_prediction(db: Session, prediction_id: int) -> Optional[Dict[str, Any]]:
    record = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.id == prediction_id)
        .first()
    )

    if not record:
        return None

    data = SimpleNamespace(
        Crop=record.crop,
        Pest_Name=record.pest_name,
        Location=record.location,
        Observation_Year=record.observation_year,
        Standard_Week=record.standard_week,
        MaxT=record.max_t,
        MinT=record.min_t,
        RH1=record.rh1,
        RH2=record.rh2,
        RF=record.rf,
        WS=record.ws,
        SSH=record.ssh,
        EVP=record.evp,
    )

    X = build_features(data)

    explainer_instance = get_explainer()
    shap_values = explainer_instance.shap_values(X)
    values = shap_values[0] if isinstance(shap_values, list) else shap_values

    feature_importance: List[Dict[str, Any]] = []
    positive_contributors: List[Dict[str, Any]] = []
    negative_contributors: List[Dict[str, Any]] = []

    for feature, raw_impact in zip(X.columns, values[0]):
        impact = float(raw_impact)
        raw_val = X[feature].iloc[0] if feature in X.columns else None

        item = {
            "feature": feature,
            "display_name": FEATURE_DESCRIPTIONS.get(feature, feature),
            "feature_value": float(raw_val) if isinstance(raw_val, (int, float, np.number)) else str(raw_val),
            "impact": round(impact, 4),
            "direction": "INCREASED_RISK" if impact > 0 else "DECREASED_RISK",
            "reason": _generate_agronomic_reason(feature, impact, raw_val),
        }

        feature_importance.append(item)
        if impact > 0:
            positive_contributors.append(item)
        elif impact < 0:
            negative_contributors.append(item)

    # Sort each list by absolute contribution strength
    feature_importance.sort(key=lambda x: abs(x["impact"]), reverse=True)
    positive_contributors.sort(key=lambda x: x["impact"], reverse=True)
    negative_contributors.sort(key=lambda x: x["impact"])

    # Base value and expected value
    base_val = float(explainer_instance.expected_value) if hasattr(explainer_instance, "expected_value") else 0.0

    return {
        "prediction_id": prediction_id,
        "base_value": round(base_val, 3),
        "feature_importance": feature_importance,
        "positive_contributors": positive_contributors[:5],
        "negative_contributors": negative_contributors[:5],
        "summary": {
            "primary_driver": positive_contributors[0]["display_name"] if positive_contributors else "Baseline Endemicity",
            "primary_mitigator": negative_contributors[0]["display_name"] if negative_contributors else "None",
            "net_shap_impact": round(sum(item["impact"] for item in feature_importance), 3),
        }
    }