from typing import Optional
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Legacy manual-input prediction schema — kept for backward compatibility."""
    Crop: str
    Observation_Year: int
    Standard_Week: int
    Pest_Name: str
    Location: str

    MaxT: float
    MinT: float

    RH1: float
    RH2: float

    RF: float
    WS: float
    SSH: float
    EVP: float


class AutoPredictionRequest(BaseModel):
    """
    Dynamic and automatic prediction schema.
    Farmer selects/defines a plant with field details + coordinates.
    Weather is auto-synchronized, and multi-pest risk modeling executes.
    """
    Crop: str
    Latitude: float = Field(..., ge=-90, le=90)
    Longitude: float = Field(..., ge=-180, le=180)

    # Optional dynamic plant and field parameters
    plant_id: Optional[int] = None
    plant_name: Optional[str] = None
    crop_variety: Optional[str] = None
    growth_stage: Optional[str] = None
    field_name: Optional[str] = None
    field_size: Optional[float] = None
    field_size_unit: Optional[str] = "acres"
    soil_type: Optional[str] = None
    soil_moisture: Optional[float] = None
    soil_ph: Optional[float] = None
    location_name: Optional[str] = None


class PredictionResponse(BaseModel):
    predicted_pest_value: float
    risk_level: str
    status: str