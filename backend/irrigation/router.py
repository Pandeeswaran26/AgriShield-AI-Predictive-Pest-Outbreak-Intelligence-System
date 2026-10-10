"""
Irrigation AI Router
AgriShield Platform
====================
Exposes:
  POST /irrigation/predict    — full irrigation prediction + automated email alert
  POST /irrigation/send-alert — direct irrigation email dispatch
  GET  /irrigation/crops      — list of supported crops
  GET  /irrigation/metadata   — model info and metrics
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session

from database.database import get_db
from auth.models import User
from auth.service import get_current_user
from plants.models import Plant
from .service import predict_irrigation, get_supported_crops, get_model_metadata
from .email_service import send_irrigation_alert_email

router = APIRouter(prefix="/irrigation", tags=["Irrigation AI"])


class IrrigationRequest(BaseModel):
    crop_name:            str            = Field(..., description="Crop name (e.g. Rice, Tomato, Cotton, Potato)")
    crop_days:            float          = Field(..., ge=1, le=500, description="Days elapsed in growth cycle")
    soil_moisture:        float          = Field(..., ge=0, le=100, description="Soil volumetric water content (% VWC)")
    soil_temperature:     float          = Field(..., ge=0, le=60, description="Topsoil temperature (°C)")
    temperature:          float          = Field(..., ge=0, le=60, description="Ambient temperature (°C)")
    humidity:             float          = Field(..., ge=0, le=100, description="Relative humidity (%)")
    rainfall:             float          = Field(0.0, ge=0, le=500, description="Rainfall in last 24h (mm)")
    plant_id:             Optional[int]  = Field(None, description="Optional ID of registered plant")
    plant_name:           Optional[str]  = Field(None, description="Plant name or label")
    field_position:       Optional[str]  = Field(None, description="Field position / zone / ridge")
    irrigation_frequency: Optional[str]  = Field(None, description="e.g. 2 times daily, Once daily, Every 2 days")
    irrigation_hours:     Optional[float]= Field(None, ge=0.0, le=24.0, description="Hours runtime needed per irrigation session")
    to_email:             Optional[str]  = Field(None, description="Target email for irrigation alert")
    send_email:           bool           = Field(True, description="Whether to automatically send alert email if water is needed")


class DirectAlertRequest(BaseModel):
    plant_name:           str            = Field(..., description="Name of the plant")
    crop_type:            str            = Field("Rice", description="Crop family")
    field_position:       str            = Field("Primary Field Zone", description="Position or zone")
    irrigation_frequency: str            = Field("2 times daily", description="How many times water is needed")
    irrigation_hours:     float          = Field(2.0, ge=0.1, le=24.0, description="How many hours water is needed")
    soil_moisture:        float          = Field(..., ge=0, le=100, description="Current soil moisture %")
    water_quantity:       str            = Field("25–35 mm (~250,000–350,000 L/ha)", description="Recommended quantity")
    timing_advice:        str            = Field("Early morning (6 AM – 9 AM)", description="Best timing window")
    to_email:             Optional[str]  = Field(None, description="Recipient email (defaults to current user)")
    advisories:           Optional[List[str]] = Field(None, description="Optional field guidelines")


def resolve_user_context(authorization: Optional[str], db: Session) -> Optional[User]:
    if authorization and authorization.startswith("Bearer "):
        try:
            return get_current_user(db, authorization)
        except Exception:
            pass
    # Local development fallback: get first user
    return db.query(User).first()


@router.post("/predict")
def irrigation_predict(
    request: IrrigationRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Predict irrigation requirement for a crop with current field conditions.
    If water is needed and send_email is True, automatically dispatches
    an alert to the registered user's email with plant name, position, frequency, and runtime hours.
    """
    try:
        user = resolve_user_context(authorization, db)
        resolved_email = request.to_email or (user.email if user else None)
        farmer_name = user.name if user else "Farmer"

        # Autofill from plant record if plant_id is provided
        target_plant_name = request.plant_name
        target_position = request.field_position
        target_frequency = request.irrigation_frequency
        target_hours = request.irrigation_hours

        if request.plant_id:
            plant = db.query(Plant).filter(Plant.id == request.plant_id).first()
            if plant:
                target_plant_name = target_plant_name or plant.name
                target_position = target_position or plant.field_position or plant.field_name
                target_frequency = target_frequency or plant.irrigation_frequency
                target_hours = target_hours if target_hours is not None else plant.irrigation_hours

        result = predict_irrigation(
            crop_name            = request.crop_name,
            crop_days            = request.crop_days,
            soil_moisture        = request.soil_moisture,
            soil_temperature     = request.soil_temperature,
            temperature          = request.temperature,
            humidity             = request.humidity,
            rainfall             = request.rainfall,
            plant_name           = target_plant_name,
            field_position       = target_position,
            irrigation_frequency = target_frequency,
            irrigation_hours     = target_hours,
            to_email             = resolved_email,
            farmer_name          = farmer_name,
            send_email           = request.send_email,
        )
        return {"status": "success", "data": result}
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail="Irrigation AI model not loaded. Run ml/training/train_irrigation_model.py first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-alert")
def send_direct_irrigation_alert(
    request: DirectAlertRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Directly trigger sending an automated irrigation email alert to the registered farmer.
    """
    user = resolve_user_context(authorization, db)
    target_email = request.to_email or (user.email if user else None)
    farmer_name = user.name if user else "Farmer"

    if not target_email:
        raise HTTPException(
            status_code=400,
            detail="Recipient email address not found. Please provide to_email or authenticate.",
        )

    alert_result = send_irrigation_alert_email(
        to_email             = target_email,
        farmer_name          = farmer_name,
        plant_name           = request.plant_name,
        crop_type            = request.crop_type,
        field_position       = request.field_position,
        irrigation_frequency = request.irrigation_frequency,
        irrigation_hours     = request.irrigation_hours,
        soil_moisture        = request.soil_moisture,
        water_quantity       = request.water_quantity,
        timing_advice        = request.timing_advice,
        advisories           = request.advisories,
    )
    return {"status": "success", "data": alert_result}


@router.get("/crops")
def list_irrigation_crops():
    """Returns list of crop names supported by the Irrigation AI model."""
    try:
        return {"status": "success", "crops": get_supported_crops()}
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Irrigation model not available.")


@router.get("/metadata")
def irrigation_model_metadata():
    """Returns Irrigation AI model version, performance metrics, and feature importance."""
    try:
        return {"status": "success", "metadata": get_model_metadata()}
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Irrigation model not available.")
