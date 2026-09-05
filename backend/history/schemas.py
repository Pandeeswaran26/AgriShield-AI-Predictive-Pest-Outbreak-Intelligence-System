from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: int
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
    pests_json: Optional[str] = None
    forecast_json: Optional[str] = None
    advisory_json: Optional[str] = None
    prediction_date: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int