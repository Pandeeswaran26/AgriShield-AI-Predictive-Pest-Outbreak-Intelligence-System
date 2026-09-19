from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from database.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class PlantDiagnosisRecord(Base):
    __tablename__ = "plant_diagnosis_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    crop_name = Column(String(100), nullable=False, index=True)
    disease_name = Column(String(150), nullable=False)
    class_key = Column(String(150), nullable=False)
    is_healthy = Column(Boolean, default=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(50), default="Medium")

    image_filename = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    symptoms_json = Column(Text, nullable=True)
    treatments_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now)

    def to_dict(self):
        symptoms = []
        if self.symptoms_json:
            try:
                symptoms = json.loads(self.symptoms_json)
            except Exception:
                symptoms = [self.symptoms_json]

        treatments = {}
        if self.treatments_json:
            try:
                treatments = json.loads(self.treatments_json)
            except Exception:
                treatments = {"general": [self.treatments_json]}

        return {
            "id": self.id,
            "user_id": self.user_id,
            "crop_name": self.crop_name,
            "disease_name": self.disease_name,
            "class_key": self.class_key,
            "is_healthy": self.is_healthy,
            "confidence": round(self.confidence, 1),
            "severity": self.severity,
            "image_filename": self.image_filename,
            "description": self.description,
            "symptoms": symptoms,
            "treatments": treatments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
