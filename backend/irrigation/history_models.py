"""
Irrigation History Model
AgriShield AI Platform
========================
Tracks every irrigation event (manual or auto-scheduled) per plant.
Supports daily morning + evening automated scheduling.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from database.database import Base


class IrrigationHistory(Base):
    __tablename__ = "irrigation_history"

    id                   = Column(Integer, primary_key=True, index=True)
    user_id              = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    plant_id             = Column(Integer, ForeignKey("plants.id"), nullable=True, index=True)

    # Plant / Crop identification
    plant_name           = Column(String, nullable=False, default="Unknown Plant")
    crop_type            = Column(String, nullable=False, default="Rice")
    field_position       = Column(String, nullable=True, default="Primary Field Zone")

    # Irrigation details
    irrigation_needed    = Column(Boolean, default=True)
    irrigation_frequency = Column(String, nullable=True)   # e.g. "2 times daily"
    irrigation_hours     = Column(Float, nullable=True)    # e.g. 2.5 hours
    water_quantity       = Column(String, nullable=True)   # e.g. "40–60 mm depth"
    timing_advice        = Column(String, nullable=True)

    # Soil / weather snapshot
    soil_moisture        = Column(Float, nullable=True)
    soil_temperature     = Column(Float, nullable=True)
    temperature          = Column(Float, nullable=True)
    humidity             = Column(Float, nullable=True)
    rainfall             = Column(Float, nullable=True)

    # Risk info
    risk_level           = Column(String, nullable=True)   # High / Medium / Low
    water_stress         = Column(String, nullable=True)   # Severe / Moderate / Optimal / Waterlogged
    probability          = Column(Float, nullable=True)

    # Dispatch context
    dispatch_type        = Column(String, default="manual")   # manual | morning_schedule | evening_schedule | threshold
    email_sent           = Column(Boolean, default=False)
    email_recipient      = Column(String, nullable=True)
    advisory_notes       = Column(Text, nullable=True)   # JSON-encoded list

    # Timestamp
    recorded_at          = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return (
            f"<IrrigationHistory id={self.id} plant='{self.plant_name}' "
            f"crop='{self.crop_type}' dispatch='{self.dispatch_type}' "
            f"at={self.recorded_at}>"
        )
