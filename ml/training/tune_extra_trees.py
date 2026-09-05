import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MASTER_FEATURES_PATH, TARGET_COLUMN, CATEGORICAL_COLUMNS, MODELS_DIR, RANDOM_STATE

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv(MASTER_FEATURES_PATH)

# Encode categorical variables
for col in CATEGORICAL_COLUMNS:
    if col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

# Features and log-transformed clipped Target
y = np.log1p(df[TARGET_COLUMN].clip(lower=0, upper=df[TARGET_COLUMN].quantile(0.99)))
X = df.drop(columns=[TARGET_COLUMN], errors="ignore")

# -----------------------------
# Train/Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

# -----------------------------
# Hyperparameter Grid
# -----------------------------
param_grid = {
    "n_estimators": [100, 200, 250, 350],
    "max_depth": [None, 15, 25, 35],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2", 1.0],
}

# -----------------------------
# Random Search
# -----------------------------
base_model = ExtraTreesRegressor(random_state=RANDOM_STATE, n_jobs=-1)

search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_grid,
    n_iter=15,
    cv=3,
    scoring="r2",
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbose=1,
)

print("Searching for optimal ExtraTrees hyperparameters...\n")
search.fit(X_train, y_train)

best_model = search.best_estimator_
print("\nOptimal Hyperparameters Found:")
print(search.best_params_)

# -----------------------------
# Evaluation on Original Scale
# -----------------------------
y_pred_log = best_model.predict(X_test)
y_pred = np.expm1(y_pred_log)
y_test_orig = np.expm1(y_test)

mae = mean_absolute_error(y_test_orig, y_pred)
rmse = mean_squared_error(y_test_orig, y_pred) ** 0.5
r2 = r2_score(y_test_orig, y_pred)

print("\nModel Performance on Test Set:")
print(f" • MAE  : {mae:.3f}")
print(f" • RMSE : {rmse:.3f}")
print(f" • R²   : {r2:.3f}")

# -----------------------------
# Save Best Model
# -----------------------------
save_path = MODELS_DIR / "best_extra_trees.pkl"
joblib.dump(best_model, save_path)
print(f"\nTuned model saved to: {save_path}")