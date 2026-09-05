from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text

from database.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)

    crop = Column(String)
    pest_name = Column(String)  # top pest (for backward compat)
    location = Column(String)   # nearest training location name
    location_display = Column(String, nullable=True)  # real GPS city name
    risk_level = Column(String)
    confidence = Column(Float, nullable=True)
    pest_value = Column(Float)

    # GPS coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Dynamic Plant & Field Context
    plant_id = Column(Integer, nullable=True, index=True)
    plant_name = Column(String, nullable=True)
    crop_variety = Column(String, nullable=True)
    growth_stage = Column(String, nullable=True)
    field_name = Column(String, nullable=True)
    field_size = Column(Float, nullable=True)
    soil_type = Column(String, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    soil_ph = Column(Float, nullable=True)

    # Auto-mode flag (True when farmer only picked crop, GPS+weather auto-collected)
    auto_mode = Column(Boolean, nullable=True, default=False)

    # Multi-pest predictions as JSON string: [{pest_name, pest_value, risk_level, rank}, ...]
    pests_json = Column(Text, nullable=True)

    # 7-day forecast risk as JSON string: [{date, max_t, rf, rh1, rh2, ws, ssh, evp, top_pest, risk_level}, ...]
    forecast_json = Column(Text, nullable=True)

    # Smart advisory as JSON string: {irrigation, fertilizer, pest_management, urgency}
    advisory_json = Column(Text, nullable=True)

    # Raw inputs — stored so /explain and /report can rebuild the
    # exact feature vector used for this prediction later.
    observation_year = Column(Integer, nullable=True)
    standard_week = Column(Integer, nullable=True)
    max_t = Column(Float, nullable=True)
    min_t = Column(Float, nullable=True)
    rh1 = Column(Float, nullable=True)
    rh2 = Column(Float, nullable=True)
    rf = Column(Float, nullable=True)
    ws = Column(Float, nullable=True)
    ssh = Column(Float, nullable=True)
    evp = Column(Float, nullable=True)

    prediction_date = Column(DateTime, default=utc_now)