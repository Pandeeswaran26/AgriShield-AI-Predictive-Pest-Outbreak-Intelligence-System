"""
Extended Multi-Crop Dataset Builder
Crop-Irrigation-AI / AgriShield Platform
=========================================
Extends multi_crop_irrigation.csv with new crops:
  - Sugarcane: 85 records (Coimbatore TN + Kolhapur MH)
  - Tomato:    31 records (Nasik MH + Kolar KA)
  - Potato:    27 records (Shimla HP + Agra UP)

Produces:
  data/processed/multi_crop_irrigation_extended.csv  (master, 763+ rows)
  data/processed/train_ext.csv  (70%)
  data/processed/val_ext.csv    (15%)
  data/processed/test_ext.csv   (15%)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW  = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
DATA_PROC.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

print("=" * 64)
print("BUILDING EXTENDED MULTI-CROP IRRIGATION DATASET")
print("=" * 64)

# ─── 1. Load existing harmonized dataset ─────────────────────────────
existing_path = DATA_PROC / "multi_crop_irrigation.csv"
df_existing = pd.read_csv(existing_path)
print(f"\n[1] Loaded existing master dataset: {len(df_existing)} rows")
print(f"    Crops: {df_existing['crop_name'].value_counts().to_dict()}")

# ─── 2. Load new crops dataset ───────────────────────────────────────
new_path = DATA_RAW / "sugarcane_tomato_potato_irrigation.csv"
df_new_raw = pd.read_csv(new_path)
print(f"\n[2] Loaded new crops raw: {len(df_new_raw)} rows")
print(f"    New crops: {df_new_raw['crop_name'].value_counts().to_dict()}")

# ─── 3. Harmonise schema of new data ─────────────────────────────────
# New data already has the correct schema (same columns as existing minus crop_type)
cols_needed = [
    "crop_name", "crop_days", "soil_moisture", "soil_temperature",
    "temperature", "humidity", "rainfall", "irrigation",
    "location", "dataset_source"
]
df_new = df_new_raw[cols_needed].copy()
df_new["crop_days"]        = df_new["crop_days"].astype(float)
df_new["soil_moisture"]    = df_new["soil_moisture"].astype(float).round(2)
df_new["soil_temperature"] = df_new["soil_temperature"].astype(float).round(1)
df_new["temperature"]      = df_new["temperature"].astype(float).round(1)
df_new["humidity"]         = df_new["humidity"].astype(float).round(1)
df_new["rainfall"]         = df_new["rainfall"].astype(float).round(1)
df_new["irrigation"]       = df_new["irrigation"].astype(int)

# ─── 4. Combine and re-encode ─────────────────────────────────────────
master_df = pd.concat(
    [df_existing.drop(columns=["crop_type"], errors="ignore"), df_new],
    ignore_index=True
)

CROP_MAPPING = {
    "Cotton":    0,
    "Groundnut": 1,
    "Maize":     2,
    "Potato":    3,
    "Rice":      4,
    "Soybean":   5,
    "Sugarcane": 6,
    "Tomato":    7,
    "Wheat":     8,
}
master_df["crop_type"] = master_df["crop_name"].map(CROP_MAPPING)

ordered_cols = [
    "crop_name", "crop_type", "crop_days", "soil_moisture", "soil_temperature",
    "temperature", "humidity", "rainfall", "irrigation",
    "location", "dataset_source"
]
master_df = master_df[ordered_cols]

out_path = DATA_PROC / "multi_crop_irrigation_extended.csv"
master_df.to_csv(out_path, index=False)

print(f"\n[3] Extended master dataset saved: {out_path}")
print(f"    Total rows : {len(master_df)}")
print(f"    Crop distribution:")
print(master_df["crop_name"].value_counts().to_string())
print(f"\n    Irrigation label distribution:")
print(master_df["irrigation"].value_counts().to_string())

# ─── 5. Stratified 70 / 15 / 15 splits ──────────────────────────────
master_df["strat_key"] = master_df["crop_name"] + "_" + master_df["irrigation"].astype(str)

train_df, temp_df = train_test_split(
    master_df, test_size=0.30,
    random_state=RANDOM_SEED,
    stratify=master_df["strat_key"]
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.50,
    random_state=RANDOM_SEED,
    stratify=temp_df["strat_key"]
)

for df, name in [(train_df, "strat_key"), (val_df, "strat_key"), (test_df, "strat_key")]:
    df.drop(columns=[name], inplace=True, errors="ignore")

train_df.to_csv(DATA_PROC / "train_ext.csv", index=False)
val_df.to_csv(DATA_PROC / "val_ext.csv",   index=False)
test_df.to_csv(DATA_PROC / "test_ext.csv",  index=False)

total = len(master_df)
print(f"\n[4] Stratified splits saved:")
print(f"    Train : {len(train_df):4d} rows  ({len(train_df)/total*100:.1f}%)")
print(f"    Val   : {len(val_df):4d} rows  ({len(val_df)/total*100:.1f}%)")
print(f"    Test  : {len(test_df):4d} rows  ({len(test_df)/total*100:.1f}%)")
print("\n[✓] Extended dataset build complete!")
