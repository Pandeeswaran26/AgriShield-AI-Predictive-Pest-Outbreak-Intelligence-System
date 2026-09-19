import io
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
from fastapi import UploadFile
from database.database import SessionLocal, engine, Base
from auth.models import User
from diagnosis.models import PlantDiagnosisRecord
from diagnosis.service import (
    run_plant_diagnosis,
    get_user_diagnosis_history,
    predict_disease_from_image,
    preprocess_image,
    validate_image_file,
)
from diagnosis.disease_db import CLASS_NAMES, get_disease_info


def test_diagnosis_pipeline():
    print("=== STARTING PLANT IMAGE DIAGNOSIS INTEGRATION TEST ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Verify Taxonomy & Knowledge Base
        assert len(CLASS_NAMES) == 38, f"Expected 38 classes, got {len(CLASS_NAMES)}"
        print(f"[OK] Knowledge base verified: {len(CLASS_NAMES)} classes across 14 crops.")

        apple_scab = get_disease_info("Apple___Apple_scab")
        assert apple_scab["crop"] == "Apple"
        assert apple_scab["disease"] == "Apple Scab"
        assert len(apple_scab["symptoms"]) > 0
        assert len(apple_scab["treatment"]["chemical"]) > 0
        print("[OK] Class metadata retrieval verified for 'Apple___Apple_scab'")

        # 2. Test Image Preprocessing & Descriptor Extraction
        # Create a test synthetic leaf
        test_img = Image.new("RGB", (256, 256), color=(45, 90, 39))
        for x in range(90, 150):
            for y in range(90, 150):
                test_img.putpixel((x, y), (97, 59, 22))

        buf = io.BytesIO()
        test_img.save(buf, format="JPEG")
        buf.seek(0)
        img_bytes = buf.read()

        img_arr, pil_img = preprocess_image(img_bytes)
        assert img_arr.shape == (128, 128, 3), f"Expected (128, 128, 3), got {img_arr.shape}"
        assert 0.0 <= img_arr.min() and img_arr.max() <= 1.0
        print(f"[OK] Preprocessing verified: Output shape {img_arr.shape}, range [{img_arr.min():.2f}, {img_arr.max():.2f}]")

        # 3. Test Vision Inference & Softmax Confidence
        predicted_class, confidence, candidates = predict_disease_from_image(img_arr)
        assert predicted_class in CLASS_NAMES
        assert 0.0 <= confidence <= 100.0
        assert len(candidates) == 3
        print(f"[OK] Vision Inference Result: {predicted_class} with {confidence}% confidence.")
        print(f"     Top-3 Candidates: {[c['disease'] for c in candidates]}")

        # 4. Test End-to-End Diagnosis Run & DB Persistence
        upload_file = UploadFile(
            file=io.BytesIO(img_bytes),
            filename="field_sample_leaf.jpg",
            headers={"content-type": "image/jpeg"},
        )

        user = db.query(User).first()
        user_id = user.id if user else None

        result = run_plant_diagnosis(
            file=upload_file,
            contents=img_bytes,
            db=db,
            user_id=user_id,
        )

        assert result["crop"] != ""
        assert result["disease"] != ""
        assert result["confidence"] > 0
        assert len(result["symptoms"]) > 0
        assert "treatment" in result
        print(f"[OK] Full Diagnosis Workflow executed: Crop={result['crop']}, Disease={result['disease']}, Severity={result['severity']}")

        # 5. Test History Retrieval
        history = get_user_diagnosis_history(db, user_id=user_id, limit=5)
        assert len(history) > 0
        latest = history[0]
        assert latest["crop_name"] == result["crop"]
        print(f"[OK] History retrieval verified: Latest ID={latest['id']} ({latest['crop_name']} - {latest['disease_name']})")

        print("=== ALL PLANT IMAGE DIAGNOSIS TESTS PASSED SUCCESSFULLY! ===")

    finally:
        db.close()


if __name__ == "__main__":
    test_diagnosis_pipeline()
