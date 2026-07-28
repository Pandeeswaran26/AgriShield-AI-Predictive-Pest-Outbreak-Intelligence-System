def calculate_risk(prediction: float) -> str:
    """
    Convert the predicted pest value into a risk level.
    """

    if prediction < 20:
        return "Low"
    elif prediction < 50:
        return "Medium"
    else:
        return "High"