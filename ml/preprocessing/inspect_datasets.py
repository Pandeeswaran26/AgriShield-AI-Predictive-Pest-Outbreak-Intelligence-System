import os
import pandas as pd

DATASET_FOLDER = "datasets/raw"

for file in os.listdir(DATASET_FOLDER):
    file_path = os.path.join(DATASET_FOLDER, file)

    if file.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        continue

    print("=" * 80)
    print(f"Dataset : {file}")
    print(f"Shape    : {df.shape}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nFirst 5 Rows:")
    print(df.head())

    print("=" * 80)