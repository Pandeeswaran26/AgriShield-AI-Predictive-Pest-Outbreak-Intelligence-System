from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class TreatmentSchema(BaseModel):
    biological: List[str] = []
    chemical: List[str] = []


class DiagnosisResponse(BaseModel):
    # ── Validation gate fields (always present) ──────────────────────────────
    is_valid_plant: bool = True
    plant_confidence: Optional[float] = None       # 0.0–1.0 from validator
    is_ambiguous_image: bool = False               # True when borderline valid
    rejection_reason: Optional[str] = None         # populated when rejected

    # ── Disease prediction fields (empty/None when rejected) ─────────────────
    id: Optional[int] = None
    crop: str = ""
    disease: str = ""
    class_key: str = ""
    is_healthy: bool = False
    confidence: float = 0.0
    severity: str = ""
    pathogen_type: str = ""
    description: str = ""
    symptoms: List[str] = []
    causes: str = ""
    prevention: List[str] = []
    treatment: TreatmentSchema = Field(default_factory=TreatmentSchema)
    top_candidates: Optional[List[Dict]] = []
    image_filename: Optional[str] = None
    status: str = "Diagnosis Completed"


class DiagnosisHistoryItem(BaseModel):
    id: int
    crop_name: str
    disease_name: str
    class_key: str
    is_healthy: bool
    confidence: float
    severity: str
    created_at: Optional[str] = None
    image_filename: Optional[str] = None


class DiagnosisHistoryResponse(BaseModel):
    total: int
    history: List[DiagnosisHistoryItem]
