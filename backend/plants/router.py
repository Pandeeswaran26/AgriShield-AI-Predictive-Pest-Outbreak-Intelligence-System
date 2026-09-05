from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from auth.models import User
from auth.service import get_current_user
from .schemas import PlantCreate, PlantUpdate, PlantResponse
from .service import (
    get_user_plants,
    get_plant_by_id,
    create_plant,
    update_plant,
    delete_plant,
)

router = APIRouter(
    prefix="/plants",
    tags=["Plants"],
)


def require_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        # Fallback for development if a demo user exists
        first_user = db.query(User).first()
        if first_user:
            return first_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return get_current_user(db, authorization)


@router.get("", response_model=List[PlantResponse])
@router.get("/", response_model=List[PlantResponse])
def list_plants(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Retrieve all plants registered by the current user."""
    return get_user_plants(db, current_user.id)


@router.post("", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
def add_plant(
    data: PlantCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Register a new plant/crop for the current user."""
    return create_plant(db, current_user.id, data)


@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant(
    plant_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get full details of a specific plant owned by the current user."""
    plant = get_plant_by_id(db, plant_id, current_user.id)
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with ID {plant_id} not found",
        )
    return plant


@router.put("/{plant_id}", response_model=PlantResponse)
@router.patch("/{plant_id}", response_model=PlantResponse)
def modify_plant(
    plant_id: int,
    data: PlantUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Update details of an existing plant."""
    updated = update_plant(db, plant_id, current_user.id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with ID {plant_id} not found or permission denied",
        )
    return updated


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_plant(
    plant_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Delete a plant record."""
    deleted = delete_plant(db, plant_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with ID {plant_id} not found or permission denied",
        )
    return None
