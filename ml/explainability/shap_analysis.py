import os
import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Create output folder
# ----------------------------
os.makedirs("outputs/shap", exist_ok=True)

# ----------------------------
# Load dataset
# ----------------------------
df = pd.read_csv("datasets/processed/master_dataset_features.csv")

# ----------------------------
# Load label encoders
# ----------------------------
encoders = joblib.load("ml/models/label_encoders.pkl")

categorical_columns = [
    "Crop",
    "Pest_Name",
    "Location",
    "Rainfall_Category"
]

for col in categorical_columns:
    df[col] = encoders[col].transform(df[col].astype(str))

# ----------------------------
# Features
# ----------------------------
X = df.drop(columns=["Pest Value"])

# ----------------------------
# Load trained model
# ----------------------------
model = joblib.load("ml/models/final_pest_prediction_model.pkl")

print("Model Loaded Successfully!")

# ----------------------------
# SHAP Explainer
# ----------------------------
explainer = shap.TreeExplainer(model)

# Use a sample for faster visualization
sample = X.sample(min(500, len(X)), random_state=42)

shap_values = explainer.shap_values(sample)

print("SHAP Values Calculated!")

# ----------------------------
# Summary Plot
# ----------------------------
plt.figure()

shap.summary_plot(
    shap_values,
    sample,
    show=False
)

plt.tight_layout()

plt.savefig(
    "outputs/shap/shap_summary.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ----------------------------
# Bar Plot
# ----------------------------
plt.figure()

shap.summary_plot(
    shap_values,
    sample,
    plot_type="bar",
    show=False
)

plt.tight_layout()

plt.savefig(
    "outputs/shap/feature_importance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nExplainability Images Saved Successfully!")

print("\nSaved Files:")
print("outputs/shap/shap_summary.png")
print("outputs/shap/feature_importance.png")