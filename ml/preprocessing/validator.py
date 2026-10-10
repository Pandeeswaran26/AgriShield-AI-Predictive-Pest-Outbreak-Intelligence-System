"""
Data Validation Pipeline for AgriShield AI.

Provides rigorous scientific boundary checking for meteorological observations,
field parameters, and dataset consistency. Ensures no physically impossible values
(e.g., negative rainfall, RH > 100%, MinT > MaxT) propagate into ML models.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd


class DataValidator:
    """
    Validates meteorological and agronomic data inputs against physical
    and biological boundary constraints.
    """

    # Physical meteorological bounds
    BOUNDS = {
        "MaxT": {"min": -10.0, "max": 60.0, "name": "Maximum Temperature (°C)"},
        "MinT": {"min": -20.0, "max": 50.0, "name": "Minimum Temperature (°C)"},
        "RH1": {"min": 0.0, "max": 100.0, "name": "Morning Relative Humidity (%)"},
        "RH2": {"min": 0.0, "max": 100.0, "name": "Afternoon Relative Humidity (%)"},
        "RF": {"min": 0.0, "max": 1000.0, "name": "Rainfall (mm)"},
        "WS": {"min": 0.0, "max": 160.0, "name": "Wind Speed (km/h)"},
        "SSH": {"min": 0.0, "max": 24.0, "name": "Sunshine Hours (hrs)"},
        "EVP": {"min": 0.0, "max": 50.0, "name": "Pan Evaporation (mm)"},
        "Standard_Week": {"min": 1, "max": 53, "name": "Standard Calendar Week"},
        "Observation_Year": {"min": 1980, "max": 2100, "name": "Observation Year"},
        "soil_moisture": {"min": 0.0, "max": 100.0, "name": "Soil Moisture (%)"},
        "soil_ph": {"min": 2.0, "max": 12.0, "name": "Soil pH"},
    }

    VALID_CROPS = {"rice", "cotton", "tomato", "potato", "corn", "wheat", "apple", "grape", "pepper"}

    @classmethod
    def validate_weather_inputs(cls, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str], Dict[str, Any]]:
        """
        Validates a single prediction or assessment input dictionary.
        Returns:
            (is_valid, errors, warnings, sanitized_dict)
        """
        errors = []
        warnings = []
        sanitized = dict(data)

        # 1. Temperature checks
        max_t = sanitized.get("MaxT")
        min_t = sanitized.get("MinT")

        if max_t is not None:
            try:
                max_t = float(max_t)
                sanitized["MaxT"] = max_t
                if not (cls.BOUNDS["MaxT"]["min"] <= max_t <= cls.BOUNDS["MaxT"]["max"]):
                    errors.append(f"MaxT ({max_t}°C) exceeds physical atmosphere boundaries (-10°C to 60°C).")
            except (ValueError, TypeError):
                errors.append(f"Invalid non-numeric MaxT: {max_t}")

        if min_t is not None:
            try:
                min_t = float(min_t)
                sanitized["MinT"] = min_t
                if not (cls.BOUNDS["MinT"]["min"] <= min_t <= cls.BOUNDS["MinT"]["max"]):
                    errors.append(f"MinT ({min_t}°C) exceeds physical atmosphere boundaries (-20°C to 50°C).")
            except (ValueError, TypeError):
                errors.append(f"Invalid non-numeric MinT: {min_t}")

        if max_t is not None and min_t is not None:
            if min_t > max_t:
                errors.append(f"Thermodynamic inconsistency: MinT ({min_t}°C) cannot exceed MaxT ({max_t}°C).")

        # 2. Humidity checks
        for rh_key in ["RH1", "RH2"]:
            val = sanitized.get(rh_key)
            if val is not None:
                try:
                    val = float(val)
                    sanitized[rh_key] = val
                    if val < 0.0 or val > 100.0:
                        errors.append(f"{rh_key} ({val}%) must be bounded strictly between 0% and 100%.")
                except (ValueError, TypeError):
                    errors.append(f"Invalid non-numeric {rh_key}: {val}")

        # Check relative humidity diurnality: Morning RH1 is almost always >= Afternoon RH2 in fair weather
        rh1 = sanitized.get("RH1")
        rh2 = sanitized.get("RH2")
        if rh1 is not None and rh2 is not None:
            if rh2 > rh1 + 25.0:
                warnings.append(f"Unusual microclimate: Afternoon RH2 ({rh2}%) exceeds Morning RH1 ({rh1}%) significantly.")

        # 3. Rainfall checks
        rf = sanitized.get("RF")
        if rf is not None:
            try:
                rf = float(rf)
                sanitized["RF"] = rf
                if rf < 0.0:
                    errors.append(f"Rainfall (RF={rf} mm) cannot be negative.")
                elif rf > 500.0:
                    warnings.append(f"Extreme precipitation event recorded: {rf} mm in 24 hours.")
            except (ValueError, TypeError):
                errors.append(f"Invalid non-numeric RF: {rf}")

        # 4. Wind speed
        ws = sanitized.get("WS")
        if ws is not None:
            try:
                ws = float(ws)
                sanitized["WS"] = ws
                if ws < 0.0:
                    errors.append(f"Wind speed (WS={ws} km/h) cannot be negative.")
                elif ws > 120.0:
                    warnings.append(f"Severe gale/storm wind speed recorded: {ws} km/h.")
            except (ValueError, TypeError):
                errors.append(f"Invalid non-numeric WS: {ws}")

        # 5. Calendar constraints
        week = sanitized.get("Standard_Week")
        if week is not None:
            try:
                week = int(week)
                sanitized["Standard_Week"] = week
                if not (1 <= week <= 53):
                    errors.append(f"Standard_Week ({week}) must be between 1 and 53.")
            except (ValueError, TypeError):
                errors.append(f"Invalid Standard_Week: {week}")

        # 6. Crop normalization
        crop = sanitized.get("Crop")
        if crop:
            crop_clean = str(crop).strip().lower()
            if not any(valid_crop in crop_clean for valid_crop in cls.VALID_CROPS):
                warnings.append(f"Crop '{crop}' is outside standard validated calibration crops: {sorted(cls.VALID_CROPS)}.")

        # 7. Soil metrics if present
        soil_moisture = sanitized.get("soil_moisture")
        if soil_moisture is not None:
            try:
                sm = float(soil_moisture)
                sanitized["soil_moisture"] = sm
                if not (0.0 <= sm <= 100.0):
                    errors.append(f"Soil moisture ({sm}%) must be between 0% and 100%.")
            except (ValueError, TypeError):
                errors.append(f"Invalid soil moisture: {soil_moisture}")

        soil_ph = sanitized.get("soil_ph")
        if soil_ph is not None:
            try:
                sph = float(soil_ph)
                sanitized["soil_ph"] = sph
                if not (3.0 <= sph <= 11.0):
                    errors.append(f"Soil pH ({sph}) is outside plausible agronomic range (3.0 to 11.0).")
            except (ValueError, TypeError):
                errors.append(f"Invalid soil pH: {soil_ph}")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings, sanitized

    @classmethod
    def validate_dataframe(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Runs comprehensive data validation and quality check across an entire dataset.
        Detects missing values, duplicates, outliers, and physical impossibilities.
        """
        report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "duplicates": int(df.duplicated().sum()),
            "missing_values": df.isnull().sum().to_dict(),
            "anomalies": {},
            "is_valid": True,
        }

        # Check for MinT > MaxT violations
        if "MinT" in df.columns and "MaxT" in df.columns:
            inversions = (df["MinT"] > df["MaxT"]).sum()
            report["anomalies"]["MinT_greater_than_MaxT"] = int(inversions)
            if inversions > 0:
                report["is_valid"] = False

        # Check RH bounds
        for rh_col in ["RH1(%)", "RH1", "RH2(%)", "RH2"]:
            if rh_col in df.columns:
                invalid_rh = ((df[rh_col] < 0) | (df[rh_col] > 100)).sum()
                report["anomalies"][f"invalid_{rh_col}"] = int(invalid_rh)
                if invalid_rh > 0:
                    report["is_valid"] = False

        # Check negative rainfall
        for rf_col in ["RF(mm)", "RF"]:
            if rf_col in df.columns:
                neg_rf = (df[rf_col] < 0).sum()
                report["anomalies"][f"negative_{rf_col}"] = int(neg_rf)
                if neg_rf > 0:
                    report["is_valid"] = False

        return report
