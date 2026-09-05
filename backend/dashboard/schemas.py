from pydantic import BaseModel


class DashboardSummary(BaseModel):
    totalPredictions: int
    highRisk: int
    mediumRisk: int
    lowRisk: int
    todayPredictions: int


class PestTrend(BaseModel):
    pest: str
    value: int


class MonthlyPrediction(BaseModel):
    month: str
    count: int


class CropAnalysis(BaseModel):
    crop: str
    value: int