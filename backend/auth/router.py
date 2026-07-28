from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db

from .models import User
from .schemas import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
)
from .service import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_email,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=AuthResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    if data.password != data.confirmPassword:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    existing = get_user_by_email(db, data.email)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        location=data.location,
        password=hash_password(data.password),
        role="farmer"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role
        }
    )

    return {
        "user": user,
        "token": token
    }


@router.post("/farmer/login", response_model=AuthResponse)
def farmer_login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if user.role != "farmer":
        raise HTTPException(
            status_code=403,
            detail="Not a farmer account"
        )

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role
        }
    )

    return {
        "user": user,
        "token": token
    }


@router.post("/admin/login", response_model=AuthResponse)
def admin_login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not an admin account"
        )

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role
        }
    )

    return {
        "user": user,
        "token": token
    }


@router.post("/logout")
def logout():
    return {
        "message": "Logged out successfully"
    }