import pandas as pd
from pathlib import Path
import sys

# Ensure ml module can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import RAW_DATA_DIR, MASTER_DATA_PATH, MASTER_FEATURES_PATH


def load_raw_cotton_data():
    path = RAW_DATA_DIR / "Book2.csv"
    if path.exists():
        return pd.read_csv(path)
    raise FileNotFoundError(f"Cotton raw dataset not found at {path}")


def load_raw_rice_data():
    path = RAW_DATA_DIR / "RICE.csv"
    if path.exists():
        return pd.read_csv(path)
    raise FileNotFoundError(f"Rice raw dataset not found at {path}")


def load_master_features():
    if MASTER_FEATURES_PATH.exists():
        return pd.read_csv(MASTER_FEATURES_PATH)
    elif MASTER_DATA_PATH.exists():
        return pd.read_csv(MASTER_DATA_PATH)
    raise FileNotFoundError(f"Processed master dataset not found at {MASTER_FEATURES_PATH}")


if __name__ == "__main__":
    df = load_master_features()
    print(f"Loaded master feature dataset with shape: {df.shape}")
    print("Columns:", list(df.columns))
