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
from history.models import PredictionHistory, FarmerAction, FollowUpOutcome, ModelVersionRecord
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
from diagnosis.models import PlantDiagnosisRecord
from diagnosis.router import router as diagnosis_router
from irrigation.router import router as irrigation_router
from irrigation.history_router import router as irrigation_history_router
from irrigation.history_models import IrrigationHistory
from irrigation.scheduler import create_irrigation_scheduler

# Create all tables (including IrrigationHistory)
Base.metadata.create_all(bind=engine)


from agronomy.growth_stage import calculate_growth_stage
from agronomy.decision_engine import evaluate_crop_health_and_risk
from agronomy.recommendation_engine import generate_structured_recommendations


def _ensure_db_migrations(target_engine):
    try:
        inspector = inspect(target_engine)
        # Migrate prediction_history
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
                ("diagnosis_id", "INTEGER"),
                ("health_status", "VARCHAR"),
                ("data_sources_json", "TEXT"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in columns_to_add:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE prediction_history ADD COLUMN {col_name} {col_type}"))
                conn.commit()

        # Migrate plants table
        if "plants" in inspector.get_table_names():
            existing_plant_cols = {col["name"] for col in inspector.get_columns("plants")}
            plant_cols_to_add = [
                ("irrigation_method", "VARCHAR"),
                ("soil_n", "FLOAT"),
                ("soil_p", "FLOAT"),
                ("soil_k", "FLOAT"),
                ("last_assessment_date", "DATETIME"),
                ("last_health_status", "VARCHAR"),
                ("last_risk_level", "VARCHAR"),
                ("last_recommended_action", "VARCHAR"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in plant_cols_to_add:
                    if col_name not in existing_plant_cols:
                        conn.execute(text(f"ALTER TABLE plants ADD COLUMN {col_name} {col_type}"))
                conn.commit()
        # Migrate otps table
        if "otps" in inspector.get_table_names():
            existing_otp_cols = {col["name"] for col in inspector.get_columns("otps")}
            otp_cols_to_add = [
                ("email", "VARCHAR"),
                ("phone", "VARCHAR"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in otp_cols_to_add:
                    if col_name not in existing_otp_cols:
                        conn.execute(text(f"ALTER TABLE otps ADD COLUMN {col_name} {col_type}"))
                # If old phone_number column exists, backfill phone and relax NOT NULL constraint
                if "phone_number" in existing_otp_cols:
                    try:
                        conn.execute(text("ALTER TABLE otps ALTER COLUMN phone_number DROP NOT NULL"))
                    except Exception:
                        pass
                    if "phone" in existing_otp_cols or True:
                        conn.execute(text("UPDATE otps SET phone = phone_number WHERE phone IS NULL AND phone_number IS NOT NULL"))
                conn.commit()

        # Migrate users table
        if "users" in inspector.get_table_names():
            existing_user_cols = {col["name"] for col in inspector.get_columns("users")}
            user_cols_to_add = [
                ("phone", "VARCHAR"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in user_cols_to_add:
                    if col_name not in existing_user_cols:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                if "phone_number" in existing_user_cols and "phone" in existing_user_cols:
                    conn.execute(text("UPDATE users SET phone = phone_number WHERE phone IS NULL AND phone_number IS NOT NULL"))
                conn.commit()
    except Exception as exc:
        print(f"Non-fatal migration notice: {exc}")


_ensure_db_migrations(engine)

# ─── Lifespan: start/stop APScheduler ────────────────────────────────
from contextlib import asynccontextmanager

_irrigation_scheduler = create_irrigation_scheduler()

@asynccontextmanager
async def lifespan(app):
    _irrigation_scheduler.start()
    import logging
    logging.getLogger("agrishield.irrigation.scheduler").info(
        "[IrrigationScheduler] Started — morning (6 AM) & evening (6 PM) dispatches active."
    )
    yield
    _irrigation_scheduler.shutdown(wait=False)


app = FastAPI(
    title="AgriShield AI API",
    description="Predictive Pest Outbreak Intelligence & Agricultural Decision-Support System",
    version="2.1.0",
    lifespan=lifespan,
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


import json
from datetime import datetime, timezone


@app.post("/predict/auto")
@app.post("/api/assessment/run")
def run_crop_assessment_and_prediction(
    request: AutoPredictionRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    AgriShield Integrated Crop Assessment & Decision Engine:
    Combines:
    1. Crop + Field Geolocation (GPS or selected station)
    2. Planting Date -> Dynamic DAP and crop-specific Growth Stage
    3. Live Weather & 7-Day Forecast from Open-Meteo
    4. Soil Environment & Nutrient Profile (Moisture, pH, NPK, Irrigation Method)
    5. Tabular ML Pest Outbreak Modeling
    6. Plant Leaf Vision Pathology (attached diagnosis record if provided)
    7. AgriShield Decision Engine -> Multi-domain Health & Risk Evaluation
    8. Prioritized WHAT / WHEN / WHY Recommendation Engine
    """
    try:
        # 1. Calculate Growth Stage from planting_date
        growth_stage_info = calculate_growth_stage(
            planting_date_str=request.planting_date,
            crop_name=request.Crop,
        )
        resolved_stage = request.growth_stage or growth_stage_info.get("growth_stage", "Vegetative")

        # 2. Fetch live weather snapshot & forecast from Open-Meteo
        snapshot = get_weather_snapshot_by_coordinates(
            request.Latitude,
            request.Longitude,
            location_label=request.location_name,
        )
        location_meta = snapshot.get("location", {})
        location_name = location_meta.get("name") or request.location_name or f"{request.Latitude:.2f}°N, {request.Longitude:.2f}°E"
        weather_dict = snapshot.get("weather", {})
        suggested = snapshot.get("suggested_values", {})
        weather_dict["Observation_Year"] = suggested.get("Observation_Year", datetime.now().year)
        weather_dict["Standard_Week"] = suggested.get("Standard_Week", int(datetime.now().isocalendar().week))

        forecast_data = get_forecast_7days(
            request.Latitude,
            request.Longitude,
            location_label=location_name,
        )
        forecast_days = forecast_data.get("days", [])
        matched_training_location = forecast_data.get("location", {}).get("matched_training_location") or location_name

        # 3. Tabular ML Pest Prediction (Rice / Cotton suite)
        pests_ranked = predict_all_pests_for_crop(request.Crop, weather_dict, matched_training_location)
        top_pest = pests_ranked[0] if pests_ranked else {
            "pest_name": "General Field Pest",
            "pest_value": 5.0,
            "risk_level": "Low",
        }
        forecast_risk = predict_forecast_risk(request.Crop, forecast_days, matched_training_location)

        tabular_ml_result = {
            "top_pest": top_pest,
            "pests_ranked": pests_ranked,
            "forecast_risk": forecast_risk,
        }

        # 4. Foliar Vision Pathology Lookup (if attached)
        diagnosis_dict = None
        if request.diagnosis_id:
            diag_rec = db.query(PlantDiagnosisRecord).filter(PlantDiagnosisRecord.id == request.diagnosis_id).first()
            if diag_rec:
                diagnosis_dict = diag_rec.to_dict()
                diagnosis_dict["is_valid_plant"] = True
                diagnosis_dict["disease"] = diag_rec.disease_name
                diagnosis_dict["confidence"] = diag_rec.confidence
                diagnosis_dict["is_healthy"] = diag_rec.is_healthy
                diagnosis_dict["severity"] = diag_rec.severity
        elif request.plant_id:
            # Check for latest diagnosis associated with this crop
            latest_diag = (
                db.query(PlantDiagnosisRecord)
                .filter(PlantDiagnosisRecord.crop_name.ilike(f"%{request.Crop}%"))
                .order_by(PlantDiagnosisRecord.created_at.desc())
                .first()
            )
            if latest_diag:
                diagnosis_dict = latest_diag.to_dict()
                diagnosis_dict["is_valid_plant"] = True
                diagnosis_dict["disease"] = latest_diag.disease_name
                diagnosis_dict["confidence"] = latest_diag.confidence
                diagnosis_dict["is_healthy"] = latest_diag.is_healthy
                diagnosis_dict["severity"] = latest_diag.severity

        # 5. Soil Context
        soil_data = {
            "soil_type": request.soil_type or "Loam",
            "soil_moisture": request.soil_moisture,
            "soil_ph": request.soil_ph,
            "soil_n": request.soil_n,
            "soil_p": request.soil_p,
            "soil_k": request.soil_k,
            "irrigation_method": request.irrigation_method or "Furrow / Basin",
        }

        # 6. Central Decision Engine Assessment
        decision_assessment = evaluate_crop_health_and_risk(
            crop=request.Crop,
            growth_stage_info=growth_stage_info,
            weather_dict=weather_dict,
            forecast_days=forecast_days,
            soil_data=soil_data,
            tabular_ml_result=tabular_ml_result,
            image_diagnosis_result=diagnosis_dict,
        )

        # 7. Structured WHAT / WHEN / WHY Recommendation Engine
        structured_recommendations = generate_structured_recommendations(
            crop=request.Crop,
            growth_stage_info=growth_stage_info,
            weather_dict=weather_dict,
            forecast_days=forecast_days,
            soil_data=soil_data,
            decision_assessment=decision_assessment,
            tabular_ml_result=tabular_ml_result,
            image_diagnosis_result=diagnosis_dict,
        )

        # 8. Legacy Smart Advisory for backward compatibility
        smart_advisory = generate_smart_advisory(
            crop=request.Crop,
            top_pest=top_pest["pest_name"],
            risk_level=top_pest["risk_level"],
            pests_ranked=pests_ranked,
            weather_dict=weather_dict,
        )

        # 9. Update Plant Surveillance State in DB if plant_id provided
        user_id = _get_optional_user_id(db, authorization)
        top_action_title = (
            structured_recommendations["prioritized_actions"][0]["title"]
            if structured_recommendations["prioritized_actions"]
            else "Routine field surveillance"
        )
        if request.plant_id and db is not None:
            try:
                plant_obj = db.query(Plant).filter(Plant.id == request.plant_id).first()
                if plant_obj:
                    plant_obj.last_assessment_date = datetime.now(timezone.utc)
                    plant_obj.last_health_status = decision_assessment["overall_health_status"]
                    plant_obj.last_risk_level = decision_assessment["overall_risk_level"]
                    plant_obj.last_recommended_action = top_action_title
                    plant_obj.growth_stage = resolved_stage
                    db.commit()
            except Exception as e:
                print(f"Non-fatal notice: could not update plant record: {e}")

        # 10. Persist Record to PredictionHistory
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
            growth_stage=resolved_stage,
            field_name=request.field_name,
            field_size=request.field_size,
            soil_type=request.soil_type,
            soil_moisture=request.soil_moisture,
            soil_ph=request.soil_ph,
        )

        if record:
            try:
                record.diagnosis_id = request.diagnosis_id or (diagnosis_dict.get("id") if diagnosis_dict else None)
                record.health_status = decision_assessment["overall_health_status"]
                record.data_sources_json = json.dumps(decision_assessment["data_sources"])
                # Store structured recommendations inside advisory_json
                combined_advisory = {
                    **smart_advisory,
                    "structured_recommendations": structured_recommendations,
                    "decision_assessment": decision_assessment,
                }
                record.advisory_json = json.dumps(combined_advisory)
                db.commit()
            except Exception:
                pass

        # 11. Environmental Contributing Factors
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
                "source": "LIVE WEATHER (OPEN-METEO)",
            },
            {
                "factor": "Morning Relative Humidity",
                "value": f"{rh1_val}%",
                "impact": "High microclimate moisture sustains foliar fungal pathogens and soft-bodied sucking pests.",
                "status": "High" if rh1_val > 75.0 else "Moderate",
                "source": "LIVE WEATHER (OPEN-METEO)",
            },
            {
                "factor": "Precipitation Accumulation",
                "value": f"{rf_val} mm",
                "impact": "Standing water in furrows increases root rot susceptibility." if rf_val > 5.0 else "Dry conditions favor mite and aphid proliferation.",
                "status": "Warning" if rf_val > 25.0 else "Normal",
                "source": "LIVE WEATHER (OPEN-METEO)",
            },
            {
                "factor": "Soil Environment",
                "value": f"{request.soil_type or 'Loam'} (pH {request.soil_ph or 6.5}, {request.soil_moisture or 60}% moisture)",
                "impact": "Soil moisture balance directly influences crop turgor and nutrient absorption.",
                "status": "Optimal" if (5.5 <= (request.soil_ph or 6.5) <= 7.5) else "Stressed",
                "source": "USER / SENSOR DATA",
            },
        ]

        return {
            "prediction_id": record.id if record else None,
            "crop": request.Crop,
            "plant": {
                "id": request.plant_id,
                "name": request.plant_name or f"{request.Crop} Field",
                "crop_type": request.Crop,
                "variety": request.crop_variety or "Standard",
                "planting_date": request.planting_date,
                "days_after_planting": growth_stage_info.get("days_after_planting"),
                "growth_stage": resolved_stage,
                "growth_stage_details": growth_stage_info,
                "field_name": request.field_name or "Primary Field",
                "field_size": request.field_size or 1.0,
                "field_size_unit": request.field_size_unit or "acres",
                "irrigation_method": soil_data["irrigation_method"],
                "soil_type": soil_data["soil_type"],
                "soil_moisture": soil_data["soil_moisture"],
                "soil_ph": soil_data["soil_ph"],
                "soil_n": soil_data["soil_n"],
                "soil_p": soil_data["soil_p"],
                "soil_k": soil_data["soil_k"],
            },
            "location": {
                "display_name": location_name,
                "matched_training_location": matched_training_location,
                "latitude": request.Latitude,
                "longitude": request.Longitude,
                "source": "GPS SENSOR / NOMINATIM GEOCODING",
            },
            "current_weather": weather_dict,
            "forecast_days": forecast_days,
            "growth_stage_info": growth_stage_info,
            "top_pest": top_pest,
            "pests_ranked": pests_ranked,
            "forecast_risk": forecast_risk,
            "decision_assessment": decision_assessment,
            "recommendations": structured_recommendations,
            "smart_advisory": smart_advisory,
            "contributing_factors": contributing_factors,
            "data_sources": decision_assessment["data_sources"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "Assessment Completed Successfully",
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
app.include_router(diagnosis_router)
app.include_router(irrigation_router)
app.include_router(irrigation_history_router)