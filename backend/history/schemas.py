from datetime import datetime
from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: int
    crop: str
    pest_name: str
    location: str
    risk_level: str
    confidence: float
    pest_value: float
    prediction_date: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int