"""
AgriShield Structured Recommendation Engine.

Generates actionable, explainable agronomic decisions answering:
1. WHAT TO DO (Concrete operational action)
2. WHEN TO DO IT (Specific time window)
3. WHY TO DO IT (Underlying agronomic & meteorological rationale)

Structured across:
- Prioritized Action Stream (CRITICAL, HIGH, MEDIUM, LOW)
- Irrigation Intelligence
- Crop Nutrition & Fertilizer (with explicit missing soil test warnings)
- Disease & Pest Management (confidence-gated IPM)
- Weather-Aware Spray & Field Timing Windows
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def generate_structured_recommendations(
    crop: str,
    growth_stage_info: Dict[str, Any],
    weather_dict: Dict[str, Any],
    forecast_days: List[Dict[str, Any]],
    soil_data: Dict[str, Any],
    decision_assessment: Dict[str, Any],
    tabular_ml_result: Optional[Dict[str, Any]] = None,
    image_diagnosis_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main entry point for generating structured, prioritized recommendations.
    """
    stage_name = growth_stage_info.get("growth_stage", "Vegetative")
    dap = growth_stage_info.get("days_after_planting", 30)
    water_demand = growth_stage_info.get("water_demand", "Medium")
    n_demand = growth_stage_info.get("nitrogen_demand", "Medium")
    k_demand = growth_stage_info.get("potassium_demand", "Medium")

    max_t = float(weather_dict.get("MaxT") or 30.0)
    min_t = float(weather_dict.get("MinT") or 22.0)
    rh1 = float(weather_dict.get("RH1") or 70.0)
    rf = float(weather_dict.get("RF") or 0.0)
    ws = float(weather_dict.get("WS") or 5.0)

    forecast_rf_sum = sum(float(day.get("rf", 0.0) or 0.0) for day in forecast_days)
    next_24h_rain = float(forecast_days[0].get("rf", 0.0)) if forecast_days else rf

    soil_moisture = soil_data.get("soil_moisture")
    soil_ph = soil_data.get("soil_ph")
    soil_n = soil_data.get("soil_n")
    soil_p = soil_data.get("soil_p")
    soil_k = soil_data.get("soil_k")
    irrigation_method = soil_data.get("irrigation_method") or "Standard Furrow / Basin"

    prioritized_actions: List[Dict[str, Any]] = []

    # ──────────────────────────────────────────────────────────────────────────
    # 1. IRRIGATION INTELLIGENCE MODULE
    # ──────────────────────────────────────────────────────────────────────────
    irrigation_status = "No irrigation currently"
    irrigation_window = "Next 48–72 hours"
    irrigation_reason = ""
    irrigation_priority = "LOW"

    # Evaluate moisture & forecast
    if next_24h_rain >= 10.0 or rf >= 15.0:
        irrigation_status = "No irrigation currently"
        irrigation_window = "Postpone for 3–5 days until field drains"
        irrigation_reason = (
            f"Recent/forecast rainfall ({next_24h_rain:.1f} mm expected) provides adequate root zone hydration. "
            f"Additional irrigation would cause waterlogging and nutrient leaching."
        )
        irrigation_priority = "LOW"
    elif soil_moisture is not None and soil_moisture < 40.0:
        if water_demand in ["High", "Very High"]:
            irrigation_status = "Irrigate now"
            irrigation_window = "Tomorrow early morning (6:00 AM – 8:30 AM)"
            irrigation_reason = (
                f"Soil moisture is critically low ({soil_moisture}%) during the '{stage_name}' stage, "
                f"which has '{water_demand}' water demand. Moisture stress now directly reduces yield."
            )
            irrigation_priority = "CRITICAL"
        else:
            irrigation_status = "Irrigate soon"
            irrigation_window = "Within the next 24 hours"
            irrigation_reason = (
                f"Soil moisture is low ({soil_moisture}%). Apply light irrigation via {irrigation_method} to maintain vegetative turgor."
            )
            irrigation_priority = "HIGH"
    elif soil_moisture is not None and soil_moisture > 80.0:
        irrigation_status = "No irrigation currently"
        irrigation_window = "Recheck after 4 days"
        irrigation_reason = f"Soil moisture is at {soil_moisture}%; root zone is sufficiently saturated."
        irrigation_priority = "LOW"
    elif max_t >= 36.0 and next_24h_rain < 2.0:
        irrigation_status = "Irrigate soon"
        irrigation_window = "Late evening (5:00 PM – 7:30 PM) or early morning"
        irrigation_reason = (
            f"High daytime temperature ({max_t}°C) accelerates evapotranspiration. "
            f"Provide light irrigation to lower canopy temperature and prevent heat shock."
        )
        irrigation_priority = "HIGH" if water_demand in ["High", "Very High"] else "MEDIUM"
    else:
        irrigation_status = "Recheck later"
        irrigation_window = "Recheck soil moisture in 48 hours"
        irrigation_reason = (
            f"Current environmental conditions and {water_demand.lower()} crop water demand at {stage_name} stage indicate stable soil moisture."
        )
        irrigation_priority = "LOW"

    irrigation_action = {
        "id": "act_irrigation",
        "domain": "Irrigation",
        "priority": irrigation_priority,
        "title": f"Irrigation: {irrigation_status}",
        "what": f"Implement {irrigation_status.lower()} strategy using {irrigation_method}.",
        "when": irrigation_window,
        "why": irrigation_reason,
        "data_sources": ["LIVE WEATHER", "USER SOIL DATA", "CALCULATED GROWTH STAGE"],
    }
    if irrigation_priority in ["CRITICAL", "HIGH", "MEDIUM"]:
        prioritized_actions.append(irrigation_action)

    # ──────────────────────────────────────────────────────────────────────────
    # 2. CROP NUTRITION & FERTILIZER MODULE
    # ──────────────────────────────────────────────────────────────────────────
    has_soil_test = (soil_n is not None or soil_p is not None or soil_k is not None)
    fert_priority = "MEDIUM"
    fert_status = "Growth-stage split application recommended"
    fert_window = f"During '{stage_name}' window (DAP {dap})"
    fert_warning = None
    fert_what = ""
    fert_why = ""

    crop_lower = crop.lower()
    is_rice = "rice" in crop_lower or "paddy" in crop_lower
    is_cotton = "cotton" in crop_lower

    if not has_soil_test:
        fert_warning = (
            "Recommendation limited because soil nutrient measurements (N/P/K) are unavailable. "
            "Displaying standard agronomic baseline for this crop and growth stage. "
            "For precision dosing, conduct a lab soil test."
        )

    # Fertilizer logic by crop and stage
    if is_rice:
        if "tillering" in stage_name.lower():
            fert_what = "Top-dress Nitrogen (Urea @ 25-30 kg/acre) + Zinc Sulphate (10 kg/acre if deficient)."
            fert_why = f"Active tillering (DAP {dap}) requires peak Nitrogen for secondary shoot initiation."
            fert_window = "Morning hours within next 48–72 hours (ensure shallow water)"
            fert_priority = "HIGH"
        elif "panicle" in stage_name.lower() or "booting" in stage_name.lower():
            fert_what = "Apply Muriate of Potash (MOP @ 15-20 kg/acre) + split Nitrogen (Urea @ 15 kg/acre)."
            fert_why = "Panicle initiation demands Potassium for spikelet fertility and lodging resistance."
            fert_window = "Within next 3–5 days"
            fert_priority = "HIGH"
        elif "flowering" in stage_name.lower() or "dough" in stage_name.lower():
            fert_what = "Avoid granular soil Nitrogen; apply foliar spray of 1% Potassium Nitrate (13-0-45) if leaf tips yellow."
            fert_why = "Excessive late-season Nitrogen delays grain ripening and promotes Rice Blast disease."
            fert_window = "Late evening spray window"
            fert_priority = "MEDIUM"
        else:
            fert_what = "Maintain basal NPK balance (100:50:50 kg/ha equivalent in splits)."
            fert_why = f"Current stage ({stage_name}) requires balanced root establishment."
            fert_priority = "LOW"
    elif is_cotton:
        if "squaring" in stage_name.lower() or "vegetative" in stage_name.lower():
            fert_what = "Top-dress Nitrogen (Urea @ 30 kg/acre) + Magnesium Sulphate @ 10 kg/acre."
            fert_why = "Square development requires vegetative vigor while Magnesium prevents red leaf blight."
            fert_window = "Within next 2–4 days after weeding"
            fert_priority = "HIGH"
        elif "flowering" in stage_name.lower() or "boll" in stage_name.lower():
            fert_what = "Foliar spray of 2% DAP or 1% Potassium Nitrate (13-0-45) + Boron 20% @ 1 g/L."
            fert_why = "Peak boll setting requires Potassium and Boron to prevent square and boll shedding."
            fert_window = "Apply in calm morning (6:30 AM – 9:00 AM)"
            fert_priority = "HIGH"
        else:
            fert_what = "Balanced split nutrition. Avoid heavy single-dose urea applications."
            fert_why = "Excessive Nitrogen attracts sucking pests and bollworm moths."
            fert_priority = "LOW"
    else:  # General Horticultural / Cereal crops (Tomato, Potato, Corn, etc.)
        if n_demand in ["High", "Very High"]:
            fert_what = f"Apply balanced NPK split (e.g. 19:19:19 @ 5 g/L foliar or side-dressing) suited for {crop}."
            fert_why = f"Crop is at '{stage_name}' stage with {n_demand.lower()} vegetative nutrient demand."
            fert_window = "Within next 3–5 days"
            fert_priority = "MEDIUM"
        elif k_demand in ["High", "Very High"]:
            fert_what = f"Supplement Potassium (SOP or Potassium Nitrate) to support fruit/tuber expansion in {crop}."
            fert_why = f"Fruiting / Bulking stage demands Potassium for sugar accumulation and skin firmness."
            fert_window = "Within next 48–72 hours"
            fert_priority = "HIGH"
        else:
            fert_what = "Follow standard balanced organic compost / NPK schedule."
            fert_why = f"Routine maintenance for {crop} at {stage_name} stage."
            fert_priority = "LOW"

    # Soil pH modification warning
    if soil_ph is not None:
        if soil_ph < 5.5:
            fert_why += f" Note: Low soil pH ({soil_ph}) reduces Phosphorus uptake; consider applying agricultural lime."
        elif soil_ph > 8.0:
            fert_why += f" Note: High soil pH ({soil_ph}) locks micronutrients; apply elemental sulfur or chelated zinc."

    fertilizer_action = {
        "id": "act_fertilizer",
        "domain": "Fertilizer",
        "priority": fert_priority,
        "title": f"Crop Nutrition: {fert_status}",
        "what": fert_what,
        "when": fert_window,
        "why": fert_why,
        "soil_test_warning": fert_warning,
        "data_sources": ["USER SOIL DATA" if has_soil_test else "STANDARD AGRONOMIC SCHEDULE", "CALCULATED GROWTH STAGE"],
    }
    if fert_priority in ["CRITICAL", "HIGH", "MEDIUM"]:
        prioritized_actions.append(fertilizer_action)

    # ──────────────────────────────────────────────────────────────────────────
    # 3. DISEASE & PEST MANAGEMENT MODULE
    # ──────────────────────────────────────────────────────────────────────────
    pest_actions_list = []
    disease_actions_list = []

    # Check foliar image diagnosis
    if image_diagnosis_result and image_diagnosis_result.get("is_valid_plant"):
        foliar_dis = image_diagnosis_result.get("disease", "")
        foliar_conf = float(image_diagnosis_result.get("confidence") or 0.0)
        foliar_healthy = bool(image_diagnosis_result.get("is_healthy", False))
        foliar_sev = image_diagnosis_result.get("severity", "Medium")

        if not foliar_healthy:
            if foliar_conf < 50.0:
                # Low confidence gate
                dis_action = {
                    "id": "act_disease_low_conf",
                    "domain": "Disease",
                    "priority": "MEDIUM",
                    "title": f"Foliar Diagnosis Uncertain ({foliar_dis})",
                    "what": "Capture and upload a closer, higher-contrast leaf photo in daylight or consult your local agricultural extension officer.",
                    "when": "Within the next 24 hours",
                    "why": f"Vision model detected potential '{foliar_dis}' but confidence is low ({foliar_conf:.1f}%). Heavy chemical treatments should not be applied without definitive confirmation.",
                    "data_sources": ["PLANT VISION MODEL (LOW CONFIDENCE)"],
                }
                prioritized_actions.insert(0, dis_action)
            else:
                # Valid high confidence disease
                dis_priority = "CRITICAL" if foliar_sev in ["High", "Critical"] else "HIGH"
                treatments = image_diagnosis_result.get("treatment", {})
                bio_tr = treatments.get("biological", [])
                chem_tr = treatments.get("chemical", [])

                dis_what = f"Isolate infected foliage and initiate targeted management for {foliar_dis}."
                if bio_tr:
                    dis_what += f" Organic: {bio_tr[0]}."
                if chem_tr:
                    dis_what += f" Chemical: {chem_tr[0]}."

                dis_why = (
                    f"Confirmed foliar infection '{foliar_dis}' (Confidence: {foliar_conf:.1f}%, Severity: {foliar_sev}) "
                    f"combined with current humidity ({rh1}%) will cause rapid pathogen spore multiplication."
                )

                dis_action = {
                    "id": "act_disease_confirmed",
                    "domain": "Disease",
                    "priority": dis_priority,
                    "title": f"Disease Action: {foliar_dis}",
                    "what": dis_what,
                    "when": "Immediate action required within 24 hours",
                    "why": dis_why,
                    "cultural_practices": image_diagnosis_result.get("prevention", []),
                    "biological_options": bio_tr,
                    "chemical_options": chem_tr,
                    "safety_warning": "Adhere strictly to label safety directions, pre-harvest interval (PHI), and use personal protective gear.",
                    "data_sources": ["PLANT VISION MODEL", "LIVE WEATHER"],
                }
                prioritized_actions.insert(0, dis_action)

    # Check tabular pest outbreak risk
    if tabular_ml_result:
        top_pest = tabular_ml_result.get("top_pest", {})
        pest_name = top_pest.get("pest_name", "General Pest")
        pest_risk = top_pest.get("risk_level", "Low")
        pest_val = float(top_pest.get("pest_value", 0.0))

        if pest_risk in ["High", "Medium"]:
            p_priority = "CRITICAL" if pest_risk == "High" else "HIGH"
            pest_action = {
                "id": "act_pest_outbreak",
                "domain": "Pest",
                "priority": p_priority,
                "title": f"Pest Outbreak Alert: {pest_name}",
                "what": f"Deploy pheromone/sticky traps (5 traps/acre) and scout 20 plants diagonally across the field for {pest_name} threshold.",
                "when": "Scout field within next 24–48 hours",
                "why": (
                    f"Predictive ML model detected {pest_risk.upper()} outbreak probability ({pest_val:.1f} pest index) "
                    f"driven by current meteorological conditions (Temp: {max_t}°C, RH: {rh1}%)."
                ),
                "data_sources": ["TABULAR ML MODEL", "LIVE WEATHER"],
            }
            prioritized_actions.append(pest_action)

    # ──────────────────────────────────────────────────────────────────────────
    # 4. WEATHER-AWARE SPRAY & FIELD OPERATIONS TIMING
    # ──────────────────────────────────────────────────────────────────────────
    spray_recommended = True
    spray_notes = []
    spray_when = "Early morning (6:30 AM – 9:00 AM) or late evening (4:30 PM – 6:30 PM)"

    if rf > 5.0 or next_24h_rain > 5.0:
        spray_recommended = False
        spray_notes.append(f"Precipitation expected ({max(rf, next_24h_rain):.1f} mm): DO NOT spray foliar agrochemicals today due to imminent wash-off.")
        spray_when = "Postpone sprays until 24 hours after rain ceases"
    elif ws > 15.0:
        spray_recommended = False
        spray_notes.append(f"High wind velocity ({ws} km/h): Postpone spraying to prevent droplet drift and uneven canopy coverage.")
        spray_when = "Wait for wind speeds to drop below 12 km/h"
    elif max_t > 36.0:
        spray_notes.append(f"High temperature ({max_t}°C): Spray strictly in the early morning to prevent rapid droplet volatilization and foliar scorch.")
    else:
        spray_notes.append(f"Calm wind ({ws} km/h) and dry canopy conditions present a favorable spray window.")

    weather_action = {
        "id": "act_weather_spray",
        "domain": "Weather & Timing",
        "priority": "HIGH" if not spray_recommended else "MEDIUM",
        "title": "Foliar Spray Window & Weather Advisory",
        "what": "Foliar spray is RECOMMENDED." if spray_recommended else "Foliar spray is NOT RECOMMENDED today.",
        "when": spray_when,
        "why": " ".join(spray_notes),
        "spray_recommended": spray_recommended,
        "data_sources": ["LIVE WEATHER (OPEN-METEO)", "7-DAY FORECAST"],
    }
    if not spray_recommended:
        prioritized_actions.insert(0, weather_action)
    else:
        prioritized_actions.append(weather_action)

    # Sort prioritized actions by rank order
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    prioritized_actions.sort(key=lambda a: priority_order.get(a["priority"], 99))

    return {
        "crop": crop,
        "growth_stage": stage_name,
        "days_after_planting": dap,
        "prioritized_actions": prioritized_actions,
        "irrigation_plan": {
            "status": irrigation_status,
            "window": irrigation_window,
            "reason": irrigation_reason,
            "priority": irrigation_priority,
            "method": irrigation_method,
            "soil_moisture_level": soil_moisture,
            "forecast_rain_sum_mm": round(forecast_rf_sum, 1),
        },
        "fertilizer_plan": {
            "status": fert_status,
            "what": fert_what,
            "when": fert_window,
            "why": fert_why,
            "priority": fert_priority,
            "warning": fert_warning,
            "has_soil_test": has_soil_test,
            "soil_npk": {"n": soil_n, "p": soil_p, "k": soil_k, "ph": soil_ph},
        },
        "weather_spray_guidance": {
            "spray_recommended": spray_recommended,
            "recommended_window": spray_when,
            "notes": spray_notes,
            "wind_speed_kmh": ws,
            "rainfall_mm": rf,
            "max_temp_c": max_t,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
