import pandas as pd

from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import cross_val_score

# Load Dataset
df = pd.read_csv("datasets/processed/book2_features.csv")

X = df.drop("Pest Value", axis=1)
y = df["Pest Value"]

# Model
model = ExtraTreesRegressor(random_state=42)

# 5-Fold Cross Validation
scores = cross_val_score(
    model,
    X,
    y,
    cv=5,
    scoring="r2"
)

print("\nCross Validation Results")
print("-------------------------")

for i, score in enumerate(scores, start=1):
    print(f"Fold {i}: {score:.3f}")

print("\nAverage R²:", round(scores.mean(), 3))
print("Standard Deviation:", round(scores.std(), 3))