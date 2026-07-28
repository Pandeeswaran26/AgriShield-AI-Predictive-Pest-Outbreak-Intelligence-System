from sqlalchemy.orm import Session

from .models import PredictionHistory


def get_all_predictions(db: Session):
    return (
        db.query(PredictionHistory)
        .order_by(PredictionHistory.prediction_date.desc())
        .all()
    )


def delete_prediction(db: Session, prediction_id: int):
    prediction = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.id == prediction_id)
        .first()
    )

    if prediction:
        db.delete(prediction)
        db.commit()

    return prediction