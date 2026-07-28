from sqlalchemy.orm import Session


def get_recommendation(prediction_id: int, db: Session):

    return {
        "suggestedActions": [
            "Inspect the field within 48 hours",
            "Install pheromone traps",
            "Monitor pest activity every 2 days"
        ],
        "prevention": [
            "Maintain proper field sanitation",
            "Avoid excess nitrogen fertilizer",
            "Use crop rotation"
        ],
        "recommendedPesticides": [
            "Imidacloprid 17.8% SL",
            "Thiamethoxam 25% WG"
        ],
        "organicAlternatives": [
            "Neem Oil Spray (2%)",
            "Release Ladybird Beetles",
            "Garlic-Chili Extract Spray"
        ],
        "expectedYieldImpact": 12.5
    }