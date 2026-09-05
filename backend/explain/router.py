from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from .service import explain_prediction

router = APIRouter(
    prefix="/predict",
    tags=["Explainable AI"]
)


@router.get("/{prediction_id}/explain")
def explain(prediction_id: int, db: Session = Depends(get_db)):
    result = explain_prediction(db, prediction_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return {
        "prediction_id": prediction_id,
        "explanation": result
    }