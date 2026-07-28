from pydantic import BaseModel


class DashboardSummary(BaseModel):
    totalPredictions: int
    highRisk: int
    mediumRisk: int
    lowRisk: int
    todayPredictions: int