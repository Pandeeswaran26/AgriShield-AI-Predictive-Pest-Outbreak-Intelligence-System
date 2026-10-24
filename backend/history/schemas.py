from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class HistoryItem(BaseModel):
    id: int
    user_id: Optional[int] = None
    crop: str
    pest_name: str
    location: str
    location_display: Optional[str] = None
    risk_level: str
    confidence: Optional[float] = None
    pest_value: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    auto_mode: Optional[bool] = False
    plant_id: Optional[int] = None
    plant_name: Optional[str] = None
    crop_variety: Optional[str] = None
    growth_stage: Optional[str] = None
    field_name: Optional[str] = None
    field_size: Optional[float] = None
    soil_type: Optional[str] = None
    soil_moisture: Optional[float] = None
    soil_ph: Optional[float] = None
    pests_json: Optional[str] = None
    forecast_json: Optional[str] = None
    advisory_json: Optional[str] = None
    prediction_date: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int