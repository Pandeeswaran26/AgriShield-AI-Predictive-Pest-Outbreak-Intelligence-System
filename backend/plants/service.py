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
        "field_size": 4.5,
        "field_size_unit": "acres",
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
        "field_size": 6.0,
        "field_size_unit": "acres",
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
        return seed_starter_plants_if_empty(db, user_id)
    return [_enrich_plant_growth(p) for p in plants]


def get_plant_by_id(db: Session, plant_id: int, user_id: int) -> Optional[Plant]:
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == user_id).first()
    return _enrich_plant_growth(plant) if plant else None


def create_plant(db: Session, user_id: int, data: PlantCreate) -> Plant:
    payload = data.model_dump()
    # Normalize crop_type to standard model suite ('Cotton' or 'Rice')
    raw_type = payload.get("crop_type") or "Rice"
    payload["crop_type"] = "Cotton" if "cotton" in raw_type.lower() else "Rice"

    plant = Plant(user_id=user_id, **payload)
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


def update_plant(db: Session, plant_id: int, user_id: int, data: PlantUpdate) -> Optional[Plant]:
    plant = get_plant_by_id(db, plant_id, user_id)
    if not plant:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "crop_type" in update_data and update_data["crop_type"]:
        raw_type = update_data["crop_type"]
        update_data["crop_type"] = "Cotton" if "cotton" in raw_type.lower() else "Rice"

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
