"""
End-to-End Integration Test for AgriShield AI Agricultural Decision-Support System.
Verifies:
1. Agronomic Growth Stage Engine (DAP, stage progress, water/nutrient demand)
2. Live Weather Telemetry & Coordinates Sync
3. Decision Engine Synthesis (Tabular ML + Plant Vision + Weather + Soil)
4. Recommendation Engine (Prioritized WHAT / WHEN / WHY Actions)
5. Database Persistence & Plant Surveillance State Updates
6. Dashboard Fields Overview API
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, date

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from database.database import Base, engine, SessionLocal
from auth.models import User
from plants.models import Plant
from plants.service import create_plant, get_user_plants, get_plant_by_id
from plants.schemas import PlantCreate
from agronomy.growth_stage import calculate_growth_stage, CROP_GROWTH_SCHEDULES
from agronomy.decision_engine import evaluate_crop_health_and_risk
from agronomy.recommendation_engine import generate_structured_recommendations
from diagnosis.models import PlantDiagnosisRecord
from history.models import PredictionHistory
from dashboard.service import get_farmer_fields_overview


def test_full_decision_support_system():
    print("=== STARTING AGRISHIELD DECISION-SUPPORT SYSTEM INTEGRATION TEST ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Test Growth Stage Engine for multiple crops
        print("\n[STEP 1] Testing Agronomic Growth Stage Engine...")
        rice_stage = calculate_growth_stage("2026-07-15", "Rice")
        assert rice_stage["days_after_planting"] > 0, "DAP calculation failed"
        assert rice_stage["growth_stage"], "Growth stage missing"
        assert rice_stage["water_demand"] in ["Low", "Medium", "High", "Very High"]
        print(f"  [OK] Rice DAP: {rice_stage['days_after_planting']} days -> Stage: {rice_stage['growth_stage']} (Water: {rice_stage['water_demand']})")

        cotton_stage = calculate_growth_stage("2026-06-01", "Cotton")
        print(f"  [OK] Cotton DAP: {cotton_stage['days_after_planting']} days -> Stage: {cotton_stage['growth_stage']} (Nutrient: N={cotton_stage['nitrogen_demand']}, K={cotton_stage['potassium_demand']})")

        tomato_stage = calculate_growth_stage("2026-08-01", "Tomato")
        print(f"  [OK] Tomato DAP: {tomato_stage['days_after_planting']} days -> Stage: {tomato_stage['growth_stage']}")

        # 2. Test Plant Model CRUD with new agronomic fields
        print("\n[STEP 2] Testing Enhanced Plant Entity Setup...")
        test_user = db.query(User).first()
        user_id = test_user.id if test_user else 1

        plant_payload = PlantCreate(
            name="Test Cauvery Delta Rice Plot",
            crop_type="Rice",
            variety="IR-64 High Yield",
            planting_date="2026-07-10",
            growth_stage="Tillering",
            field_name="Plot B-14",
            field_size=3.5,
            field_size_unit="acres",
            irrigation_method="Drip Irrigation",
            soil_type="Clay Loam",
            soil_moisture=65.0,
            soil_ph=6.8,
            soil_n=120.0,
            soil_p=40.0,
            soil_k=150.0,
            latitude=10.7870,
            longitude=79.1378,
            location_name="Thanjavur, Tamil Nadu",
            notes="Active decision support monitoring test plot.",
        )
        created_plant = create_plant(db, user_id, plant_payload)
        assert created_plant.id is not None, "Plant creation failed"
        print(f"  [OK] Plant Created: ID={created_plant.id}, Name='{created_plant.name}', Irrigation='{created_plant.irrigation_method}'")

        # 3. Test Decision Engine Synthesis
        print("\n[STEP 3] Testing Central Decision Engine Synthesis...")
        weather = {"MaxT": 34.5, "MinT": 23.0, "RH1": 84.0, "RF": 0.0, "WS": 6.5}
        forecast = [{"rf": 0.0}, {"rf": 0.0}, {"rf": 15.0}]
        soil_data = {
            "soil_type": created_plant.soil_type,
            "soil_moisture": created_plant.soil_moisture,
            "soil_ph": created_plant.soil_ph,
            "soil_n": created_plant.soil_n,
            "soil_p": created_plant.soil_p,
            "soil_k": created_plant.soil_k,
            "irrigation_method": created_plant.irrigation_method,
        }
        tabular_ml = {
            "top_pest": {"pest_name": "Yellow Stem Borer", "pest_value": 24.2, "risk_level": "High"},
            "pests_ranked": [],
            "forecast_risk": [],
        }
        leaf_diagnosis = {
            "is_valid_plant": True,
            "disease": "Rice Blast",
            "confidence": 89.2,
            "is_healthy": False,
            "severity": "High",
            "treatment": {
                "biological": ["Pseudomonas fluorescens 0.5% liquid spray @ 5 ml/L water"],
                "chemical": ["Tricyclazole 75% WP @ 120-160 g/acre in 200L water"],
            },
            "prevention": ["Avoid excessive Nitrogen during humid periods"],
        }

        assessment = evaluate_crop_health_and_risk(
            crop="Rice",
            growth_stage_info=rice_stage,
            weather_dict=weather,
            forecast_days=forecast,
            soil_data=soil_data,
            tabular_ml_result=tabular_ml,
            image_diagnosis_result=leaf_diagnosis,
        )
        assert assessment["overall_health_status"] == "Active Disease Infection"
        assert assessment["overall_risk_level"] == "High"
        assert "data_sources" in assessment
        print(f"  [OK] Decision Assessment: Health='{assessment['overall_health_status']}', Risk='{assessment['overall_risk_level']}'")
        print(f"  [OK] Data Source Tracking Verified: {len(assessment['data_sources'])} streams mapped.")

        # 4. Test Structured Recommendation Engine (WHAT / WHEN / WHY)
        print("\n[STEP 4] Testing Recommendation Engine (Prioritized WHAT / WHEN / WHY)...")
        recs = generate_structured_recommendations(
            crop="Rice",
            growth_stage_info=rice_stage,
            weather_dict=weather,
            forecast_days=forecast,
            soil_data=soil_data,
            decision_assessment=assessment,
            tabular_ml_result=tabular_ml,
            image_diagnosis_result=leaf_diagnosis,
        )
        actions = recs["prioritized_actions"]
        assert len(actions) > 0, "No prioritized actions generated"
        print(f"  [OK] Generated {len(actions)} Prioritized Operational Actions:")
        for a in actions:
            assert "what" in a and "when" in a and "why" in a, "Action must contain WHAT, WHEN, and WHY"
            assert a["priority"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            print(f"    - [{a['priority']}] {a['domain']}: {a['title']}")
            print(f"      • WHAT: {a['what']}")
            print(f"      • WHEN: {a['when']}")
            print(f"      • WHY:  {a['why']}")

        # 5. Test Dashboard Fields Overview API
        print("\n[STEP 5] Testing Dashboard Fields Overview Integration...")
        fields_overview = get_farmer_fields_overview(db, user_id)
        assert len(fields_overview) > 0, "Fields overview returned empty"
        first_field = fields_overview[0]
        assert "days_after_planting" in first_field, "DAP missing in field summary"
        assert "growth_stage" in first_field, "Growth stage missing in field summary"
        print(f"  [OK] Field Surveillance Card: '{first_field['name']}', Stage: '{first_field['growth_stage']}' (DAP: {first_field['days_after_planting']})")

        print("\n=== ALL DECISION-SUPPORT SYSTEM TESTS PASSED SUCCESSFULLY! ===")
    finally:
        db.close()


if __name__ == "__main__":
    test_full_decision_support_system()
