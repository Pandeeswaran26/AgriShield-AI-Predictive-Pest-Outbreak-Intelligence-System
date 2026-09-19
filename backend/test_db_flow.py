import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, engine, Base
from auth.models import User
from auth.service import hash_password, create_access_token, decode_token
from plants.models import Plant
from plants.service import (
    get_user_plants,
    create_plant,
    update_plant,
    delete_plant,
    get_plant_by_id,
)
from plants.schemas import PlantCreate, PlantUpdate
from history.models import PredictionHistory
from history.service import get_all_predictions, create_auto_prediction_history
from app.prediction import predict_all_pests_for_crop, predict_forecast_risk
from recommendation.service import generate_smart_advisory
from weather.service import get_weather_snapshot_by_coordinates, get_forecast_7days

def test_full_pipeline():
    print("=== STARTING COMPLETE DATABASE INTEGRATION TEST ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Ensure test user exists
        test_email = "tester_farmer@agrishield.ai"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                name="Farmer Tester",
                email=test_email,
                phone="+919876543210",
                location="Thanjavur, Tamil Nadu",
                password=hash_password("AgriShield@2026"),
                is_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"[OK] Created test user: {user.email} (ID: {user.id})")
        else:
            print(f"[OK] Existing test user found: {user.email} (ID: {user.id})")

        # 2. Test Plant Creation
        new_plant_data = PlantCreate(
            name="Mysore Super Basmati",
            crop_type="Rice",
            variety="Pusa 1121",
            planting_date="2026-06-01",
            growth_stage="Tillering",
            field_name="Cauvery Basin East",
            field_size=5.0,
            field_size_unit="acres",
            soil_type="Clay Loam",
            soil_moisture=70.0,
            soil_ph=6.7,
            latitude=10.7870,
            longitude=79.1378,
            location_name="Thanjavur, Tamil Nadu",
            notes="Automated test rice plot",
        )
        created_plant = create_plant(db, user.id, new_plant_data)
        print(f"[OK] Plant created: {created_plant.name} (ID: {created_plant.id}, User ID: {created_plant.user_id})")

        # 3. Test Plant Update (e.g. Updating location & soil)
        update_data = PlantUpdate(
            soil_moisture=75.0,
            location_name="Madurai Rural, Tamil Nadu",
            latitude=9.9252,
            longitude=78.1198,
        )
        updated_plant = update_plant(db, created_plant.id, user.id, update_data)
        print(f"[OK] Plant updated: {updated_plant.name} -> Lat: {updated_plant.latitude}, Lon: {updated_plant.longitude}, Place: {updated_plant.location_name}, Moisture: {updated_plant.soil_moisture}%")
        assert updated_plant.soil_moisture == 75.0
        assert updated_plant.latitude == 9.9252

        # 4. Fetch User Plants
        plants = get_user_plants(db, user.id)
        print(f"[OK] User owns {len(plants)} plant records in DB.")
        assert any(p.id == updated_plant.id for p in plants)

        # 5. Fetch Live Weather & Forecast for Updated Coordinates
        snapshot = get_weather_snapshot_by_coordinates(updated_plant.latitude, updated_plant.longitude, location_label=updated_plant.location_name)
        weather_dict = snapshot.get("weather", {})
        suggested = snapshot.get("suggested_values", {})
        weather_dict["Observation_Year"] = suggested.get("Observation_Year", 2026)
        weather_dict["Standard_Week"] = suggested.get("Standard_Week", 35)
        print(f"[OK] Weather fetched for ({updated_plant.latitude}, {updated_plant.longitude}): MaxT={weather_dict.get('MaxT')}C, RH1={weather_dict.get('RH1')}%, RF={weather_dict.get('RF')}mm")

        forecast_data = get_forecast_7days(updated_plant.latitude, updated_plant.longitude, location_label=updated_plant.location_name)
        matched_loc = forecast_data.get("location", {}).get("matched_training_location") or "Madurai"
        print(f"[OK] Matched Training Location: {matched_loc}")

        # 6. Execute ML Model Prediction Pipeline
        pests_ranked = predict_all_pests_for_crop(updated_plant.crop_type, weather_dict, matched_loc)
        print(f"[OK] ML Model evaluated {len(pests_ranked)} pests. Top Threat: {pests_ranked[0]['pest_name']} ({pests_ranked[0]['risk_level']} Risk)")

        forecast_risk = predict_forecast_risk(updated_plant.crop_type, forecast_data.get("days", []), matched_loc)
        print(f"[OK] 7-Day Forecast Risk generated ({len(forecast_risk)} days)")

        advisory = generate_smart_advisory(
            crop=updated_plant.crop_type,
            top_pest=pests_ranked[0]["pest_name"],
            risk_level=pests_ranked[0]["risk_level"],
            pests_ranked=pests_ranked,
            weather_dict=weather_dict,
        )
        print(f"[OK] Smart Advisory generated: Urgency={advisory.get('urgency')}")

        # 7. Persist Prediction into Database
        pred_record = create_auto_prediction_history(
            db=db,
            crop=updated_plant.crop_type,
            location_name=matched_loc,
            location_display=updated_plant.location_name,
            latitude=updated_plant.latitude,
            longitude=updated_plant.longitude,
            weather_dict=weather_dict,
            top_pest_result=pests_ranked[0],
            pests_ranked=pests_ranked,
            forecast_risk=forecast_risk,
            advisory=advisory,
            user_id=user.id,
            plant_id=updated_plant.id,
            plant_name=updated_plant.name,
            crop_variety=updated_plant.variety,
            growth_stage=updated_plant.growth_stage,
            field_name=updated_plant.field_name,
            field_size=updated_plant.field_size,
            soil_type=updated_plant.soil_type,
            soil_moisture=updated_plant.soil_moisture,
            soil_ph=updated_plant.soil_ph,
        )
        print(f"[OK] Prediction saved to DB (ID: {pred_record.id}, Plant ID: {pred_record.plant_id})")

        # 8. Verify History Retrieval
        user_history = get_all_predictions(db, user_id=user.id)
        assert len(user_history) > 0
        latest = user_history[0]
        print(f"[OK] Retrieved latest history record: Crop={latest.crop}, Pest={latest.pest_name}, Risk={latest.risk_level}, Plant={latest.plant_name}")
        assert latest.id == pred_record.id
        assert latest.plant_id == updated_plant.id

        # 9. Clean up test plant
        delete_plant(db, created_plant.id, user.id)
        print(f"[OK] Cleaned up test plant (ID: {created_plant.id})")

        print("=== ALL DATABASE INTEGRATION TESTS PASSED SUCCESSFULLY! ===")

    finally:
        db.close()

if __name__ == "__main__":
    test_full_pipeline()
