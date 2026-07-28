import os
import pandas as pd
import numpy as np

# Load master dataset
df = pd.read_csv("datasets/processed/master_dataset.csv")

print("Original Shape:", df.shape)

# ============================
# Feature Engineering
# ============================

# Temperature Difference
df["Temp_Diff"] = df["MaxT"] - df["MinT"]

# Average Humidity
df["Avg_Humidity"] = (df["RH1(%)"] + df["RH2(%)"]) / 2

# Week Cyclic Encoding
df["Week_Sin"] = np.sin(2 * np.pi * df["Standard Week"] / 52)
df["Week_Cos"] = np.cos(2 * np.pi * df["Standard Week"] / 52)

# Weather Index
df["Weather_Index"] = (
    df["MaxT"]
    + df["RH1(%)"]
    + df["RH2(%)"]
    + df["RF(mm)"]
    + df["WS(kmph)"]
)

# Rainfall Category
df["Rainfall_Category"] = pd.cut(
    df["RF(mm)"],
    bins=[-1, 10, 50, 10000],
    labels=["Low", "Medium", "High"]
)

# ============================
# Save
# ============================

os.makedirs("datasets/processed", exist_ok=True)

output_path = "datasets/processed/master_dataset_features.csv"

df.to_csv(output_path, index=False)

print("\nFeature Engineering Completed!")
print("New Shape:", df.shape)
print("Saved:", output_path)
print("\nColumns:")
print(df.columns.tolist())