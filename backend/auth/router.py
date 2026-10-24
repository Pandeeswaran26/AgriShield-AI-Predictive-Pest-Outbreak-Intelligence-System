import logging
import re
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

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

logger = logging.getLogger("agrishield.auth")

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
    normalized_email = data.email.strip().lower()
    normalized_phone = re.sub(r"[\s\-\(\)\.]", "", data.phone.strip())
    logger.info("Registration attempt received for email=%s", normalized_email)

    # Password confirmation validation
    if data.password != data.confirm_password:
        logger.warning("Registration failed: password mismatch for email=%s", normalized_email)
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match."
        )

    # Check email uniqueness
    existing_user = get_user_by_email(db, normalized_email)
    if existing_user:
        if existing_user.is_verified:
            logger.warning("Registration conflict: email=%s is already verified", normalized_email)
            raise HTTPException(
                status_code=409,
                detail="An account with this email already exists. Please log in."
            )
        else:
            # Re-registration for unverified account: update profile and reissue OTP
            logger.info("Re-issuing registration for unverified email=%s", normalized_email)
            # Check if updated phone clashes with another verified user
            phone_user = get_user_by_phone(db, normalized_phone)
            if phone_user and phone_user.id != existing_user.id:
                raise HTTPException(
                    status_code=409,
                    detail="An account with this phone number already exists. Please log in."
                )

            existing_user.name = data.name.strip()
            existing_user.phone = normalized_phone
            existing_user.location = data.location.strip()
            existing_user.password = hash_password(data.password)

            try:
                db.commit()
                db.refresh(existing_user)
            except IntegrityError as exc:
                db.rollback()
                logger.warning("IntegrityError updating unverified user: %s", exc)
                raise HTTPException(
                    status_code=409,
                    detail="An account with this email or phone already exists. Please log in."
                )
            except Exception as exc:
                db.rollback()
                logger.error("Database failure updating user email=%s: %s", normalized_email, exc)
                raise HTTPException(
                    status_code=500,
                    detail="Registration could not be completed. Please try again later."
                )

            create_and_send_otp(
                db=db,
                email=existing_user.email,
                phone=existing_user.phone,
                purpose="register"
            )

            return {
                "message": "OTP sent to your email.",
                "email": existing_user.email
            }

    # Check phone uniqueness for new registration
    phone_user = get_user_by_phone(db, normalized_phone)
    if phone_user:
        logger.warning("Registration conflict: phone=%s already registered", normalized_phone)
        raise HTTPException(
            status_code=409,
            detail="An account with this phone number already exists. Please log in."
        )

    # Create new user
    user = User(
        name=data.name.strip(),
        email=normalized_email,
        phone=normalized_phone,
        location=data.location.strip(),
        password=hash_password(data.password),
        is_verified=False
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        logger.warning("IntegrityError creating user email=%s: %s", normalized_email, exc)
        raise HTTPException(
            status_code=409,
            detail="An account with this email or phone already exists. Please log in."
        )
    except Exception as exc:
        db.rollback()
        logger.error("Database failure creating user email=%s: %s", normalized_email, exc)
        raise HTTPException(
            status_code=500,
            detail="Registration could not be completed. Please try again later."
        )

    # Send OTP to user's registered email
    try:
        create_and_send_otp(
            db=db,
            email=user.email,
            phone=user.phone,
            purpose="register"
        )
    except Exception as exc:
        logger.error("Error creating OTP for email=%s: %s", user.email, exc)

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
    normalized_email = data.email.strip().lower()
    user = get_user_by_email(db, normalized_email)

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
        otp_code=data.otp.strip(),
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
        "phone": user.phone or "",
        "location": user.location or ""
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
    normalized_email = data.email.strip().lower()
    user = get_user_by_email(db, normalized_email)

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
    normalized_email = data.email.strip().lower()
    logger.info("Login attempt for email=%s", normalized_email)

    try:
        user = get_user_by_email(db, normalized_email)
    except Exception as exc:
        logger.error("Database query failed during login for email=%s: %s", normalized_email, exc)
        raise HTTPException(
            status_code=500,
            detail="Database service error. Please try again later."
        )

    # If no user exists for the supplied email, explain that the user must register first
    if not user:
        logger.warning("Login failed: no user registered for email=%s", normalized_email)
        raise HTTPException(
            status_code=401,
            detail="No account found with this email. Please register first."
        )

    # Validate password
    try:
        password_matches = verify_password(data.password, user.password)
    except Exception as exc:
        logger.error("Password verification error for user_id=%s: %s", user.id, exc)
        raise HTTPException(
            status_code=500,
            detail="Authentication verification failed. Please try again."
        )

    if not password_matches:
        logger.warning("Login failed: invalid password for user_id=%s email=%s", user.id, normalized_email)
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Must verify account first
    if not user.is_verified:
        logger.warning("Login rejected: account not verified for user_id=%s", user.id)
        raise HTTPException(
            status_code=403,
            detail="Account is not verified. Please verify OTP first."
        )

    token = create_access_token(
        {
            "sub": user.email
        }
    )
    logger.info("Login successful for user_id=%s email=%s", user.id, normalized_email)

    return {
        "message": "Login successful",
        "token": token,
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone or "",
        "location": user.location or ""
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
        "phone": user.phone or "",
        "location": user.location or ""
    }
