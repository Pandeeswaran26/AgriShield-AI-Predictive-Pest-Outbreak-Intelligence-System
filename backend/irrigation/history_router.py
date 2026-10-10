"""
Irrigation History Router
AgriShield AI Platform
=======================
Endpoints:
  GET  /irrigation/history            — list irrigation history records (paginated)
  POST /irrigation/history/log        — manually log an irrigation event
  GET  /irrigation/history/{id}       — get a single history record
  DELETE /irrigation/history/{id}     — delete a record
  POST /irrigation/history/send-morning  — trigger morning scheduled dispatch
  POST /irrigation/history/send-evening  — trigger evening scheduled dispatch
"""
import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.database import get_db
from auth.models import User
from auth.service import get_current_user
from plants.models import Plant
from .history_models import IrrigationHistory
from .email_service import send_irrigation_alert_email
from .service import predict_irrigation

router = APIRouter(prefix="/irrigation", tags=["Irrigation History"])


# ─── Pydantic Schemas ─────────────────────────────────────────────────

class IrrigationLogRequest(BaseModel):
    plant_id:             Optional[int]   = Field(None, description="Linked plant record ID")
    plant_name:           str             = Field(..., description="Plant display name")
    crop_type:            str             = Field("Rice", description="Crop family")
    field_position:       Optional[str]   = Field(None, description="Field zone / position")
    irrigation_needed:    bool            = Field(True)
    irrigation_frequency: Optional[str]   = Field(None)
    irrigation_hours:     Optional[float] = Field(None)
    water_quantity:       Optional[str]   = Field(None)
    timing_advice:        Optional[str]   = Field(None)
    soil_moisture:        Optional[float] = Field(None, ge=0, le=100)
    soil_temperature:     Optional[float] = Field(None)
    temperature:          Optional[float] = Field(None)
    humidity:             Optional[float] = Field(None)
    rainfall:             Optional[float] = Field(None)
    risk_level:           Optional[str]   = Field(None)
    water_stress:         Optional[str]   = Field(None)
    probability:          Optional[float] = Field(None)
    dispatch_type:        str             = Field("manual")
    advisory_notes:       Optional[List[str]] = Field(None)


class ScheduledDispatchRequest(BaseModel):
    """Trigger a morning/evening dispatch for all plants that have auto_irrigation_alerts=True."""
    force_send: bool = Field(False, description="Send even if irrigation is not predicted to be needed")


# ─── Helpers ──────────────────────────────────────────────────────────

def resolve_user(authorization: Optional[str], db: Session) -> Optional[User]:
    if authorization and authorization.startswith("Bearer "):
        try:
            return get_current_user(db, authorization)
        except Exception:
            pass
    return db.query(User).first()


def _serialize_history(record: IrrigationHistory) -> dict:
    notes = []
    if record.advisory_notes:
        try:
            notes = json.loads(record.advisory_notes)
        except Exception:
            notes = [record.advisory_notes]
    return {
        "id":                   record.id,
        "user_id":              record.user_id,
        "plant_id":             record.plant_id,
        "plant_name":           record.plant_name,
        "crop_type":            record.crop_type,
        "field_position":       record.field_position or "Primary Field Zone",
        "irrigation_needed":    record.irrigation_needed,
        "irrigation_frequency": record.irrigation_frequency,
        "irrigation_hours":     record.irrigation_hours,
        "water_quantity":       record.water_quantity,
        "timing_advice":        record.timing_advice,
        "soil_moisture":        record.soil_moisture,
        "soil_temperature":     record.soil_temperature,
        "temperature":          record.temperature,
        "humidity":             record.humidity,
        "rainfall":             record.rainfall,
        "risk_level":           record.risk_level,
        "water_stress":         record.water_stress,
        "probability":          record.probability,
        "dispatch_type":        record.dispatch_type,
        "email_sent":           record.email_sent,
        "email_recipient":      record.email_recipient,
        "advisory_notes":       notes,
        "recorded_at":          record.recorded_at.isoformat() if record.recorded_at else None,
    }


# ─── Endpoints ────────────────────────────────────────────────────────

@router.get("/history")
def list_irrigation_history(
    limit:  int = 50,
    offset: int = 0,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Return paginated irrigation history records for the authenticated user,
    sorted newest-first.
    """
    user = resolve_user(authorization, db)
    query = db.query(IrrigationHistory)
    if user:
        query = query.filter(IrrigationHistory.user_id == user.id)
    records = query.order_by(IrrigationHistory.recorded_at.desc()).offset(offset).limit(limit).all()
    total   = query.count()
    return {
        "status": "success",
        "total":  total,
        "data":   [_serialize_history(r) for r in records],
    }


@router.post("/history/log")
def log_irrigation_event(
    request: IrrigationLogRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Manually log a new irrigation event to the history ledger.
    """
    user = resolve_user(authorization, db)
    record = IrrigationHistory(
        user_id              = user.id if user else None,
        plant_id             = request.plant_id,
        plant_name           = request.plant_name,
        crop_type            = request.crop_type,
        field_position       = request.field_position or "Primary Field Zone",
        irrigation_needed    = request.irrigation_needed,
        irrigation_frequency = request.irrigation_frequency,
        irrigation_hours     = request.irrigation_hours,
        water_quantity       = request.water_quantity,
        timing_advice        = request.timing_advice,
        soil_moisture        = request.soil_moisture,
        soil_temperature     = request.soil_temperature,
        temperature          = request.temperature,
        humidity             = request.humidity,
        rainfall             = request.rainfall,
        risk_level           = request.risk_level,
        water_stress         = request.water_stress,
        probability          = request.probability,
        dispatch_type        = request.dispatch_type,
        email_sent           = False,
        email_recipient      = user.email if user else None,
        advisory_notes       = json.dumps(request.advisory_notes or []),
        recorded_at          = datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"status": "success", "data": _serialize_history(record)}


@router.get("/history/{record_id}")
def get_irrigation_history_record(
    record_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Retrieve a single irrigation history record by ID."""
    record = db.query(IrrigationHistory).filter(IrrigationHistory.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Irrigation history record not found.")
    return {"status": "success", "data": _serialize_history(record)}


@router.delete("/history/{record_id}")
def delete_irrigation_history_record(
    record_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Delete an irrigation history record."""
    record = db.query(IrrigationHistory).filter(IrrigationHistory.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    db.delete(record)
    db.commit()
    return {"status": "success", "message": f"Record {record_id} deleted."}


# ─── Scheduled Morning / Evening Dispatch ─────────────────────────────

def _run_scheduled_dispatch(dispatch_type: str, db: Session, force_send: bool = False) -> dict:
    """
    Core logic: iterate all plants with auto_irrigation_alerts=True,
    run irrigation prediction, send emails if irrigation is needed,
    and save every result to IrrigationHistory.
    """
    plants = db.query(Plant).filter(Plant.auto_irrigation_alerts == True).all()
    dispatched = []
    skipped    = []

    for plant in plants:
        # Fetch the owning user to get their email
        user = db.query(User).filter(User.id == plant.user_id).first() if hasattr(plant, "user_id") else None
        to_email     = user.email if user else None
        farmer_name  = user.name  if user else "Farmer"

        # Use stored soil / weather defaults if available, otherwise safe defaults
        soil_moisture   = float(getattr(plant, "soil_moisture",   None) or 22.0)
        soil_temperature = 28.0
        temperature      = 32.0
        humidity         = 68.0
        rainfall         = 0.0

        try:
            pred = predict_irrigation(
                crop_name            = getattr(plant, "crop_type", None) or "Rice",
                crop_days            = max(1, int(getattr(plant, "crop_days", 45) or 45)),
                soil_moisture        = soil_moisture,
                soil_temperature     = soil_temperature,
                temperature          = temperature,
                humidity             = humidity,
                rainfall             = rainfall,
                plant_name           = plant.name,
                field_position       = getattr(plant, "field_position", None) or "Primary Field Zone",
                irrigation_frequency = getattr(plant, "irrigation_frequency", None),
                irrigation_hours     = getattr(plant, "irrigation_hours", None),
                to_email             = None,   # email is dispatched explicitly below
                farmer_name          = farmer_name,
                send_email           = False,  # handle separately so we can log first
            )

        except Exception as exc:
            skipped.append({"plant": plant.name, "reason": str(exc)})
            continue

        email_result = None
        if (pred["irrigation_needed"] or force_send) and to_email:
            email_result = send_irrigation_alert_email(
                to_email             = to_email,
                farmer_name          = farmer_name,
                plant_name           = plant.name,
                crop_type            = pred["crop"],
                field_position       = pred["field_position"],
                irrigation_frequency = pred["irrigation_frequency"],
                irrigation_hours     = pred["irrigation_hours"],
                soil_moisture        = soil_moisture,
                water_quantity       = pred["water_quantity"],
                timing_advice        = pred["timing_advice"],
                advisories           = pred["advisory"],
            )

        # Save to history
        hist = IrrigationHistory(
            user_id              = user.id if user else None,
            plant_id             = plant.id,
            plant_name           = plant.name,
            crop_type            = pred["crop"],
            field_position       = pred["field_position"],
            irrigation_needed    = pred["irrigation_needed"],
            irrigation_frequency = pred["irrigation_frequency"],
            irrigation_hours     = pred["irrigation_hours"],
            water_quantity       = pred["water_quantity"],
            timing_advice        = pred["timing_advice"],
            soil_moisture        = soil_moisture,
            soil_temperature     = soil_temperature,
            temperature          = temperature,
            humidity             = humidity,
            rainfall             = rainfall,
            risk_level           = pred["risk_level"],
            water_stress         = pred["water_stress"],
            probability          = pred["probability"],
            dispatch_type        = dispatch_type,
            email_sent           = bool(email_result and email_result.get("sent")),
            email_recipient      = to_email,
            advisory_notes       = json.dumps(pred["advisory"]),
            recorded_at          = datetime.utcnow(),
        )
        db.add(hist)
        dispatched.append({"plant": plant.name, "irrigation_needed": pred["irrigation_needed"], "email_sent": hist.email_sent})

    db.commit()
    return {
        "dispatch_type": dispatch_type,
        "dispatched": dispatched,
        "skipped":    skipped,
        "total_plants": len(plants),
        "total_alerts": sum(1 for d in dispatched if d["email_sent"]),
    }


@router.post("/history/send-morning")
def send_morning_irrigation_dispatch(
    request: ScheduledDispatchRequest = ScheduledDispatchRequest(),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    🌅 Morning irrigation dispatch — runs analysis for all registered plants
    and sends email alerts for those that need water. Automatically logs
    every event to Irrigation History.
    """
    result = _run_scheduled_dispatch("morning_schedule", db, force_send=request.force_send)
    return {"status": "success", "data": result}


@router.post("/history/send-evening")
def send_evening_irrigation_dispatch(
    request: ScheduledDispatchRequest = ScheduledDispatchRequest(),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    🌇 Evening irrigation dispatch — runs analysis for all registered plants
    and sends email alerts for those that need water. Automatically logs
    every event to Irrigation History.
    """
    result = _run_scheduled_dispatch("evening_schedule", db, force_send=request.force_send)
    return {"status": "success", "data": result}
