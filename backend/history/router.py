from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.database import get_db

from .schemas import HistoryResponse
from .service import get_all_predictions, delete_prediction

import io
import csv

router = APIRouter(
    prefix="/history",
    tags=["Prediction History"]
)


@router.get("", response_model=HistoryResponse)
def history(db: Session = Depends(get_db)):

    items = get_all_predictions(db)

    return {
        "items": items,
        "total": len(items)
    }


@router.delete("/{prediction_id}")
def remove_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):

    prediction = delete_prediction(db, prediction_id)

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="Prediction not found"
        )

    return {
        "message": "Prediction deleted successfully"
    }


@router.get("/export")
def export_history(db: Session = Depends(get_db)):

    rows = get_all_predictions(db)

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Crop",
        "Pest",
        "Location",
        "Risk",
        "Confidence",
        "Pest Value",
        "Date"
    ])

    for row in rows:
        writer.writerow([
            row.crop,
            row.pest_name,
            row.location,
            row.risk_level,
            row.confidence,
            row.pest_value,
            row.prediction_date
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=prediction_history.csv"
        }
    )