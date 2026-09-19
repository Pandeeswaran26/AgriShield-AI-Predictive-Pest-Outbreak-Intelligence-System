from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from database.database import get_db
from auth.service import decode_token, is_token_revoked, get_user_by_email

from .service import (
    get_dashboard_summary,
    pest_trend,
    weather_trend,
    monthly_predictions,
    crop_analysis,
    get_latest_prediction_card,
    get_farmer_fields_overview,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def _get_optional_user_id(db: Session, authorization: Optional[str] = None) -> Optional[int]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    if not token or is_token_revoked(db, token):
        return None
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email:
            user = get_user_by_email(db, email)
            return user.id if user else None
    except Exception:
        return None
    return None


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)


@router.get("/fields")
def get_fields(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    user_id = _get_optional_user_id(db, authorization)
    return get_farmer_fields_overview(db, user_id)


@router.get("/latest")
def latest_prediction(db: Session = Depends(get_db)):
    return get_latest_prediction_card(db)


@router.get("/pest-trend")
def get_pest_trend(db: Session = Depends(get_db)):
    return pest_trend(db)


@router.get("/weather-trend")
def get_weather_trend(db: Session = Depends(get_db)):
    return weather_trend(db)


@router.get("/monthly-predictions")
def get_monthly_predictions(db: Session = Depends(get_db)):
    return monthly_predictions(db)


@router.get("/crop-analysis")
def get_crop_analysis(db: Session = Depends(get_db)):
    return crop_analysis(db)