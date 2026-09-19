from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PlantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Name or title of this plant crop")
    crop_type: str = Field("Rice", description="Base crop family for ML model: 'Rice' or 'Cotton'")
    variety: Optional[str] = Field(None, max_length=100)
    planting_date: Optional[str] = None
    growth_stage: Optional[str] = Field(None, max_length=60)
    field_name: Optional[str] = Field(None, max_length=100)
    field_size: Optional[float] = Field(None, ge=0.0)
    field_size_unit: Optional[str] = Field("acres", max_length=20)
    irrigation_method: Optional[str] = Field(None, max_length=60)
    soil_type: Optional[str] = Field(None, max_length=60)
    soil_moisture: Optional[float] = Field(None, ge=0.0, le=100.0)
    soil_ph: Optional[float] = Field(None, ge=0.0, le=14.0)
    soil_n: Optional[float] = Field(None, ge=0.0)
    soil_p: Optional[float] = Field(None, ge=0.0)
    soil_k: Optional[float] = Field(None, ge=0.0)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    location_name: Optional[str] = Field(None, max_length=200)
    last_assessment_date: Optional[datetime] = None
    last_health_status: Optional[str] = None
    last_risk_level: Optional[str] = None
    last_recommended_action: Optional[str] = None
    notes: Optional[str] = None


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    crop_type: Optional[str] = None
    variety: Optional[str] = None
    planting_date: Optional[str] = None
    growth_stage: Optional[str] = None
    field_name: Optional[str] = None
    field_size: Optional[float] = Field(None, ge=0.0)
    field_size_unit: Optional[str] = None
    irrigation_method: Optional[str] = None
    soil_type: Optional[str] = None
    soil_moisture: Optional[float] = Field(None, ge=0.0, le=100.0)
    soil_ph: Optional[float] = Field(None, ge=0.0, le=14.0)
    soil_n: Optional[float] = Field(None, ge=0.0)
    soil_p: Optional[float] = Field(None, ge=0.0)
    soil_k: Optional[float] = Field(None, ge=0.0)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    location_name: Optional[str] = None
    last_assessment_date: Optional[datetime] = None
    last_health_status: Optional[str] = None
    last_risk_level: Optional[str] = None
    last_recommended_action: Optional[str] = None
    notes: Optional[str] = None


class PlantResponse(PlantBase):
    id: int
    user_id: int
    days_after_planting: Optional[int] = None
    growth_stage_details: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
