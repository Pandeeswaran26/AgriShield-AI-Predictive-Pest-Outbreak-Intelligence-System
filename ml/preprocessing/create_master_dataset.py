import os
import pandas as pd

# File paths
book2_path = "datasets/raw/Book2.csv"
rice_path = "datasets/raw/RICE.csv"

# Load datasets
book2 = pd.read_csv(book2_path)
rice = pd.read_csv(rice_path)

# Remove rows with missing target values
book2 = book2.dropna(subset=["Pest Value"])
rice = rice.dropna(subset=["Pest Value"])

# Rename columns to match
book2.rename(columns={
    "MaxT(°C)": "MaxT",
    "MinT(°C)": "MinT",
    "Pest/Disease": "Pest_Name"
}, inplace=True)

rice.rename(columns={
    "PEST NAME": "Pest_Name"
}, inplace=True)

# Remove column only present in RICE
if "Collection Type" in rice.columns:
    rice.drop(columns=["Collection Type"], inplace=True)

# Add crop names
book2["Crop"] = "Cotton"
rice["Crop"] = "Rice"

# Arrange columns
columns = [
    "Crop",
    "Observation Year",
    "Standard Week",
    "Pest_Name",
    "Location",
    "MaxT",
    "MinT",
    "RH1(%)",
    "RH2(%)",
    "RF(mm)",
    "WS(kmph)",
    "SSH(hrs)",
    "EVP(mm)",
    "Pest Value"
]

book2 = book2[columns]
rice = rice[columns]

# Merge
master = pd.concat([book2, rice], ignore_index=True)

# Remove duplicates
master = master.drop_duplicates()

# Create processed folder if needed
os.makedirs("datasets/processed", exist_ok=True)

# Save file
master.to_csv("datasets/processed/master_dataset.csv", index=False)

print("✅ Master dataset created successfully!")
print(master.shape)