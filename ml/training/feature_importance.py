import sys
from pathlib import Path
import joblib
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import FINAL_MODEL_PATH, MASTER_FEATURES_PATH, TARGET_COLUMN, OUTPUTS_DIR

# Load model
model = joblib.load(FINAL_MODEL_PATH)

# Load data
df = pd.read_csv(MASTER_FEATURES_PATH)
X = df.drop(columns=[TARGET_COLUMN], errors="ignore")

# Feature importance
importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(by="Importance", ascending=True)

print("\nFeature Importance Rankings:")
print("----------------------------")
print(importance.sort_values(by="Importance", ascending=False))

# Plot
plt.figure(figsize=(10, 6))
plt.barh(importance["Feature"], importance["Importance"], color="#166534")
plt.xlabel("Gini Importance")
plt.ylabel("Feature")
plt.title("AgriShield AI - ExtraTrees Feature Importance")
plt.tight_layout()

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
plot_path = OUTPUTS_DIR / "feature_importance.png"
plt.savefig(plot_path, dpi=300)
plt.close()

print(f"\nFeature importance plot saved successfully to: {plot_path}")