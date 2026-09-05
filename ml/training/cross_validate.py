import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MASTER_FEATURES_PATH, TARGET_COLUMN, CATEGORICAL_COLUMNS, RANDOM_STATE

# Load Dataset
df = pd.read_csv(MASTER_FEATURES_PATH)

# Target clipping & log1p
y = np.log1p(df[TARGET_COLUMN].clip(lower=0, upper=df[TARGET_COLUMN].quantile(0.99)))
X = df.drop(columns=[TARGET_COLUMN], errors="ignore")

# Encode categorical variables
for col in CATEGORICAL_COLUMNS:
    if col in X.columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

# Model
model = ExtraTreesRegressor(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)

# 5-Fold Cross Validation
print("\nRunning 5-Fold Cross Validation on Master Features...")
scores = cross_val_score(model, X, y, cv=5, scoring="r2")

print("\nCross Validation Results (Log Scale R²)")
print("-----------------------------------------")
for i, score in enumerate(scores, start=1):
    print(f" Fold {i}: {score:.4f}")

print("-----------------------------------------")
print(f" Mean R²: {scores.mean():.4f} (+/- {scores.std():.4f})\n")