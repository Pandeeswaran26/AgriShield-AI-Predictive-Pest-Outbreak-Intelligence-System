import shap
import pandas as pd

from app.model_loader import model


explainer = shap.TreeExplainer(model)


def explain_prediction(input_data: dict):

    df = pd.DataFrame([input_data])

    shap_values = explainer.shap_values(df)

    feature_importance = []

    values = shap_values[0] if isinstance(shap_values, list) else shap_values

    for feature, value in zip(df.columns, values[0]):
        feature_importance.append({
            "feature": feature,
            "impact": float(value)
        })

    feature_importance.sort(
        key=lambda x: abs(x["impact"]),
        reverse=True
    )

    return feature_importance