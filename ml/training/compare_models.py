import pandas as pd
import time

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Machine Learning Models
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor
)

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("datasets/processed/book2_features.csv")

# -----------------------------
# Features and Target
# -----------------------------
X = df.drop("Pest Value", axis=1)
y = df["Pest Value"]

# -----------------------------
# Train Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------
# Models
# -----------------------------
models = {
    "Random Forest": RandomForestRegressor(random_state=42),

    "Extra Trees": ExtraTreesRegressor(random_state=42),

    "Gradient Boosting": GradientBoostingRegressor(random_state=42),

    "XGBoost": XGBRegressor(
        random_state=42,
        objective="reg:squarederror"
    ),

    "LightGBM": LGBMRegressor(random_state=42),

    "CatBoost": CatBoostRegressor(
        verbose=0,
        random_state=42
    )
}

results = []

print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

# -----------------------------
# Train Every Model
# -----------------------------
for name, model in models.items():

    print(f"\nTraining {name}...")

    start = time.time()

    model.fit(X_train, y_train)

    end = time.time()

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)

    rmse = mean_squared_error(
        y_test,
        y_pred
    ) ** 0.5

    r2 = r2_score(y_test, y_pred)

    training_time = round(end - start, 2)

    results.append({
        "Model": name,
        "MAE": round(mae, 3),
        "RMSE": round(rmse, 3),
        "R2": round(r2, 3),
        "Training Time (sec)": training_time
    })

# -----------------------------
# Display Results
# -----------------------------
results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="R2",
    ascending=False
)

print("\n")
print(results_df)

# -----------------------------
# Save Results
# -----------------------------
results_df.to_csv(
    "ml/reports/model_comparison.csv",
    index=False
)

print("\nComparison report saved successfully!")