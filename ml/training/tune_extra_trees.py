import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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
# Train/Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------
# Hyperparameter Grid
# -----------------------------
param_grid = {
    "n_estimators": [100, 200, 300, 500],
    "max_depth": [None, 10, 20, 30, 40],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2", None]
}

# -----------------------------
# Base Model
# -----------------------------
model = ExtraTreesRegressor(random_state=42)

# -----------------------------
# Random Search
# -----------------------------
search = RandomizedSearchCV(
    estimator=model,
    param_distributions=param_grid,
    n_iter=20,
    cv=5,
    scoring="r2",
    random_state=42,
    n_jobs=-1
)

print("Searching for best parameters...\n")

search.fit(X_train, y_train)

best_model = search.best_estimator_

print("Best Parameters:")
print(search.best_params_)

# -----------------------------
# Evaluate
# -----------------------------
y_pred = best_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("\nModel Performance")
print(f"MAE  : {mae:.3f}")
print(f"RMSE : {rmse:.3f}")
print(f"R²   : {r2:.3f}")

# -----------------------------
# Save Model
# -----------------------------
joblib.dump(best_model, "ml/models/best_extra_trees.pkl")

print("\nBest model saved successfully!")