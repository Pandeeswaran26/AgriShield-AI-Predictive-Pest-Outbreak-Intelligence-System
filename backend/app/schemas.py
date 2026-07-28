from pydantic import BaseModel


class PredictionRequest(BaseModel):
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


class PredictionResponse(BaseModel):
    predicted_pest_value: float
    risk_level: str
    status: str