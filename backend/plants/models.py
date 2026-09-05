from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from database.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Core Plant Identification
    name = Column(String, nullable=False)                # e.g., "Kaveri Hybrid Rice" or "Bollgard II Cotton"
    crop_type = Column(String, nullable=False)           # "Rice" or "Cotton" (matches ML model base suite)
    variety = Column(String, nullable=True)              # e.g., "IR-64", "RCH-2 Bt", "Basmati 1121"
    planting_date = Column(String, nullable=True)         # ISO Date format "YYYY-MM-DD"
    growth_stage = Column(String, nullable=True)          # e.g., "Seedling", "Vegetative", "Tillering", "Flowering", "Maturity"

    # Field & Agronomic Dimensions
    field_name = Column(String, nullable=True)            # e.g., "North Plot A"
    field_size = Column(Float, nullable=True)             # e.g., 3.5
    field_size_unit = Column(String, default="acres")     # "acres" or "hectares"
    soil_type = Column(String, nullable=True)             # e.g., "Clay Loam", "Black Soil", "Red Sandy Loam"
    soil_moisture = Column(Float, nullable=True)          # e.g., 65.0 (%)
    soil_ph = Column(Float, nullable=True)                # e.g., 6.5 (pH scale)

    # Saved Geolocation for this Field
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String, nullable=True)         # e.g., "Thanjavur, Tamil Nadu"

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
