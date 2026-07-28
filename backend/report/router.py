from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .service import generate_prediction_report

router = APIRouter(
    prefix="/predict",
    tags=["Prediction Report"]
)


@router.get("/{prediction_id}/report")
def prediction_report(prediction_id: int):

    pdf = generate_prediction_report(prediction_id)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=prediction_{prediction_id}.pdf"
        }
    )