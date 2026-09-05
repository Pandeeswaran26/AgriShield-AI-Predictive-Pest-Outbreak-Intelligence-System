import json
from typing import Optional
from sqlalchemy.orm import Session

from .models import PredictionHistory


def get_all_predictions(db: Session, user_id: Optional[int] = None):
    query = db.query(PredictionHistory)
    if user_id is not None:
        query = query.filter(PredictionHistory.user_id == user_id)
    return query.order_by(PredictionHistory.prediction_date.desc()).all()


def get_latest_prediction(db: Session, user_id: Optional[int] = None):
    query = db.query(PredictionHistory)
    if user_id is not None:
        query = query.filter(PredictionHistory.user_id == user_id)
    return query.order_by(PredictionHistory.prediction_date.desc()).first()


def delete_prediction(db: Session, prediction_id: int, user_id: Optional[int] = None):
    query = db.query(PredictionHistory).filter(PredictionHistory.id == prediction_id)
    if user_id is not None:
        query = query.filter(PredictionHistory.user_id == user_id)
    prediction = query.first()

    if prediction:
        db.delete(prediction)
        db.commit()

    return prediction


def create_prediction_history(
    db: Session, request, result: dict, user_id: Optional[int] = None
) -> PredictionHistory:
    record = PredictionHistory(
        user_id=user_id,
        crop=request.Crop,
        pest_name=request.Pest_Name,
        location=request.Location,
        risk_level=result["risk_level"],
        pest_value=result["predicted_pest_value"],
        observation_year=request.Observation_Year,
        standard_week=request.Standard_Week,
        max_t=request.MaxT,
        min_t=request.MinT,
        rh1=request.RH1,
        rh2=request.RH2,
        rf=request.RF,
        ws=request.WS,
        ssh=request.SSH,
        evp=request.EVP,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def create_auto_prediction_history(
    db: Session,
    crop: str,
    location_name: str,
    location_display: str,
    latitude: float,
    longitude: float,
    weather_dict: dict,
    top_pest_result: dict,
    pests_ranked: list[dict],
    forecast_risk: list[dict],
    advisory: dict,
    user_id: Optional[int] = None,
    plant_id: Optional[int] = None,
    plant_name: Optional[str] = None,
    crop_variety: Optional[str] = None,
    growth_stage: Optional[str] = None,
    field_name: Optional[str] = None,
    field_size: Optional[float] = None,
    soil_type: Optional[str] = None,
    soil_moisture: Optional[float] = None,
    soil_ph: Optional[float] = None,
) -> PredictionHistory:
    record = PredictionHistory(
        user_id=user_id,
        crop=crop,
        pest_name=top_pest_result["pest_name"],
        location=location_name,
        location_display=location_display,
        risk_level=top_pest_result["risk_level"],
        pest_value=top_pest_result["pest_value"],
        confidence=top_pest_result.get("confidence"),
        latitude=latitude,
        longitude=longitude,
        auto_mode=True,
        plant_id=plant_id,
        plant_name=plant_name,
        crop_variety=crop_variety,
        growth_stage=growth_stage,
        field_name=field_name,
        field_size=field_size,
        soil_type=soil_type,
        soil_moisture=soil_moisture,
        soil_ph=soil_ph,
        pests_json=json.dumps(pests_ranked),
        forecast_json=json.dumps(forecast_risk),
        advisory_json=json.dumps(advisory),
        observation_year=weather_dict.get("Observation_Year"),
        standard_week=weather_dict.get("Standard_Week"),
        max_t=weather_dict.get("MaxT"),
        min_t=weather_dict.get("MinT"),
        rh1=weather_dict.get("RH1"),
        rh2=weather_dict.get("RH2"),
        rf=weather_dict.get("RF"),
        ws=weather_dict.get("WS"),
        ssh=weather_dict.get("SSH"),
        evp=weather_dict.get("EVP"),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record