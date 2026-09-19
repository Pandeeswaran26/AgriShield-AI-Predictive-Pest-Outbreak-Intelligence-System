from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.database import get_db
from auth.service import decode_token, is_token_revoked, get_user_by_email

from .schemas import HistoryResponse
from .service import get_all_predictions, delete_prediction

import io
import csv

router = APIRouter(
    prefix="/history",
    tags=["Prediction History"]
)


def _get_user_id(db: Session, authorization: Optional[str] = None) -> Optional[int]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    if not token or is_token_revoked(db, token):
        return None
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email:
            user = get_user_by_email(db, email)
            return user.id if user else None
    except Exception:
        return None
    return None


@router.get("", response_model=HistoryResponse)
@router.get("/", response_model=HistoryResponse)
def history(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    user_id = _get_user_id(db, authorization)
    items = get_all_predictions(db, user_id=user_id)

    return {
        "items": items,
        "total": len(items)
    }


@router.delete("/{prediction_id}")
def remove_prediction(
    prediction_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    user_id = _get_user_id(db, authorization)
    prediction = delete_prediction(db, prediction_id, user_id=user_id)

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="Prediction not found or permission denied"
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