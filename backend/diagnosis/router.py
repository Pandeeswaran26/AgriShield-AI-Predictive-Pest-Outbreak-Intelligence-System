import os
from typing import Optional
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database.database import get_db
from auth.service import decode_token, is_token_revoked, get_user_by_email
from .schemas import DiagnosisResponse, DiagnosisHistoryResponse
from .service import run_plant_diagnosis, get_user_diagnosis_history, UPLOADS_DIR
from .disease_db import CLASS_NAMES, get_disease_info

router = APIRouter(prefix="/api/plant-diagnosis", tags=["Plant Image Diagnosis"])


def _get_optional_user_id(db: Session, authorization: Optional[str] = None) -> Optional[int]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    if not token or is_token_revoked(db, token):
        return None
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email:
            user = get_user_by_email(db, email)
            return user.id if user else None
    except Exception:
        return None
    return None


@router.post("", response_model=DiagnosisResponse)
async def diagnose_plant_image(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Accepts an uploaded plant leaf image, validates it, preprocesses it,
    performs AI disease recognition, stores the diagnosis in DB,
    and returns comprehensive plant health metadata and IPM treatment plan.
    """
    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read uploaded image payload.")

    if not contents or len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty image file received.")

    user_id = _get_optional_user_id(db, authorization)

    result = run_plant_diagnosis(file=file, contents=contents, db=db, user_id=user_id)
    return result


@router.get("/history", response_model=DiagnosisHistoryResponse)
def get_history(
    limit: int = 20,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Fetches the diagnosis history for the authenticated farmer/user.
    """
    user_id = _get_optional_user_id(db, authorization)
    history_items = get_user_diagnosis_history(db, user_id=user_id, limit=limit)
    return {
        "total": len(history_items),
        "history": history_items,
    }


@router.get("/classes")
def get_supported_classes():
    """
    Returns the full taxonomy of 38 supported crop disease and healthy classes.
    """
    crops_summary = {}
    for class_key in CLASS_NAMES:
        info = get_disease_info(class_key)
        c_name = info["crop"]
        if c_name not in crops_summary:
            crops_summary[c_name] = {"diseases": [], "has_healthy_class": False}

        if info["is_healthy"]:
            crops_summary[c_name]["has_healthy_class"] = True
        else:
            crops_summary[c_name]["diseases"].append(info["disease"])

    return {
        "total_classes": len(CLASS_NAMES),
        "total_crops": len(crops_summary),
        "crops": crops_summary,
        "classes": CLASS_NAMES,
    }


@router.get("/image/{filename}")
def get_diagnosed_image(filename: str):
    """
    Serves diagnosed image for preview.
    """
    # Prevent path traversal
    safe_name = os.path.basename(filename)
    file_path = UPLOADS_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found.")
    return FileResponse(file_path)
