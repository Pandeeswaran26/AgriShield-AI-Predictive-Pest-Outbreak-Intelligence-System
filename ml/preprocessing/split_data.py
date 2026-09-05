import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import RANDOM_STATE, TARGET_COLUMN


def time_aware_split(df: pd.DataFrame, train_ratio: float = 0.8):
    """
    Performs a time-aware temporal holdout split based on Observation Year
    to prevent future-leakage into training sets.
    """
    X = df.drop(columns=[TARGET_COLUMN], errors="ignore")
    y = df[TARGET_COLUMN]

    if "Observation Year" in X.columns:
        unique_years = sorted(X["Observation Year"].dropna().unique())
        if len(unique_years) > 1:
            cutoff_idx = int(np.floor(len(unique_years) * train_ratio))
            cutoff_year = unique_years[cutoff_idx]
            train_mask = X["Observation Year"] <= cutoff_year
            test_mask = X["Observation Year"] > cutoff_year
            return X.loc[train_mask], X.loc[test_mask], y.loc[train_mask], y.loc[test_mask]

    return train_test_split(X, y, test_size=1.0 - train_ratio, random_state=RANDOM_STATE)


if __name__ == "__main__":
    from load_data import load_master_features
    df = load_master_features()
    X_train, X_test, y_train, y_test = time_aware_split(df)
    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
