from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database.database import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)

    crop = Column(String)

    pest_name = Column(String)

    location = Column(String)

    risk_level = Column(String)

    confidence = Column(Float)

    pest_value = Column(Float)

    prediction_date = Column(DateTime, default=datetime.utcnow) 