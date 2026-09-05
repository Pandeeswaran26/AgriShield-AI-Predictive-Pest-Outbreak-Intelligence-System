from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from sqlalchemy import inspect, text
from database.database import Base, engine, get_db
from auth.models import User, OTP
from auth.router import router as auth_router
from auth.service import decode_token, is_token_revoked, get_user_by_email
from plants.models import Plant
from plants.router import router as plants_router

from .schemas import PredictionRequest, AutoPredictionRequest
from .prediction import predict, predict_all_pests_for_crop, predict_forecast_risk
from history.models import PredictionHistory
from history.router import router as history_router
from history.service import create_prediction_history, create_auto_prediction_history
from dashboard.router import router as dashboard_router
from recommendation.router import router as recommendation_router
from recommendation.service import generate_smart_advisory
from analytics.router import router as analytics_router
from assistant.router import router as assistant_router
from report.router import router as report_router
from explain.router import router as explain_router
from weather.router import router as weather_router
from weather.service import get_weather_snapshot_by_coordinates, get_forecast_7days

Base.metadata.create_all(bind=engine)


def _ensure_db_migrations(target_engine):
    try:
        inspector = inspect(target_engine)
        if "prediction_history" in inspector.get_table_names():
            existing_cols = {col["name"] for col in inspector.get_columns("prediction_history")}
            columns_to_add = [
                ("plant_id", "INTEGER"),
                ("plant_name", "VARCHAR"),
                ("crop_variety", "VARCHAR"),
                ("growth_stage", "VARCHAR"),
                ("field_name", "VARCHAR"),
                ("field_size", "FLOAT"),
                ("soil_type", "VARCHAR"),
                ("soil_moisture", "FLOAT"),
                ("soil_ph", "FLOAT"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in columns_to_add:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE prediction_history ADD COLUMN {col_name} {col_type}"))
                conn.commit()
    except Exception as exc:
        print(f"Non-fatal migration notice: {exc}")


_ensure_db_migrations(engine)

app = FastAPI(
    title="AgriShield AI API",
    description="Predictive Pest Outbreak Intelligence System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


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


@app.get("/")
def home():
    return {
        "message": "Welcome to AgriShield AI API",
        "system": "Predictive Pest Outbreak Intelligence",
        "status": "Running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {"status": "Healthy", "service": "AgriShield AI Backend"}


@app.post("/predict")
def predict_pest(
    request: PredictionRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        result = predict(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    user_id = _get_optional_user_id(db, authorization)
    record = create_prediction_history(db, request, result, user_id=user_id)

    return {**result, "prediction_id": record.id}


@app.post("/predict/auto")
def predict_pest_auto(
    request: AutoPredictionRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Intelligent Auto-Prediction Endpoint:
    Farmer provides only Crop + GPS (lat/lon).
    Backend auto-fetches weather + 7-day forecast, ranks all known pests for this crop,
    evaluates 7-day future risk, generates Smart Advisory, and saves prediction history.
    """
    try:
        # 1. Fetch current weather snapshot & nearest training location
        snapshot = get_weather_snapshot_by_coordinates(
            request.Latitude,
            request.Longitude,
            location_label=request.location_name,
        )
        location_meta = snapshot.get("location", {})
        location_name = location_meta.get("name") or request.location_name or f"{request.Latitude:.2f}°N, {request.Longitude:.2f}°E"
        weather_dict = snapshot.get("weather", {})
        suggested = snapshot.get("suggested_values", {})
        weather_dict["Observation_Year"] = suggested.get("Observation_Year", 2026)
        weather_dict["Standard_Week"] = suggested.get("Standard_Week", 35)

        # 2. Fetch 7-day forecast
        forecast_data = get_forecast_7days(
            request.Latitude,
            request.Longitude,
            location_label=location_name,
        )
        forecast_days = forecast_data.get("days", [])
        matched_training_location = forecast_data.get("location", {}).get("matched_training_location") or location_name

        # 3. Evaluate multi-pest risk ranking for the chosen crop
        pests_ranked = predict_all_pests_for_crop(request.Crop, weather_dict, matched_training_location)
        if not pests_ranked:
            raise HTTPException(status_code=400, detail="Unable to generate pest predictions for this crop.")

        top_pest = pests_ranked[0]

        # 4. Predict 7-day risk timeline
        forecast_risk = predict_forecast_risk(request.Crop, forecast_days, matched_training_location)

        # 5. Generate comprehensive Smart Advisory
        smart_advisory = generate_smart_advisory(
            crop=request.Crop,
            top_pest=top_pest["pest_name"],
            risk_level=top_pest["risk_level"],
            pests_ranked=pests_ranked,
            weather_dict=weather_dict,
        )

        # 6. Save to history with rich plant context
        user_id = _get_optional_user_id(db, authorization)
        record = create_auto_prediction_history(
            db=db,
            crop=request.Crop,
            location_name=matched_training_location,
            location_display=location_name,
            latitude=request.Latitude,
            longitude=request.Longitude,
            weather_dict=weather_dict,
            top_pest_result=top_pest,
            pests_ranked=pests_ranked,
            forecast_risk=forecast_risk,
            advisory=smart_advisory,
            user_id=user_id,
            plant_id=request.plant_id,
            plant_name=request.plant_name,
            crop_variety=request.crop_variety,
            growth_stage=request.growth_stage,
            field_name=request.field_name,
            field_size=request.field_size,
            soil_type=request.soil_type,
            soil_moisture=request.soil_moisture,
            soil_ph=request.soil_ph,
        )

        # 7. Evaluate Contributing Environmental Factors
        rh1_val = weather_dict.get("RH1") or 70.0
        rf_val = weather_dict.get("RF") or 0.0
        max_t = weather_dict.get("MaxT") or 32.0
        min_t = weather_dict.get("MinT") or 24.0
        temp_swing = round(max_t - min_t, 1)

        contributing_factors = [
            {
                "factor": "Diurnal Temp Differential",
                "value": f"{temp_swing}°C ({min_t}°C - {max_t}°C)",
                "impact": "Thermal oscillation accelerates nymph incubation and canopy egg-laying.",
                "status": "High" if temp_swing > 9.0 else "Normal",
            },
            {
                "factor": "Morning Relative Humidity",
                "value": f"{rh1_val}%",
                "impact": "High microclimate moisture sustains foliar fungal pathogens and soft-bodied sucking pests.",
                "status": "High" if rh1_val > 75.0 else "Moderate",
            },
            {
                "factor": "Precipitation Accumulation",
                "value": f"{rf_val} mm",
                "impact": "Standing water in furrows increases root rot susceptibility and stem borer activity." if rf_val > 5.0 else "Dry conditions favor aphid and mite proliferation.",
                "status": "Warning" if rf_val > 25.0 else "Normal",
            },
            {
                "factor": "Soil Environment",
                "value": f"{request.soil_type or 'Loam'} (pH {request.soil_ph or 6.5}, {request.soil_moisture or 60}% moisture)",
                "impact": "Soil moisture balance directly influences plant turgor and systemic chemical uptake.",
                "status": "Optimal" if (5.5 <= (request.soil_ph or 6.5) <= 7.5) else "Stressed",
            },
        ]

        from datetime import datetime, timezone

        return {
            "prediction_id": record.id,
            "crop": request.Crop,
            "plant": {
                "id": request.plant_id,
                "name": request.plant_name or f"{request.Crop} Plant",
                "crop_type": request.Crop,
                "variety": request.crop_variety or "Standard",
                "growth_stage": request.growth_stage or "Vegetative",
                "field_name": request.field_name or "Primary Field",
                "field_size": request.field_size or 1.0,
                "field_size_unit": request.field_size_unit or "acres",
                "soil_type": request.soil_type or "Loam",
                "soil_moisture": request.soil_moisture or 60.0,
                "soil_ph": request.soil_ph or 6.5,
            },
            "location": {
                "display_name": location_name,
                "matched_training_location": matched_training_location,
                "latitude": request.Latitude,
                "longitude": request.Longitude,
            },
            "current_weather": weather_dict,
            "top_pest": top_pest,
            "pests_ranked": pests_ranked,
            "forecast_risk": forecast_risk,
            "smart_advisory": smart_advisory,
            "contributing_factors": contributing_factors,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "Prediction Successful",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


app.include_router(plants_router)
app.include_router(history_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(recommendation_router)
app.include_router(assistant_router)
app.include_router(report_router)
app.include_router(explain_router)
app.include_router(weather_router)