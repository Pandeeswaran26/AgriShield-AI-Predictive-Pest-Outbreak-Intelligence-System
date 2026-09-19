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
                ("plant_id", "INTEGER"),
                ("plant_name", "VARCHAR"),
                ("crop_variety", "VARCHAR"),
                ("growth_stage", "VARCHAR"),
                ("field_name", "VARCHAR"),
                ("field_size", "FLOAT"),
                ("soil_type", "VARCHAR"),
                ("soil_moisture", "FLOAT"),
                ("soil_ph", "FLOAT"),
                ("diagnosis_id", "INTEGER"),
                ("health_status", "VARCHAR"),
                ("data_sources_json", "TEXT"),
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
    except Exception as exc:
        print(f"Non-fatal migration notice: {exc}")


ensure_migrations(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()