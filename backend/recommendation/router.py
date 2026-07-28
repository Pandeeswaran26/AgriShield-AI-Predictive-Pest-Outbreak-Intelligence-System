from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from .service import get_recommendation

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/{prediction_id}")
def recommendation(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    return get_recommendation(prediction_id, db)