from typing import List, Optional
from sqlalchemy.orm import Session

from .models import Plant
from .schemas import PlantCreate, PlantUpdate


DEFAULT_STARTER_PLANTS = [
    {
        "name": "Paddy Rice (IR-64)",
        "crop_type": "Rice",
        "variety": "IR-64 High Yield",
        "planting_date": "2026-06-15",
        "growth_stage": "Tillering",
        "field_name": "Cauvery Delta Plot 1",
        "field_position": "Cauvery Basin - Sector A",
        "field_size": 4.5,
        "field_size_unit": "acres",
        "irrigation_method": "Flood / Furrow",
        "irrigation_frequency": "2 times daily",
        "irrigation_hours": 2.5,
        "auto_irrigation_alerts": True,
        "soil_type": "Clay Loam",
        "soil_moisture": 72.0,
        "soil_ph": 6.8,
        "latitude": 10.7870,
        "longitude": 79.1378,
        "location_name": "Thanjavur, Tamil Nadu",
        "notes": "Lowland irrigated paddy with active water management.",
    },
    {
        "name": "Hybrid Cotton (Bt RCH-2)",
        "crop_type": "Cotton",
        "variety": "Bollgard II RCH-2",
        "planting_date": "2026-05-20",
        "growth_stage": "Squaring & Flowering",
        "field_name": "Black Soil Sector B",
        "field_position": "Black Soil Sector B - Ridge 3",
        "field_size": 6.0,
        "field_size_unit": "acres",
        "irrigation_method": "Drip Irrigation",
        "irrigation_frequency": "Every 2 days",
        "irrigation_hours": 3.0,
        "auto_irrigation_alerts": True,
        "soil_type": "Black Soil",
        "soil_moisture": 48.0,
        "soil_ph": 7.4,
        "latitude": 11.0168,
        "longitude": 76.9558,
        "location_name": "Coimbatore, Tamil Nadu",
        "notes": "Drip irrigated hybrid cotton with pheromone traps installed.",
    },
]


from agronomy.growth_stage import calculate_growth_stage


def _enrich_plant_growth(plant: Plant) -> Plant:
    if plant and plant.planting_date:
        try:
            stage_info = calculate_growth_stage(plant.planting_date, plant.crop_type)
            setattr(plant, "days_after_planting", stage_info.get("days_after_planting"))
            setattr(plant, "growth_stage_details", stage_info)
            if not plant.growth_stage or plant.growth_stage == "Vegetative":
                plant.growth_stage = stage_info.get("growth_stage")
        except Exception:
            pass
    return plant


def seed_starter_plants_if_empty(db: Session, user_id: int) -> List[Plant]:
    count = db.query(Plant).filter(Plant.user_id == user_id).count()
    if count == 0:
        for starter in DEFAULT_STARTER_PLANTS:
            plant = Plant(user_id=user_id, **starter)
            db.add(plant)
        db.commit()
    plants = db.query(Plant).filter(Plant.user_id == user_id).order_by(Plant.id.asc()).all()
    return [_enrich_plant_growth(p) for p in plants]


def get_user_plants(db: Session, user_id: int) -> List[Plant]:
    plants = db.query(Plant).filter(Plant.user_id == user_id).order_by(Plant.updated_at.desc()).all()
    if not plants:
        return []
    return [_enrich_plant_growth(p) for p in plants]


def get_plant_by_id(db: Session, plant_id: int, user_id: int) -> Optional[Plant]:
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == user_id).first()
    return _enrich_plant_growth(plant) if plant else None


def create_plant(db: Session, user_id: int, data: PlantCreate) -> Plant:
    payload = data.model_dump()
    raw_type = payload.get("crop_type") or "Rice"
    known_crops = {
        "cotton": "Cotton", "rice": "Rice", "maize": "Maize", "corn": "Maize",
        "wheat": "Wheat", "potato": "Potato", "tomato": "Tomato",
        "sugarcane": "Sugarcane", "soybean": "Soybean", "groundnut": "Groundnut",
    }
    matched = None
    for k, v in known_crops.items():
        if k in raw_type.lower():
            matched = v
            break
    payload["crop_type"] = matched or raw_type.strip().title()

    plant = Plant(user_id=user_id, **payload)
    db.add(plant)
    db.commit()
    db.refresh(plant)

    # Automatically send irrigation email alert if auto alerts enabled and moisture indicates water is needed
    moisture = plant.soil_moisture if plant.soil_moisture is not None else 20.0
    if plant.auto_irrigation_alerts and moisture < 30.0:
        try:
            import json
            from auth.models import User
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.email:
                from irrigation.email_service import send_irrigation_alert_email
                from irrigation.history_models import IrrigationHistory

                pos = plant.field_position or plant.field_name or "Primary Field Zone"
                freq = plant.irrigation_frequency or "2 times daily"
                hrs = plant.irrigation_hours or 2.0
                advisories = [
                    f"Plant '{plant.name}' was registered with soil moisture at {moisture:.1f}% VWC (irrigation threshold is 30%).",
                    f"Recommended schedule: {freq}, running pumps for {hrs} hours in {pos}.",
                    "Early morning or late evening operation recommended to prevent evaporation loss.",
                ]

                email_res = send_irrigation_alert_email(
                    to_email=user.email,
                    farmer_name=user.name,
                    plant_name=plant.name,
                    crop_type=plant.crop_type,
                    field_position=pos,
                    irrigation_frequency=freq,
                    irrigation_hours=hrs,
                    soil_moisture=moisture,
                    water_quantity="25–35 mm (~250,000–350,000 L/ha)",
                    timing_advice="Early morning (6 AM – 9 AM) to minimize evaporation loss.",
                    advisories=advisories,
                )

                hist_entry = IrrigationHistory(
                    user_id=user_id,
                    plant_id=plant.id,
                    plant_name=plant.name,
                    crop_type=plant.crop_type,
                    field_position=pos,
                    irrigation_needed=True,
                    irrigation_frequency=freq,
                    irrigation_hours=hrs,
                    water_quantity="25–35 mm (~250,000–350,000 L/ha)",
                    timing_advice="Early morning (6 AM – 9 AM) to minimize evaporation loss.",
                    soil_moisture=moisture,
                    risk_level="High" if moisture < 20.0 else "Medium",
                    water_stress="Severe" if moisture < 16.0 else "Moderate",
                    dispatch_type="registration_alert",
                    email_sent=bool(email_res.get("sent", False)),
                    email_recipient=user.email,
                    advisory_notes=json.dumps(advisories),
                )
                db.add(hist_entry)
                db.commit()
        except Exception as exc:
            print(f"[Plant Registration Alert] Warning: {exc}")

    return plant


def update_plant(db: Session, plant_id: int, user_id: int, data: PlantUpdate) -> Optional[Plant]:
    plant = get_plant_by_id(db, plant_id, user_id)
    if not plant:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "crop_type" in update_data and update_data["crop_type"]:
        raw_type = update_data["crop_type"]
        known_crops = {
            "cotton": "Cotton", "rice": "Rice", "maize": "Maize", "corn": "Maize",
            "wheat": "Wheat", "potato": "Potato", "tomato": "Tomato",
            "sugarcane": "Sugarcane", "soybean": "Soybean", "groundnut": "Groundnut",
        }
        matched = None
        for k, v in known_crops.items():
            if k in raw_type.lower():
                matched = v
                break
        update_data["crop_type"] = matched or raw_type.strip().title()

    for field, value in update_data.items():
        setattr(plant, field, value)

    db.commit()
    db.refresh(plant)
    return plant


def delete_plant(db: Session, plant_id: int, user_id: int) -> bool:
    plant = get_plant_by_id(db, plant_id, user_id)
    if not plant:
        return False
    db.delete(plant)
    db.commit()
    return True
