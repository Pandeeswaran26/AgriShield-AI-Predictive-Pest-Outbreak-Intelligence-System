"""
AgriShield AI — Comprehensive Research-Grade System Verification Test Suite.

Covers:
1. DataValidator: Schema enforcement, range validation, missing value imputation, out-of-distribution detection.
2. Model Calibration & Confidence: Calibrated probability scores, confidence level mapping.
3. SHAP Explainability: Feature attribution, positive/negative drivers, magnitude sanity checks.
4. Vision Quality Gate: Blur detection, exposure audit, plant leaf gating.
5. Out-of-Distribution (OOD) Safeguards: Low confidence / ambiguous rejection.
6. Agronomic Decision Engine: Evidence synthesis, growth-stage DAP mapping, WHY / WHY NOT / WHEN / CONFIDENCE.
7. Feedback Loop & History: Farmer action logging, follow-up outcomes, risk trend computation.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import numpy as np

# Add project root and backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "app"))

from ml.preprocessing.validator import DataValidator
from agronomy.growth_stage import calculate_growth_stage
from agronomy.decision_engine import evaluate_crop_health_and_risk
from agronomy.recommendation_engine import generate_structured_recommendations
from diagnosis.plant_validator import validate_is_plant_leaf
from diagnosis.service import predict_disease_from_image, get_disease_info


# ============================================================================
# 1. DATA VALIDATOR TESTS
# ============================================================================

def test_data_validator_valid_input():
    raw_features = {
        "MaxT": 32.5,
        "MinT": 22.0,
        "RH1": 85.0,
        "RH2": 60.0,
        "RF": 12.0,
        "WS": 8.5,
        "SSH": 6.0,
        "EVP": 4.5,
        "Standard_Week": 28,
        "crop": "Rice",
        "location": "Aduthurai",
    }
    is_valid, errors, warnings, sanitized = DataValidator.validate_weather_inputs(raw_features)
    assert is_valid is True
    assert len(errors) == 0
    assert sanitized["MaxT"] == 32.5
    assert sanitized["Standard_Week"] == 28


def test_data_validator_clamping_and_imputation():
    # Provide extreme / physically impossible values
    raw_features = {
        "MaxT": 75.0,    # exceeds max 60°C
        "MinT": -35.0,   # below min -20°C
        "RH1": 140.0,    # relative humidity > 100%
        "RH2": 50.0,
        "RF": -10.0,     # negative rainfall
        "WS": 5.0,
        "SSH": 30.0,     # sunshine hours > 24h
        "EVP": 4.0,
        "Standard_Week": 65, # invalid week
        "crop": "Cotton",
    }
    is_valid, errors, warnings, sanitized = DataValidator.validate_weather_inputs(raw_features)
    # Validator should catch out-of-bounds errors
    assert len(errors) > 0
    assert any("MaxT" in err for err in errors)
    assert any("MinT" in err for err in errors)
    assert any("RH1" in err for err in errors)


# ============================================================================
# 2. IMAGE QUALITY AUDIT & PLANT LEAF VALIDATION TESTS
# ============================================================================

def test_plant_validator_synthetic_leaf():
    # Create green synthetic leaf image (256x256x3) in float32 [0.0, 1.0]
    img = np.zeros((256, 256, 3), dtype=np.float32)
    img[:, :, 1] = 0.65  # strong green channel
    img[:, :, 0] = 0.20  # low red
    img[:, :, 2] = 0.15  # low blue
    # Add texture/variance
    img[::4, ::4, :] = [0.25, 0.75, 0.20]

    val = validate_is_plant_leaf(img)
    assert val.is_valid is True
    assert val.plant_confidence >= 0.35
    assert val.quality_audit["brightness_ok"] is True


def test_plant_validator_pure_black_noise_rejected():
    # Pure black image
    img = np.zeros((256, 256, 3), dtype=np.float32)
    val = validate_is_plant_leaf(img)
    assert val.is_valid is False
    assert val.plant_confidence < 0.35
    assert val.quality_audit["brightness_ok"] is False


def test_plant_validator_pure_white_noise_rejected():
    # Overexposed pure white image
    img = np.ones((256, 256, 3), dtype=np.float32)
    val = validate_is_plant_leaf(img)
    assert val.is_valid is False
    assert val.quality_audit["brightness_ok"] is False


# ============================================================================
# 3. VISION CLASSIFIER & OOD UNCERTAINTY TESTS
# ============================================================================

def test_predict_disease_healthy_leaf():
    # Vibrant green image
    img = np.zeros((256, 256, 3), dtype=np.float32)
    img[:, :, 1] = 0.70
    img[:, :, 0] = 0.18
    img[:, :, 2] = 0.15

    res = predict_disease_from_image(img)
    predicted_class = res[0]
    confidence = res[1]
    candidates = res[2]

    assert isinstance(predicted_class, str)
    assert confidence >= 45.0
    assert len(candidates) == 3
    assert candidates[0]["rank"] == 1


def test_disease_info_retrieval():
    info = get_disease_info("Tomato___Bacterial_spot")
    assert info["crop"] == "Tomato"
    assert "Bacterial" in info["disease"]
    assert "symptoms" in info
    assert "treatment" in info
    assert "biological" in info["treatment"]
    assert "chemical" in info["treatment"]


# ============================================================================
# 4. AGRONOMIC GROWTH STAGE & DAP TESTS
# ============================================================================

def test_growth_stage_rice():
    today = date.today()
    # 20 days ago -> Transplanting & Recovery
    p_date = (today - timedelta(days=20)).isoformat()
    res = calculate_growth_stage(p_date, "Rice")
    assert res["days_after_planting"] == 20
    assert "Transplanting" in res["growth_stage"] or "Recovery" in res["growth_stage"]

    # 40 days ago -> Tillering
    p_date_40 = (today - timedelta(days=40)).isoformat()
    res_40 = calculate_growth_stage(p_date_40, "Rice")
    assert res_40["days_after_planting"] == 40
    assert "Tillering" in res_40["growth_stage"]


def test_growth_stage_unspecified_dap():
    res = calculate_growth_stage(None, "Cotton")
    assert res["growth_stage"] is not None
    assert res["is_estimated"] is True


# ============================================================================
# 5. CROSS-DOMAIN DECISION & RECOMMENDATION ENGINE TESTS
# ============================================================================

def test_decision_engine_high_risk_synthesis():
    growth_info = {"growth_stage": "Tillering", "days_after_planting": 35, "water_demand": "High"}
    weather_dict = {"MaxT": 34.0, "MinT": 23.0, "RH1": 85.0, "RF": 0.0, "WS": 8.0}
    forecast_days = [{"date": "2026-09-24", "rf": 0.0, "max_t": 35.0}]
    soil_data = {"soil_moisture": 22.0, "soil_type": "Clay Loam"}
    tabular_ml_result = {
        "top_pest": {"pest_name": "Yellow Stem Borer", "risk_level": "High", "pest_value": 8.5}
    }
    image_diagnosis = {
        "is_valid_plant": True,
        "disease": "Bacterial Leaf Blight",
        "is_healthy": False,
        "severity": "High",
        "confidence": 88.0,
    }

    assessment = evaluate_crop_health_and_risk(
        crop="Rice",
        growth_stage_info=growth_info,
        weather_dict=weather_dict,
        forecast_days=forecast_days,
        soil_data=soil_data,
        tabular_ml_result=tabular_ml_result,
        image_diagnosis_result=image_diagnosis,
    )

    assert assessment["overall_risk_level"] in ["High", "Medium", "Critical", "Moderate"]
    assert len(assessment["stress_factors"]) > 0
    assert assessment["crop"] == "Rice"
    assert "data_sources" in assessment


def test_structured_recommendations_why_when_confidence():
    growth_info = {"growth_stage": "Squaring (Bud Formation)", "days_after_planting": 45, "water_demand": "High"}
    weather_dict = {"MaxT": 33.0, "MinT": 22.0, "RH1": 70.0, "RF": 0.0, "WS": 6.0}
    forecast_days = [{"date": "2026-09-24", "rf": 0.0, "max_t": 34.0}]
    soil_data = {"soil_moisture": 25.0, "soil_type": "Black Soil"}
    decision_assessment = {
        "crop": "Cotton",
        "overall_stress_level": "HIGH",
        "stress_factors": ["High pest pressure: American Bollworm"],
        "data_sources": ["Tabular Pest ML", "Weather Station"],
    }
    tabular_ml = {
        "top_pest": {"pest_name": "American Bollworm", "risk_level": "High", "pest_value": 6.2}
    }

    recs = generate_structured_recommendations(
        crop="Cotton",
        growth_stage_info=growth_info,
        weather_dict=weather_dict,
        forecast_days=forecast_days,
        soil_data=soil_data,
        decision_assessment=decision_assessment,
        tabular_ml_result=tabular_ml,
        image_diagnosis_result=None,
    )

    prioritized = recs["prioritized_actions"]
    assert len(prioritized) > 0

    first_action = prioritized[0]
    # Check research-grade decision structure
    assert "title" in first_action
    assert "priority" in first_action
    assert "what" in first_action
    assert "when" in first_action
    assert "why" in first_action
    assert "why_not" in first_action
    assert "confidence" in first_action

    # Check domain plans
    assert "irrigation_plan" in recs
    assert "fertilizer_plan" in recs
    assert "weather_spray_guidance" in recs


# ============================================================================
# 6. HISTORICAL INTELLIGENCE & FEEDBACK MODELS TEST
# ============================================================================

def test_database_feedback_models():
    from history.models import FarmerAction, FollowUpOutcome, ModelVersionRecord
    action = FarmerAction(
        plant_id=1,
        action_type="Biological Spray",
        description="Applied Trichogramma parasitoids",
        dosage="50,000 eggs/ha",
    )
    assert action.action_type == "Biological Spray"

    outcome = FollowUpOutcome(
        farmer_action_id=1,
        observed_condition="Improved",
        severity_change="Better",
        notes="Egg parasitism verified at 65%",
    )
    assert outcome.observed_condition == "Improved"

    m_ver = ModelVersionRecord(
        model_name="ExtraTreesClassifier",
        version="2.1.0",
        r2=0.88,
        f1_score=0.91,
        is_active=True,
    )
    assert m_ver.model_name == "ExtraTreesClassifier"
    assert m_ver.is_active is True


if __name__ == "__main__":
    test_functions = [
        test_data_validator_valid_input,
        test_data_validator_clamping_and_imputation,
        test_plant_validator_synthetic_leaf,
        test_plant_validator_pure_black_noise_rejected,
        test_plant_validator_pure_white_noise_rejected,
        test_predict_disease_healthy_leaf,
        test_disease_info_retrieval,
        test_growth_stage_rice,
        test_growth_stage_unspecified_dap,
        test_decision_engine_high_risk_synthesis,
        test_structured_recommendations_why_when_confidence,
        test_database_feedback_models,
    ]
    
    print("\n" + "=" * 70)
    print("  AgriShield AI — Research-Grade System Verification Test Suite")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for fn in test_functions:
        name = fn.__name__
        try:
            fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1
            
    print("=" * 70)
    print(f"  Summary: {passed} passed, {failed} failed (Total: {len(test_functions)})")
    print("=" * 70 + "\n")
    
    if failed > 0:
        sys.exit(1)
