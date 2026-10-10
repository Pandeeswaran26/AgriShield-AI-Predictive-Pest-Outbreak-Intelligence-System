import pytest
from irrigation.service import (
    predict_irrigation,
    get_supported_crops,
    get_model_metadata,
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_supported_crops():
    crops = get_supported_crops()
    assert isinstance(crops, list)
    assert len(crops) >= 9
    assert "Tomato" in crops
    assert "Potato" in crops
    assert "Sugarcane" in crops
    assert "Rice" in crops


def test_model_metadata():
    meta = get_model_metadata()
    assert meta["model_type"] == "RandomForestClassifier"
    assert "feature_importances" in meta
    assert "test_metrics" in meta
    assert meta["test_metrics"]["roc_auc"] >= 0.70


def test_predict_irrigation_dry_soil():
    res = predict_irrigation(
        crop_name="Tomato",
        crop_days=40,
        soil_moisture=15.0,
        soil_temperature=29.0,
        temperature=34.0,
        humidity=45.0,
        rainfall=0.0,
    )
    assert res["crop"] == "Tomato"
    assert res["irrigation_needed"] is True
    assert res["risk_level"] in ["High", "Medium"]
    assert len(res["advisory"]) > 0
    assert "timing_advice" in res


def test_predict_irrigation_high_rain_override():
    res = predict_irrigation(
        crop_name="Rice",
        crop_days=50,
        soil_moisture=38.0,
        soil_temperature=25.0,
        temperature=28.0,
        humidity=85.0,
        rainfall=25.0,
    )
    assert res["crop"] == "Rice"
    assert res["irrigation_needed"] is False
    assert res["risk_level"] == "Low"


def test_irrigation_api_endpoints():
    r_crops = client.get("/irrigation/crops")
    assert r_crops.status_code == 200
    assert "Tomato" in r_crops.json()["crops"]

    r_meta = client.get("/irrigation/metadata")
    assert r_meta.status_code == 200
    assert r_meta.json()["status"] == "success"

    r_pred = client.post(
        "/irrigation/predict",
        json={
            "crop_name": "Potato",
            "crop_days": 35,
            "soil_moisture": 14.0,
            "soil_temperature": 26.0,
            "temperature": 29.0,
            "humidity": 55.0,
            "rainfall": 0.0,
        },
    )
    assert r_pred.status_code == 200
    data = r_pred.json()["data"]
    assert data["crop"] == "Potato"
    assert "probability" in data
    assert "field_position" in data
    assert "irrigation_frequency" in data
    assert "irrigation_hours" in data


def test_irrigation_position_frequency_hours_and_email():
    res = predict_irrigation(
        crop_name="Tomato",
        crop_days=45,
        soil_moisture=12.0,
        soil_temperature=28.0,
        temperature=33.0,
        humidity=40.0,
        rainfall=0.0,
        plant_name="Roma Tomato High-Yield",
        field_position="North Ridge Sector 3",
        irrigation_frequency="2 times daily",
        irrigation_hours=2.5,
        to_email="test_farmer@agrishield.ai",
        farmer_name="Farmer Ramesh",
        send_email=True,
    )
    assert res["plant_name"] == "Roma Tomato High-Yield"
    assert res["field_position"] == "North Ridge Sector 3"
    assert res["irrigation_frequency"] == "2 times daily"
    assert res["irrigation_hours"] == 2.5
    assert res["irrigation_needed"] is True
    assert res["email_alert"] is not None
    assert res["email_alert"]["sent"] is True


def test_direct_irrigation_alert_api():
    r = client.post(
        "/irrigation/send-alert",
        json={
            "plant_name": "Sugarcane Cane-Elite",
            "crop_type": "Sugarcane",
            "field_position": "East River Basin Block 2",
            "irrigation_frequency": "Every 2 days",
            "irrigation_hours": 3.5,
            "soil_moisture": 16.5,
            "water_quantity": "35–45 mm (~350,000–450,000 L/ha)",
            "timing_advice": "Irrigate at dawn (5:30 AM – 8:00 AM)",
            "to_email": "farmer_sugarcane@agrishield.ai",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["data"]["sent"] is True
