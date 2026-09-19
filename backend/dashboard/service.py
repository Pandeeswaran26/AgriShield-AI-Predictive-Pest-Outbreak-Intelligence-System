from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from history.models import PredictionHistory


def get_dashboard_summary(db: Session):
    total = (
        db.query(func.count(PredictionHistory.id))
        .scalar()
        or 0
    )

    high = (
        db.query(func.count(PredictionHistory.id))
        .filter(PredictionHistory.risk_level == "High")
        .scalar()
        or 0
    )

    medium = (
        db.query(func.count(PredictionHistory.id))
        .filter(PredictionHistory.risk_level == "Medium")
        .scalar()
        or 0
    )

    low = (
        db.query(func.count(PredictionHistory.id))
        .filter(PredictionHistory.risk_level == "Low")
        .scalar()
        or 0
    )

    today_start = datetime.combine(date.today(), datetime.min.time())
    tomorrow_start = today_start + timedelta(days=1)

    today = (
        db.query(func.count(PredictionHistory.id))
        .filter(
            PredictionHistory.prediction_date >= today_start,
            PredictionHistory.prediction_date < tomorrow_start,
        )
        .scalar()
        or 0
    )

    return {
        "totalPredictions": total,
        "highRisk": high,
        "mediumRisk": medium,
        "lowRisk": low,
        "todayPredictions": today,
    }


def pest_trend(db: Session):
    rows = (
        db.query(
            PredictionHistory.pest_name,
            func.count(PredictionHistory.id).label("value"),
        )
        .group_by(PredictionHistory.pest_name)
        .order_by(func.count(PredictionHistory.id).desc())
        .all()
    )

    return [
        {
            "pest": row.pest_name or "Unknown",
            "value": int(row.value),
        }
        for row in rows
    ]


def monthly_predictions(db: Session):
    # Fetch all records to do robust month grouping across SQLite and PostgreSQL
    records = db.query(PredictionHistory.prediction_date).all()
    month_counts = defaultdict(int)

    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    for (p_date,) in records:
        if p_date:
            if isinstance(p_date, str):
                try:
                    p_date = datetime.fromisoformat(p_date.replace("Z", "+00:00"))
                except Exception:
                    continue
            month_idx = p_date.month - 1
            month_counts[month_idx] += 1

    if month_counts:
        return [
            {
                "month": month_names[m_idx],
                "count": month_counts[m_idx],
            }
            for m_idx in sorted(month_counts.keys())
        ]

    return []


def crop_analysis(db: Session):
    rows = (
        db.query(
            PredictionHistory.crop,
            func.count(PredictionHistory.id).label("value"),
        )
        .group_by(PredictionHistory.crop)
        .order_by(func.count(PredictionHistory.id).desc())
        .all()
    )

    return [
        {
            "crop": row.crop or "Unknown",
            "value": int(row.value),
        }
        for row in rows
    ]


def weather_trend(db: Session):
    """
    Returns rolling environmental trends (Avg Temperature, Humidity, Rainfall)
    from historical predictions.
    """
    rows = (
        db.query(
            PredictionHistory.standard_week.label("week"),
            func.avg(PredictionHistory.max_t).label("avg_temp"),
            func.avg(PredictionHistory.rh1).label("avg_humidity"),
            func.avg(PredictionHistory.rf).label("avg_rain"),
            func.count(PredictionHistory.id).label("count"),
        )
        .filter(PredictionHistory.standard_week.isnot(None))
        .group_by(PredictionHistory.standard_week)
        .order_by(PredictionHistory.standard_week.asc())
        .limit(10)
        .all()
    )

    if rows:
        return [
            {
                "week": f"Wk {int(row.week)}",
                "maxTemp": round(float(row.avg_temp or 0), 1),
                "humidity": round(float(row.avg_humidity or 0), 1),
                "rainfall": round(float(row.avg_rain or 0), 1),
            }
            for row in rows
        ]

    return []


def get_latest_prediction_card(db: Session):
    latest = (
        db.query(PredictionHistory)
        .order_by(PredictionHistory.prediction_date.desc())
        .first()
    )

    if not latest:
        return None

    import json
    pests_data = []
    if latest.pests_json:
        try:
            pests_data = json.loads(latest.pests_json)
        except Exception:
            pests_data = []

    forecast_data = []
    if latest.forecast_json:
        try:
            forecast_data = json.loads(latest.forecast_json)
        except Exception:
            forecast_data = []

    return {
        "id": latest.id,
        "crop": latest.crop,
        "pest_name": latest.pest_name,
        "risk_level": latest.risk_level,
        "pest_value": latest.pest_value,
        "confidence": latest.confidence,
        "location": latest.location,
        "location_display": latest.location_display or latest.location,
        "latitude": latest.latitude,
        "longitude": latest.longitude,
        "prediction_date": latest.prediction_date.isoformat() if latest.prediction_date else None,
        "pests_ranked": pests_data,
        "forecast_risk": forecast_data,
        "weather": {
            "max_t": latest.max_t,
            "min_t": latest.min_t,
            "rh1": latest.rh1,
            "rf": latest.rf,
            "ws": latest.ws,
        },
    }


def get_farmer_fields_overview(db: Session, user_id: int | None = None):
    """
    Returns an operational overview of the farmer's actual registered fields,
    complete with dynamic DAP, growth stages, last assessment health, risk level,
    and next prioritized action.
    """
    from plants.models import Plant
    from plants.service import get_user_plants
    from diagnosis.models import PlantDiagnosisRecord
    from agronomy.growth_stage import calculate_growth_stage

    if user_id:
        plants = get_user_plants(db, user_id)
    else:
        plants = db.query(Plant).order_by(Plant.updated_at.desc()).limit(10).all()

    fields_overview = []
    for plant in plants:
        # Calculate growth stage
        stage_info = calculate_growth_stage(plant.planting_date, plant.crop_type)

        # Check latest prediction record
        latest_pred = (
            db.query(PredictionHistory)
            .filter(PredictionHistory.plant_id == plant.id)
            .order_by(PredictionHistory.prediction_date.desc())
            .first()
        )
        if not latest_pred:
            # Fallback to crop match if plant_id wasn't set on legacy rows
            latest_pred = (
                db.query(PredictionHistory)
                .filter(PredictionHistory.crop.ilike(f"%{plant.crop_type}%"))
                .order_by(PredictionHistory.prediction_date.desc())
                .first()
            )

        # Check latest plant leaf diagnosis
        latest_diag = (
            db.query(PlantDiagnosisRecord)
            .filter(PlantDiagnosisRecord.crop_name.ilike(f"%{plant.crop_type}%"))
            .order_by(PlantDiagnosisRecord.created_at.desc())
            .first()
        )

        health_status = plant.last_health_status or (latest_pred.health_status if latest_pred else "Healthy")
        risk_level = plant.last_risk_level or (latest_pred.risk_level if latest_pred else "Low")
        next_action = plant.last_recommended_action or "Routine crop surveillance and moisture monitoring."

        fields_overview.append({
            "id": plant.id,
            "name": plant.name,
            "crop_type": plant.crop_type,
            "variety": plant.variety or "Standard",
            "field_name": plant.field_name or "Primary Field",
            "field_size": plant.field_size or 2.0,
            "field_size_unit": plant.field_size_unit or "acres",
            "planting_date": plant.planting_date,
            "days_after_planting": stage_info.get("days_after_planting", 30),
            "growth_stage": plant.growth_stage or stage_info.get("growth_stage", "Vegetative"),
            "growth_stage_details": stage_info,
            "water_demand": stage_info.get("water_demand", "Medium"),
            "irrigation_method": getattr(plant, "irrigation_method", "Furrow / Basin"),
            "soil_type": plant.soil_type or "Clay Loam",
            "soil_moisture": plant.soil_moisture or 60.0,
            "soil_ph": plant.soil_ph or 6.5,
            "latitude": plant.latitude or 11.0168,
            "longitude": plant.longitude or 76.9558,
            "location_name": plant.location_name or "Field Station",
            "health_status": health_status,
            "risk_level": risk_level,
            "next_action": next_action,
            "last_assessment_date": plant.last_assessment_date.isoformat() if getattr(plant, "last_assessment_date", None) else (latest_pred.prediction_date.isoformat() if latest_pred and latest_pred.prediction_date else None),
            "last_diagnosis": {
                "disease_name": latest_diag.disease_name,
                "confidence": latest_diag.confidence,
                "is_healthy": latest_diag.is_healthy,
                "created_at": latest_diag.created_at.isoformat() if latest_diag.created_at else None,
            } if latest_diag else None,
        })

    return fields_overview