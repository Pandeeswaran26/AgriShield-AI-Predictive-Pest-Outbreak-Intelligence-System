import joblib
import pandas as pd
import matplotlib.pyplot as plt

# Load model
model = joblib.load("ml/models/pest_prediction_model.pkl")

# Load data
df = pd.read_csv("datasets/processed/book2_features.csv")

X = df.drop(columns=["Pest Value"])

# Feature importance
importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print(importance)

# Plot
plt.figure(figsize=(10,6))
plt.barh(
    importance["Feature"],
    importance["Importance"]
)
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance")
plt.tight_layout()

plt.savefig("docs/feature_importance.png")
plt.show()