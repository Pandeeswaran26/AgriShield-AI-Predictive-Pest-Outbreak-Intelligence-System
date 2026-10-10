"""
Multi-Crop Dataset Harmonization and Splitting Script
Crop-Irrigation-AI / AgriSense Platform
=====================================================
Builds data/processed/multi_crop_irrigation.csv from real raw datasets:
1. GCEKIoT 2019-2020 (Paddy/Rice, Groundnut)
2. Smart Farming Sensor Logs 2024 (Maize, Wheat, Cotton, Soybean, Rice)
Generates stratified 70/15/15 train/val/test splits preserving crop class ratios.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
DATA_PROC.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

print("=" * 60)
print("BUILDING MULTI-CROP HARMONIZED DATASET")
print("=" * 60)

# ─── 1. Load GCEKIoT Raw Data ────────────────────────────────────────────────
gcek_path = DATA_RAW / "irrigation_dataset.xlsx"
df_gcek_raw = pd.read_excel(gcek_path, sheet_name="Project datasheet")
df_gcek = df_gcek_raw[[
    "CropType", "CropDays", "Soil Moisture", "Soil Temperature",
    "Temperature", "Humidity", "Irrigation(Y/N)"
]].dropna().copy()

df_gcek["CropDays"] = pd.to_numeric(df_gcek["CropDays"], errors="coerce")
df_gcek = df_gcek.dropna()

gcek_crop_map = {1: "Rice", 2: "Groundnut"}
df_gcek["crop_name"] = df_gcek["CropType"].map(gcek_crop_map)
df_gcek["crop_days"] = df_gcek["CropDays"].astype(float)

# Empirical capacitive sensor calibration: ADC 780 = 10% dry, ADC 100 = 45% saturated
df_gcek["soil_moisture"] = np.clip(
    10.0 + (780.0 - df_gcek["Soil Moisture"].astype(float)) / (780.0 - 100.0) * (45.0 - 10.0),
    10.0, 45.0
).round(2)

df_gcek["soil_temperature"] = df_gcek["Soil Temperature"].astype(float)
df_gcek["temperature"] = df_gcek["Temperature"].astype(float)
df_gcek["humidity"] = df_gcek["Humidity"].astype(float)
df_gcek["rainfall"] = 0.0
df_gcek["irrigation"] = df_gcek["Irrigation(Y/N)"].astype(int)
df_gcek["location"] = "Karad, Western Maharashtra, India"
df_gcek["dataset_source"] = "GCEKIoT-2020"

print(f"GCEKIoT loaded: {len(df_gcek)} rows ({df_gcek['crop_name'].value_counts().to_dict()})")

# ─── 2. Load Smart Farming 2024 Raw Data ─────────────────────────────────────
sf_path = DATA_RAW / "smart_farming_2024.csv"
df_sf_raw = pd.read_csv(sf_path)

df_sf = pd.DataFrame()
df_sf["crop_name"] = df_sf_raw["crop_type"].replace({"Paddy": "Rice"})
df_sf["crop_days"] = df_sf_raw["total_days"].astype(float)
df_sf["soil_moisture"] = df_sf_raw["soil_moisture_%"].astype(float).round(2)
# Topsoil thermal canopy equilibrium: T_soil ~ 0.75 * T_air + 3.0
df_sf["soil_temperature"] = (0.75 * df_sf_raw["temperature_C"] + 3.0).round(1)
df_sf["temperature"] = df_sf_raw["temperature_C"].astype(float).round(1)
df_sf["humidity"] = df_sf_raw["humidity_%"].astype(float).round(1)
df_sf["rainfall"] = df_sf_raw["rainfall_mm"].astype(float).round(1)
# Binary target: None/NaN -> 0, Sprinkler/Drip/Manual -> 1
df_sf["irrigation"] = df_sf_raw["irrigation_type"].notna().astype(int)
df_sf["location"] = df_sf_raw["region"]
df_sf["dataset_source"] = "SmartFarming-IoT-2024"

print(f"SmartFarming-2024 loaded: {len(df_sf)} rows ({df_sf['crop_name'].value_counts().to_dict()})")

# ─── 3. Combine into Master Harmonized Dataset ───────────────────────────────
cols = [
    "crop_name", "crop_days", "soil_moisture", "soil_temperature",
    "temperature", "humidity", "rainfall", "irrigation",
    "location", "dataset_source"
]

master_df = pd.concat([df_gcek[cols], df_sf[cols]], ignore_index=True)

# Crop encoding
CROP_MAPPING = {
    "Cotton": 0,
    "Groundnut": 1,
    "Maize": 2,
    "Rice": 3,
    "Soybean": 4,
    "Wheat": 5,
}

master_df["crop_type"] = master_df["crop_name"].map(CROP_MAPPING)

# Reorder columns with crop_type early
ordered_cols = [
    "crop_name", "crop_type", "crop_days", "soil_moisture", "soil_temperature",
    "temperature", "humidity", "rainfall", "irrigation",
    "location", "dataset_source"
]
master_df = master_df[ordered_cols]

master_csv_path = DATA_PROC / "multi_crop_irrigation.csv"
master_df.to_csv(master_csv_path, index=False)
print(f"\nSaved master dataset to {master_csv_path}")
print(f"Total rows: {len(master_df)}")
print(f"Crop distribution:\n{master_df['crop_name'].value_counts()}")
print(f"Irrigation label distribution:\n{master_df['irrigation'].value_counts()}")

# ─── 4. Stratified 70 / 15 / 15 Train / Val / Test Split ─────────────────────
# Stratify by compound key: crop_name + "_" + irrigation to preserve per-crop class balance
master_df["strat_key"] = master_df["crop_name"] + "_" + master_df["irrigation"].astype(str)

train_df, temp_df = train_test_split(
    master_df,
    test_size=0.30,
    random_state=RANDOM_SEED,
    stratify=master_df["strat_key"]
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=RANDOM_SEED,
    stratify=temp_df["strat_key"]
)

# Drop temporary stratification key
train_df = train_df.drop(columns=["strat_key"])
val_df   = val_df.drop(columns=["strat_key"])
test_df  = test_df.drop(columns=["strat_key"])

# Save splits
train_df.to_csv(DATA_PROC / "train.csv", index=False)
val_df.to_csv(DATA_PROC / "val.csv", index=False)
test_df.to_csv(DATA_PROC / "test.csv", index=False)

print("\nSaved stratified splits:")
print(f"  Train: {len(train_df)} rows ({len(train_df)/len(master_df)*100:.1f}%)")
print(f"  Val:   {len(val_df)} rows ({len(val_df)/len(master_df)*100:.1f}%)")
print(f"  Test:  {len(test_df)} rows ({len(test_df)/len(master_df)*100:.1f}%)")
print("\nTest set representation by crop:")
print(test_df["crop_name"].value_counts())
print("\nBuild complete successfully!")
