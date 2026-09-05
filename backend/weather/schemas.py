from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class WeatherCurrentResponse(BaseModel):
    temperature: Optional[float] = Field(None, description="Current temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Relative humidity percentage")
    wind_speed: Optional[float] = Field(None, description="Wind speed in km/h")
    rainfall: Optional[float] = Field(None, description="Current precipitation in mm")


class LocationMetadata(BaseModel):
    name: str
    admin1: Optional[str] = None
    country: Optional[str] = None
    latitude: float
    longitude: float
    timezone: str = "auto"


class SuggestedValues(BaseModel):
    Observation_Year: int
    Standard_Week: int


class WeatherParameters(BaseModel):
    MaxT: Optional[float] = None
    MinT: Optional[float] = None
    RH1: Optional[float] = None
    RH2: Optional[float] = None
    RF: Optional[float] = None
    WS: Optional[float] = None
    SSH: Optional[float] = None
    EVP: Optional[float] = None


class WeatherSnapshotResponse(BaseModel):
    location: LocationMetadata
    suggested_values: SuggestedValues
    weather: WeatherParameters
    source: str = "Open-Meteo"
