import pandas as pd
import os

RAW_PATH = "datasets/raw"
OUTPUT_PATH = "datasets/processed"

os.makedirs(OUTPUT_PATH, exist_ok=True)

# Load dataset
df = pd.read_csv(os.path.join(RAW_PATH, "Book2.csv"))

print("=" * 60)
print("Original Shape:", df.shape)

# Remove duplicate rows
df = df.drop_duplicates()

# Remove rows where Pest Value is missing
df = df.dropna(subset=["Pest Value"])

print("After Cleaning:", df.shape)

# Save cleaned dataset
df.to_csv(
    os.path.join(OUTPUT_PATH, "book2_clean.csv"),
    index=False
)

print("Saved Successfully!")