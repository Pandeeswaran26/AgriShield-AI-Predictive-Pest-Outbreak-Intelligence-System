from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.database import get_db
from .service import generate_prediction_report

router = APIRouter(
    prefix="/predict",
    tags=["Prediction Report"]
)


@router.get("/{prediction_id}/report")
def prediction_report(prediction_id: int, db: Session = Depends(get_db)):
    try:
        pdf = generate_prediction_report(db, prediction_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err))

    if pdf is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=prediction_{prediction_id}.pdf"
        }
    )