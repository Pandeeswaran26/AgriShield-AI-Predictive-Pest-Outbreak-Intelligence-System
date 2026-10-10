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

    # Decision Engine & Assessment Linkage
    diagnosis_id = Column(Integer, nullable=True)
    health_status = Column(String, nullable=True)
    data_sources_json = Column(Text, nullable=True)

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


# ---------------------------------------------------------------------------
# Farmer Action Feedback Loop
# ---------------------------------------------------------------------------

class FarmerAction(Base):
    """Records the farmer's response to a recommendation — what they actually did."""
    __tablename__ = "farmer_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    plant_id = Column(Integer, nullable=True, index=True)
    prediction_id = Column(Integer, nullable=True, index=True)

    action_type = Column(String, nullable=False)  # Irrigation | Fertilizer | Chemical Spray | Biological Treatment | Scouting | No Action
    description = Column(Text, nullable=True)     # Free-text notes on what was applied / done
    product_used = Column(String, nullable=True)  # Herbicide / fertilizer brand, dose
    dosage = Column(String, nullable=True)        # e.g. "2 L/acre"

    performed_at = Column(DateTime, nullable=True)  # When the action was taken
    created_at = Column(DateTime, default=utc_now)


class FollowUpOutcome(Base):
    """Records the observed crop condition after a farmer action."""
    __tablename__ = "follow_up_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    farmer_action_id = Column(Integer, nullable=False, index=True)
    plant_id = Column(Integer, nullable=True, index=True)

    days_after_action = Column(Integer, nullable=True)  # How many days since the action

    observed_condition = Column(String, nullable=False)  # Improved | Stable | Worsened | Pest Eradicated | Recurrence
    severity_change = Column(String, nullable=True)       # Better | Same | Worse
    notes = Column(Text, nullable=True)                   # Detailed field observations

    recorded_at = Column(DateTime, default=utc_now)


class ModelVersionRecord(Base):
    """Tracks trained model versions and their benchmark metrics for the monitoring dashboard."""
    __tablename__ = "model_version_records"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)          # e.g. ExtraTrees, XGBoost
    version = Column(String, nullable=False)             # e.g. 2.1.0
    feature_schema = Column(String, nullable=True)       # e.g. FS-3

    # Regression metrics
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    r2 = Column(Float, nullable=True)

    # Classification metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)

    # Calibration
    brier_score = Column(Float, nullable=True)

    benchmark_report_json = Column(Text, nullable=True)  # Full JSON from model_benchmark.py
    trained_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False)           # True for the currently deployed model

    created_at = Column(DateTime, default=utc_now)