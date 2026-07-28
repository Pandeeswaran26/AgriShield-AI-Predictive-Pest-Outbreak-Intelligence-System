from fastapi import APIRouter

from .service import explain_prediction

router = APIRouter(
    prefix="/predict",
    tags=["Explainable AI"]
)


@router.get("/{prediction_id}/explain")
def explain(prediction_id: int):

    # Replace this later with actual prediction data from DB
    sample = {
        "Temperature": 31,
        "Humidity": 78,
        "Rainfall": 110,
        "Soil_Moisture": 42,
        "Crop_Stress_Indicator": 0.62
    }

    return {
        "prediction_id": prediction_id,
        "explanation": explain_prediction(sample)
    }