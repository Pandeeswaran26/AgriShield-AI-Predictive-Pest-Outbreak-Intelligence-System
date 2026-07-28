import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

INPUT_PATH = "datasets/processed/book2_clean.csv"
OUTPUT_PATH = "datasets/processed"

# Load cleaned dataset
df = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("Original Shape:", df.shape)

# Encode categorical columns
label_encoders = {}

categorical_columns = [
    "Pest/Disease",
    "Location"
]

for col in categorical_columns:
    encoder = LabelEncoder()
    df[col] = encoder.fit_transform(df[col].astype(str))
    label_encoders[col] = encoder

# Create Season feature from Standard Week
def get_season(week):
    if week <= 13:
        return "Winter"
    elif week <= 26:
        return "Summer"
    elif week <= 39:
        return "Monsoon"
    else:
        return "PostMonsoon"

df["Season"] = df["Standard Week"].apply(get_season)

season_encoder = LabelEncoder()
df["Season"] = season_encoder.fit_transform(df["Season"])

# Save processed dataset
output_file = os.path.join(OUTPUT_PATH, "book2_features.csv")
df.to_csv(output_file, index=False)

print("Feature Engineering Completed!")
print("New Shape:", df.shape)
print("Saved:", output_file)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 Rows:")
print(df.head())