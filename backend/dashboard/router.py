from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db

from .service import (
    get_dashboard_summary,
    pest_trend,
    weather_trend,
    monthly_predictions,
    crop_analysis,
    get_latest_prediction_card,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)


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