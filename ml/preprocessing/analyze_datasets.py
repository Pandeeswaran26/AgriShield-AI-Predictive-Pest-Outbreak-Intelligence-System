import pandas as pd
from pathlib import Path

# Folder containing your datasets
DATASET_FOLDER = "datasets/raw"

# Supported file types
extensions = ["*.csv", "*.xlsx", "*.xls"]

files = []

for ext in extensions:
    files.extend(Path(DATASET_FOLDER).glob(ext))

print("=" * 80)
print("AGRISHIELD AI - DATASET ANALYSIS")
print("=" * 80)

for file in files:

    print(f"\n📁 Dataset: {file.name}")

    try:
        if file.suffix == ".csv":
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        print("-" * 60)
        print(f"Rows      : {df.shape[0]}")
        print(f"Columns   : {df.shape[1]}")

        print("\nColumn Names:")
        print(df.columns.tolist())

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nDuplicate Rows:")
        print(df.duplicated().sum())

        print("\nData Types:")
        print(df.dtypes)

        print("\nFirst 3 Rows:")
        print(df.head(3))

        print("=" * 80)

    except Exception as e:
        print("Error:", e)