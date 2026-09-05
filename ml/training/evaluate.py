import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error,
)


def evaluate_regression(y_true, y_pred, prefix=""):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    r2 = r2_score(y_true, y_pred)
    
    # Avoid zero division in MAPE
    mask = y_true > 0
    mape = (
        mean_absolute_percentage_error(y_true[mask], y_pred[mask])
        if mask.any()
        else 0.0
    )

    metrics = {
        f"{prefix}mae": float(mae),
        f"{prefix}rmse": float(rmse),
        f"{prefix}r2": float(r2),
        f"{prefix}mape": float(mape),
    }

    return metrics


def print_metrics(metrics: dict, title: str = "Evaluation Metrics"):
    print(f"\n{'='*40}")
    print(f" {title}")
    print(f"{'='*40}")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f" • {k.upper():<12}: {v:.4f}")
        else:
            print(f" • {k.upper():<12}: {v}")
    print(f"{'='*40}\n")
