"""
AgriShield Central Decision Engine.

Synthesizes:
1. Field Telemetry & Geolocation
2. Calculated Growth Stage & Crop Age
3. Live Open-Meteo Weather & 7-Day Forecast
4. Soil Environment & Nutrient Constraints
5. Tabular ML Pest Outbreak Predictions
6. Foliar Vision Pathology Diagnosis

Generates a unified Crop Assessment with multi-factor risk scoring
and strict Data Source tracking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


def evaluate_crop_health_and_risk(
    crop: str,
    growth_stage_info: Dict[str, Any],
    weather_dict: Dict[str, Any],
    forecast_days: List[Dict[str, Any]],
    soil_data: Dict[str, Any],
    tabular_ml_result: Optional[Dict[str, Any]] = None,
    image_diagnosis_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Combines all available intelligence streams into an integrated assessment.
    """
    max_t = float(weather_dict.get("MaxT") or 30.0)
    min_t = float(weather_dict.get("MinT") or 22.0)
    temp_swing = round(max_t - min_t, 1)
    rh1 = float(weather_dict.get("RH1") or 70.0)
    rf = float(weather_dict.get("RF") or 0.0)
    ws = float(weather_dict.get("WS") or 5.0)

    # 7-day rainfall forecast sum
    forecast_rf_sum = sum(float(day.get("rf", 0.0) or 0.0) for day in forecast_days)

    # ── 1. Tabular Outbreak Risk Assessment ──────────────────────────────
    top_pest_name = "General Pest Pressure"
    pest_risk_level = "Low"
    pest_prob_score = 0.0
    if tabular_ml_result:
        top_pest = tabular_ml_result.get("top_pest", {})
        top_pest_name = top_pest.get("pest_name", "General Field Pest")
        pest_risk_level = top_pest.get("risk_level", "Low")
        pest_prob_score = float(top_pest.get("pest_value", 0.0))

    # ── 2. Foliar Pathology Assessment ──────────────────────────────────
    foliar_disease = None
    foliar_confidence = 0.0
    foliar_is_healthy = True
    foliar_severity = "Low"
    has_valid_leaf_diagnosis = False

    if image_diagnosis_result and image_diagnosis_result.get("is_valid_plant"):
        has_valid_leaf_diagnosis = True
        foliar_disease = image_diagnosis_result.get("disease", "")
        foliar_confidence = float(image_diagnosis_result.get("confidence") or 0.0)
        foliar_is_healthy = bool(image_diagnosis_result.get("is_healthy", False))
        foliar_severity = image_diagnosis_result.get("severity", "Medium")

    # ── 3. Environmental & Meteorological Stress Scoring ─────────────────
    env_stress_points = 0
    stress_factors = []

    # Thermal Stress
    if max_t >= 37.0:
        env_stress_points += 2
        stress_factors.append({
            "category": "Thermal Stress",
            "severity": "High",
            "detail": f"Extreme daytime high of {max_t}°C causes pollen sterility and stomatal closure.",
            "source": "LIVE WEATHER",
        })
    elif max_t >= 34.0:
        env_stress_points += 1
        stress_factors.append({
            "category": "Elevated Temperature",
            "severity": "Moderate",
            "detail": f"Daytime high of {max_t}°C accelerates evaporation and nymph development.",
            "source": "LIVE WEATHER",
        })

    # High Diurnal Oscillation
    if temp_swing >= 10.0:
        env_stress_points += 1
        stress_factors.append({
            "category": "Diurnal Temp Differential",
            "severity": "Moderate",
            "detail": f"{temp_swing}°C swing ({min_t}°C to {max_t}°C) promotes dew formation and spore germination.",
            "source": "LIVE WEATHER",
        })

    # Foliar Fungal Humidity Window
    if rh1 >= 80.0 and 20.0 <= max_t <= 32.0:
        env_stress_points += 2
        stress_factors.append({
            "category": "High Foliar Humidity",
            "severity": "High",
            "detail": f"Morning relative humidity at {rh1}% provides ideal microclimate for foliar blight, blast, and powdery mildew.",
            "source": "LIVE WEATHER",
        })

    # Heavy Precipitation / Wash-off Risk
    if rf >= 25.0 or forecast_rf_sum >= 40.0:
        env_stress_points += 2
        stress_factors.append({
            "category": "Heavy Precipitation",
            "severity": "High",
            "detail": f"Substantial rainfall ({rf} mm today, {forecast_rf_sum:.1f} mm 7-day forecast) risks waterlogging and wash-off of sprays.",
            "source": "LIVE WEATHER / FORECAST",
        })
    elif rf == 0.0 and forecast_rf_sum <= 2.0:
        stress_factors.append({
            "category": "Dry Weather Window",
            "severity": "Low",
            "detail": "Clear weather with minimal rainfall; favorable for scheduled field operations and foliar sprays.",
            "source": "LIVE WEATHER / FORECAST",
        })

    # Wind Drift Risk
    if ws >= 16.0:
        stress_factors.append({
            "category": "High Wind Drift",
            "severity": "Moderate",
            "detail": f"Wind speeds of {ws} km/h will cause severe pesticide drift. Delay spraying until calm periods.",
            "source": "LIVE WEATHER",
        })

    # Soil Context Stress
    soil_moisture = soil_data.get("soil_moisture")
    soil_ph = soil_data.get("soil_ph")
    if soil_moisture is not None:
        if soil_moisture < 35.0:
            env_stress_points += 2
            stress_factors.append({
                "category": "Soil Moisture Deficit",
                "severity": "High",
                "detail": f"Soil moisture at {soil_moisture}% indicates crop water stress; root nutrient uptake is compromised.",
                "source": "USER / SENSOR DATA",
            })
        elif soil_moisture > 85.0 and crop != "Rice":
            env_stress_points += 1
            stress_factors.append({
                "category": "Soil Saturation",
                "severity": "Moderate",
                "detail": f"High soil moisture ({soil_moisture}%) in upland crop risks root hypoxia and damping-off.",
                "source": "USER / SENSOR DATA",
            })

    if soil_ph is not None:
        if soil_ph < 5.2:
            stress_factors.append({
                "category": "Soil Acidity",
                "severity": "Moderate",
                "detail": f"Acidic soil (pH {soil_ph}) limits Phosphorus availability and micronutrient balance.",
                "source": "USER / SOIL DATA",
            })
        elif soil_ph > 8.2:
            stress_factors.append({
                "category": "Soil Alkalinity",
                "severity": "Moderate",
                "detail": f"Alkaline soil (pH {soil_ph}) restricts Iron and Zinc uptake; consider gypsum or sulfur amendments.",
                "source": "USER / SOIL DATA",
            })

    # ── 4. Unified Overall Health & Combined Risk Determination ─────────
    # Combine Tabular ML + Leaf Pathology + Environmental Stress
    overall_health = "Healthy"
    overall_risk = "Low"
    health_headline = "Crop Condition Normal"

    if has_valid_leaf_diagnosis and not foliar_is_healthy:
        if foliar_confidence >= 70.0 or foliar_severity in ["High", "Critical"]:
            overall_health = "Active Disease Infection"
            overall_risk = "High"
            health_headline = f"Foliar Disease Confirmed: {foliar_disease}"
        else:
            overall_health = "Foliar Symptoms Detected"
            overall_risk = "Moderate" if pest_risk_level != "High" else "High"
            health_headline = f"Potential Foliar Disease: {foliar_disease}"
    elif pest_risk_level == "High":
        overall_health = "Pest Outbreak Alert"
        overall_risk = "High"
        health_headline = f"Elevated Pest Outbreak Pressure ({top_pest_name})"
    elif pest_risk_level == "Medium" or env_stress_points >= 3:
        overall_health = "Moderate Environmental Stress"
        overall_risk = "Moderate"
        health_headline = "Microclimate Favorable for Pest / Disease Incubation"
    else:
        overall_health = "Healthy & Optimal"
        overall_risk = "Low"
        health_headline = f"{crop} crop is within normal physiological parameters"

    # ── 5. Data Source Manifest ──────────────────────────────────────────
    data_sources = {
        "location": "USER / GPS SENSOR",
        "crop": "USER INPUT",
        "planting_date": "USER INPUT",
        "growth_stage": "CALCULATED (ESTIMATE)",
        "days_after_planting": "CALCULATED (ESTIMATE)",
        "temperature": "LIVE WEATHER (OPEN-METEO)",
        "humidity": "LIVE WEATHER (OPEN-METEO)",
        "rainfall": "LIVE WEATHER (OPEN-METEO)",
        "forecast": "LIVE WEATHER (OPEN-METEO)",
        "soil_moisture": "USER / SENSOR DATA" if soil_data.get("soil_moisture") is not None else "UNSPECIFIED (DEFAULT USED FOR ADVISORY)",
        "soil_nutrients_npk": "USER / SOIL TEST" if (soil_data.get("soil_n") is not None or soil_data.get("soil_p") is not None) else "NOT PROVIDED (WARNING ISSUED)",
        "pest_outbreak_risk": "TABULAR ML MODEL (EXTRATREES)",
        "leaf_diagnosis": "PLANT VISION CLASSIFIER (38-CLASS RESNET/BENCHMARK)" if has_valid_leaf_diagnosis else "NO IMAGE ATTACHED",
        "decision_synthesis": "AGRISHIELD HYBRID DECISION ENGINE",
    }

    return {
        "overall_health_status": overall_health,
        "overall_risk_level": overall_risk,
        "health_headline": health_headline,
        "crop": crop,
        "growth_stage": growth_stage_info.get("growth_stage", "Vegetative"),
        "days_after_planting": growth_stage_info.get("days_after_planting", 30),
        "stage_description": growth_stage_info.get("stage_description", ""),
        "water_demand": growth_stage_info.get("water_demand", "Medium"),
        "nutrient_demand": {
            "nitrogen": growth_stage_info.get("nitrogen_demand", "Medium"),
            "potassium": growth_stage_info.get("potassium_demand", "Medium"),
        },
        "environmental_stress_score": env_stress_points,
        "stress_factors": stress_factors,
        "tabular_pest_assessment": {
            "top_pest": top_pest_name,
            "risk_level": pest_risk_level,
            "predicted_incidence_value": round(pest_prob_score, 2),
            "source": "TABULAR ML MODEL",
        },
        "foliar_pathology_assessment": {
            "has_leaf_diagnosis": has_valid_leaf_diagnosis,
            "disease": foliar_disease,
            "confidence": foliar_confidence,
            "is_healthy": foliar_is_healthy,
            "severity": foliar_severity,
            "source": "PLANT VISION MODEL" if has_valid_leaf_diagnosis else "NONE",
        },
        "data_sources": data_sources,
        "assessment_timestamp": datetime.now(timezone.utc).isoformat(),
    }
