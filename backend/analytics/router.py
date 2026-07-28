from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from .service import (
    prediction_trends,
    crop_analysis,
    weather_impact,
    location_analysis,
    risk_distribution,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/prediction-trends")
def get_prediction_trends(db: Session = Depends(get_db)):
    return prediction_trends(db)


@router.get("/crop-analysis")
def get_crop_analysis(db: Session = Depends(get_db)):
    return crop_analysis(db)


@router.get("/weather-impact")
def get_weather_impact(db: Session = Depends(get_db)):
    return weather_impact(db)


@router.get("/location-analysis")
def get_location_analysis(db: Session = Depends(get_db)):
    return location_analysis(db)


@router.get("/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    return risk_distribution(db)