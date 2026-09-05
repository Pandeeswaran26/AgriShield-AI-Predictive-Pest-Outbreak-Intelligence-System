from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "datasets"
RAW_DATA_DIR = DATASETS_DIR / "raw"
PROCESSED_DATA_DIR = DATASETS_DIR / "processed"
MASTER_DATA_PATH = PROCESSED_DATA_DIR / "master_dataset.csv"
MASTER_FEATURES_PATH = PROCESSED_DATA_DIR / "master_dataset_features.csv"

MODELS_DIR = PROJECT_ROOT / "ml" / "models"
FINAL_MODEL_PATH = MODELS_DIR / "final_pest_prediction_model.pkl"
ENCODERS_PATH = MODELS_DIR / "label_encoders.pkl"
METADATA_PATH = MODELS_DIR / "model_metadata.json"
METRICS_PATH = MODELS_DIR / "model_metrics.json"

REPORTS_DIR = PROJECT_ROOT / "ml" / "reports"
MODEL_COMPARISON_PATH = REPORTS_DIR / "model_comparison.csv"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
SHAP_OUTPUTS_DIR = OUTPUTS_DIR / "shap"

# Columns
TARGET_COLUMN = "Pest Value"
CATEGORICAL_COLUMNS = ["Crop", "Pest_Name", "Location", "Rainfall_Category"]
NUMERICAL_FEATURE_COLUMNS = [
    "Observation Year",
    "Standard Week",
    "MaxT",
    "MinT",
    "RH1(%)",
    "RH2(%)",
    "RF(mm)",
    "WS(kmph)",
    "SSH(hrs)",
    "EVP(mm)",
    "Temp_Diff",
    "Avg_Humidity",
    "Week_Sin",
    "Week_Cos",
    "Weather_Index",
]

ALL_FEATURE_COLUMNS = [
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
    "Temp_Diff",
    "Avg_Humidity",
    "Week_Sin",
    "Week_Cos",
    "Weather_Index",
    "Rainfall_Category",
]

# Hyperparameters
RANDOM_STATE = 42
TARGET_CAP_HIGH = 0.99
TARGET_CAP_LOW = 0.01
N_ESTIMATORS = 250
