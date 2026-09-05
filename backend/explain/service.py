from types import SimpleNamespace

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


def explain_prediction(db: Session, prediction_id: int):
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

    feature_importance = [
        {"feature": feature, "impact": float(value)}
        for feature, value in zip(X.columns, values[0])
    ]

    feature_importance.sort(key=lambda x: abs(x["impact"]), reverse=True)

    return feature_importance