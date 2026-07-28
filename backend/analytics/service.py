from sqlalchemy.orm import Session
from history.models import PredictionHistory


def prediction_trends(db: Session):
    return [
        {"label": "Week 20", "riskScore": 45},
        {"label": "Week 21", "riskScore": 61},
        {"label": "Week 22", "riskScore": 74},
    ]


def crop_analysis(db: Session):
    return [
        {"crop": "Cotton", "avgRisk": 58},
        {"crop": "Rice", "avgRisk": 34},
        {"crop": "Maize", "avgRisk": 49},
    ]


def weather_impact(db: Session):
    return [
        {"factor": "Humidity", "impact": 82},
        {"factor": "Rainfall", "impact": 65},
        {"factor": "Temperature", "impact": 47},
        {"factor": "Wind Speed", "impact": 29},
    ]


def location_analysis(db: Session):
    return [
        {"location": "Coimbatore", "count": 38},
        {"location": "Madurai", "count": 21},
        {"location": "Theni", "count": 17},
    ]


def risk_distribution(db: Session):
    predictions = db.query(PredictionHistory).all()

    low = sum(1 for p in predictions if p.risk_level == "Low")
    medium = sum(1 for p in predictions if p.risk_level == "Medium")
    high = sum(1 for p in predictions if p.risk_level == "High")

    return [
        {"level": "Low", "value": low},
        {"level": "Medium", "value": medium},
        {"level": "High", "value": high},
    ]