from pathlib import Path
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

# Load a backend-level.env file even when the API is started from the repo root.
load_dotenv(dotenv_path=BASE_DIR / ".env")
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    sqlite_path = BASE_DIR / "agrishield.db"
    DATABASE_URL = f"sqlite:///{sqlite_path}"
    print(f"DATABASE_URL not set; using local SQLite fallback: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

from sqlalchemy import inspect, text


def ensure_migrations(target_engine):
    try:
        inspector = inspect(target_engine)
        table_names = inspector.get_table_names()

        # Migrate prediction_history
        if "prediction_history" in table_names:
            existing_cols = {col["name"] for col in inspector.get_columns("prediction_history")}
            columns_to_add = [
                ("user_id", "INTEGER"),
                ("location_display", "VARCHAR"),
                ("confidence", "FLOAT"),
                ("latitude", "FLOAT"),
                ("longitude", "FLOAT"),
                ("plant_id", "INTEGER"),
                ("plant_name", "VARCHAR"),
                ("crop_variety", "VARCHAR"),
                ("growth_stage", "VARCHAR"),
                ("field_name", "VARCHAR"),
                ("field_size", "FLOAT"),
                ("soil_type", "VARCHAR"),
                ("soil_moisture", "FLOAT"),
                ("soil_ph", "FLOAT"),
                ("auto_mode", "BOOLEAN DEFAULT FALSE"),
                ("pests_json", "TEXT"),
                ("forecast_json", "TEXT"),
                ("advisory_json", "TEXT"),
                ("diagnosis_id", "INTEGER"),
                ("health_status", "VARCHAR"),
                ("data_sources_json", "TEXT"),
                ("observation_year", "INTEGER"),
                ("standard_week", "INTEGER"),
                ("max_t", "FLOAT"),
                ("min_t", "FLOAT"),
                ("rh1", "FLOAT"),
                ("rh2", "FLOAT"),
                ("rf", "FLOAT"),
                ("ws", "FLOAT"),
                ("ssh", "FLOAT"),
                ("evp", "FLOAT"),
                ("prediction_date", "TIMESTAMP" if not DATABASE_URL.startswith("sqlite") else "DATETIME"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in columns_to_add:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE prediction_history ADD COLUMN {col_name} {col_type}"))
                conn.commit()

        # Migrate plants table
        if "plants" in table_names:
            existing_plant_cols = {col["name"] for col in inspector.get_columns("plants")}
            plant_cols_to_add = [
                ("irrigation_method", "VARCHAR"),
                ("field_position", "VARCHAR"),
                ("irrigation_frequency", "VARCHAR"),
                ("irrigation_hours", "FLOAT"),
                ("auto_irrigation_alerts", "BOOLEAN DEFAULT TRUE"),
                ("soil_n", "FLOAT"),
                ("soil_p", "FLOAT"),
                ("soil_k", "FLOAT"),
                ("last_assessment_date", "TIMESTAMP" if not DATABASE_URL.startswith("sqlite") else "DATETIME"),
                ("last_health_status", "VARCHAR"),
                ("last_risk_level", "VARCHAR"),
                ("last_recommended_action", "VARCHAR"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in plant_cols_to_add:
                    if col_name not in existing_plant_cols:
                        conn.execute(text(f"ALTER TABLE plants ADD COLUMN {col_name} {col_type}"))
                conn.commit()
        # Migrate irrigation_history table
        if "irrigation_history" in table_names:
            existing_irr_cols = {col["name"] for col in inspector.get_columns("irrigation_history")}
            irr_cols_to_add = [
                ("user_id",              "INTEGER"),
                ("plant_id",             "INTEGER"),
                ("plant_name",           "VARCHAR"),
                ("crop_type",            "VARCHAR"),
                ("field_position",       "VARCHAR"),
                ("irrigation_needed",    "BOOLEAN DEFAULT TRUE"),
                ("irrigation_frequency", "VARCHAR"),
                ("irrigation_hours",     "FLOAT"),
                ("water_quantity",       "VARCHAR"),
                ("timing_advice",        "VARCHAR"),
                ("soil_moisture",        "FLOAT"),
                ("soil_temperature",     "FLOAT"),
                ("temperature",          "FLOAT"),
                ("humidity",             "FLOAT"),
                ("rainfall",             "FLOAT"),
                ("risk_level",           "VARCHAR"),
                ("water_stress",         "VARCHAR"),
                ("probability",          "FLOAT"),
                ("dispatch_type",        "VARCHAR DEFAULT 'manual'"),
                ("email_sent",           "BOOLEAN DEFAULT FALSE"),
                ("email_recipient",      "VARCHAR"),
                ("advisory_notes",       "TEXT"),
                ("recorded_at",          "DATETIME"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in irr_cols_to_add:
                    if col_name not in existing_irr_cols:
                        conn.execute(text(f"ALTER TABLE irrigation_history ADD COLUMN {col_name} {col_type}"))
                conn.commit()

        # Migrate users table
        if "users" in table_names:
            existing_user_cols = {col["name"] for col in inspector.get_columns("users")}
            user_cols_to_add = [
                ("phone", "VARCHAR"),
                ("location", "VARCHAR"),
                ("is_verified", "BOOLEAN DEFAULT FALSE"),
            ]
            with target_engine.connect() as conn:
                for col_name, col_type in user_cols_to_add:
                    if col_name not in existing_user_cols:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                if "phone_number" in existing_user_cols and not DATABASE_URL.startswith("sqlite"):
                    try:
                        conn.execute(text("ALTER TABLE users ALTER COLUMN phone_number DROP NOT NULL"))
                    except Exception:
                        pass
                conn.commit()
    except Exception as exc:
        print(f"Non-fatal migration notice: {exc}")


ensure_migrations(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()