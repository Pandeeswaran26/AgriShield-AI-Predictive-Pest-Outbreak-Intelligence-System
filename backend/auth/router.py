from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db

from .models import User
from .schemas import (
    RegisterRequest,
    LoginRequest,
    OTPVerifyRequest,
    ResendOTPRequest,
    OTPPendingResponse,
    AuthResponse,
)

from .service import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_email,
    get_user_by_phone,
    create_and_send_otp,
    verify_otp,
    revoke_token,
    get_current_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =====================================================
# REGISTER
# =====================================================

@router.post(
    "/register",
    response_model=OTPPendingResponse
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Password confirmation
    if data.password != data.confirm_password:

        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    # Check email
    if get_user_by_email(
        db,
        data.email
    ):

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Check phone
    if get_user_by_phone(
        db,
        data.phone
    ):

        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )

    # Create user
    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        location=data.location,
        password=hash_password(
            data.password
        ),
        is_verified=False
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    # Send OTP to the user's email
    create_and_send_otp(
        db=db,
        email=user.email,
        phone=user.phone,
        purpose="register"
    )

    return {
        "message": "OTP sent to your email.",
        "email": user.email
    }


# =====================================================
# VERIFY REGISTRATION OTP
# =====================================================

@router.post(
    "/verify-otp",
    response_model=AuthResponse
)
def verify_registration_otp(
    data: OTPVerifyRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Account already verified"
        )

    valid = verify_otp(
    db=db,
    email=user.email,
    otp_code=data.otp,
    purpose="register"
)
    if not valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    user.is_verified = True

    db.commit()
    db.refresh(user)

    token = create_access_token(
        {
            "sub": user.email
        }
    )

    return {
        "message": "Account verified successfully",
        "token": token,
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "location": user.location
    }

# =====================================================
# RESEND OTP
# =====================================================

@router.post(
    "/resend-otp",
    response_model=OTPPendingResponse
)
def resend_otp(
    data: ResendOTPRequest,
    db: Session = Depends(get_db)
):

    user = get_user_by_email(
        db,
        data.email
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    create_and_send_otp(
        db=db,
        email=user.email,
        phone=user.phone,
        purpose=data.purpose
    )

    return {
        "message": "OTP resent successfully",
        "email": user.email
    }


# =====================================================
# LOGIN
# =====================================================

@router.post(
    "/login",
    response_model=AuthResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = get_user_by_email(
        db,
        data.email
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Check password
    if not verify_password(
        data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Must verify account first
    if not user.is_verified:

        raise HTTPException(
            status_code=403,
            detail="Account is not verified. Please verify OTP first."
        )

    token = create_access_token(
        {
            "sub": user.email
        }
    )

    return {
        "message": "Login successful",
        "token": token,
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "location": user.location
    }


# =====================================================
# LOGOUT
# =====================================================

@router.post("/logout")
def logout(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must use Bearer token"
        )

    token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Bearer token is missing"
        )

    try:
        revoke_token(db, token)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc)
        )

    return {
        "message": "Logged out successfully"
    }


@router.get("/me")
def me(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(db, authorization)

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "location": user.location
    }

