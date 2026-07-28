from datetime import date
from sqlalchemy.orm import Session

from history.models import PredictionHistory


def get_dashboard_summary(db: Session):

    predictions = db.query(PredictionHistory).all()

    total = len(predictions)

    high = sum(1 for p in predictions if p.risk_level == "High")
    medium = sum(1 for p in predictions if p.risk_level == "Medium")
    low = sum(1 for p in predictions if p.risk_level == "Low")

    today = sum(
        1
        for p in predictions
        if p.prediction_date.date() == date.today()
    )

    return {
        "totalPredictions": total,
        "highRisk": high,
        "mediumRisk": medium,
        "lowRisk": low,
        "todayPredictions": today,
    }


def pest_trend(db: Session):
    return [
        {"week": "W20", "value": 2.1},
        {"week": "W21", "value": 2.8},
        {"week": "W22", "value": 3.0},
    ]


def weather_trend(db: Session):
    return [
        {"week": "W20", "maxTemp": 33.2, "rainfall": 5.1},
        {"week": "W21", "maxTemp": 34.1, "rainfall": 8.3},
    ]


def monthly_predictions(db: Session):
    return [
        {"month": "Jan", "count": 12},
        {"month": "Feb", "count": 18},
        {"month": "Mar", "count": 25},
    ]


def crop_analysis(db: Session):
    return [
        {"crop": "Cotton", "value": 120},
        {"crop": "Rice", "value": 94},
    ]