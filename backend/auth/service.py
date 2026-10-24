import os
import random
import smtplib
import types
from datetime import datetime, timedelta
from email.message import EmailMessage

from fastapi import HTTPException
try:
    from jose import jwt, JWTError
except ImportError:
    import jwt
    from jwt.exceptions import PyJWTError as JWTError

import bcrypt
# Compatibility shim for passlib 1.7.4 with modern bcrypt >= 4.0.0
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = types.SimpleNamespace(__version__=getattr(bcrypt, "__version__", "4.0.0"))

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import User, OTP, RevokedToken


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "agrishield-secret-key-change-this"
)

ALGORITHM = "HS256"

OTP_EXPIRE_MINUTES = 5


# =========================
# PASSWORD
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    if not password or not hashed_password:
        return False
    try:
        return pwd_context.verify(password, hashed_password)
    except Exception:
        return False


# =========================
# JWT
# =========================

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(days=7)
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        raise ValueError("Invalid or expired token")


def revoke_token(db: Session, token: str):
    payload = decode_token(token)

    if "sub" not in payload:
        raise ValueError("Token payload does not contain subject")

    exp = payload.get("exp")
    if isinstance(exp, int):
        expires_at = datetime.fromtimestamp(exp)
    else:
        expires_at = datetime.utcnow() + timedelta(days=7)

    existing = (
        db.query(RevokedToken)
        .filter(RevokedToken.token == token)
        .first()
    )

    if existing:
        return existing

    revoked = RevokedToken(
        token=token,
        email=payload["sub"],
        expires_at=expires_at
    )

    db.add(revoked)
    db.commit()
    db.refresh(revoked)

    return revoked


def is_token_revoked(db: Session, token: str) -> bool:
    return (
        db.query(RevokedToken)
        .filter(RevokedToken.token == token)
        .first()
        is not None
    )


def get_current_user(db: Session, authorization: str) -> User:
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
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    if is_token_revoked(db, token):
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked"
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Token payload does not contain subject"
        )

    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found for token"
        )

    return user


# =========================
# USER
# =========================

def get_user_by_email(db: Session, email: str):
    if not email:
        return None
    normalized_email = email.strip().lower()
    return (
        db.query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )


def get_user_by_phone(db: Session, phone: str):
    if not phone:
        return None
    normalized_phone = phone.strip()
    return (
        db.query(User)
        .filter(User.phone == normalized_phone)
        .first()
    )


# =========================
# OTP
# =========================

def generate_otp_code() -> str:
    return "".join(
        random.choices(
            "0123456789",
            k=6
        )
    )


# =========================
# EMAIL OTP
# =========================

def send_otp_email(
    to_email: str,
    otp_code: str,
    purpose: str
) -> bool:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL")

    if (
        not smtp_host
        or not smtp_user
        or not smtp_password
        or not smtp_from_email
    ):
        print("=" * 50)
        print("EMAIL OTP")
        print("To:", to_email)
        print("OTP:", otp_code)
        print("Expires:", OTP_EXPIRE_MINUTES, "minutes")
        print("=" * 50)
        return False

    message = EmailMessage()
    message["Subject"] = "AgriShield AI OTP Verification"
    message["From"] = smtp_from_email
    message["To"] = to_email
    message.set_content(
        f"Your AgriShield AI OTP for {purpose} is {otp_code}. "
        f"It expires in {OTP_EXPIRE_MINUTES} minutes."
    )

    try:
        with smtplib.SMTP(
            smtp_host,
            int(smtp_port),
            timeout=5
        ) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
    except Exception as exc:
        print("WARNING: OTP email could not be delivered.")
        print("Reason:", exc)
        print("EMAIL OTP")
        print("To:", to_email)
        print("OTP:", otp_code)
        print("Expires:", OTP_EXPIRE_MINUTES, "minutes")
        print("=" * 50)
        return False

    return True


# =========================
# CREATE OTP
# =========================

def create_and_send_otp(
    db: Session,
    email: str,
    phone: str,
    purpose: str
):
    otp_code = generate_otp_code()

    expires_at = (
        datetime.utcnow()
        + timedelta(minutes=OTP_EXPIRE_MINUTES)
    )

    otp_entry = OTP(
        email=email.strip().lower(),
        phone=phone.strip(),
        otp_code=otp_code,
        purpose=purpose,
        expires_at=expires_at,
        is_used=False
    )

    db.add(otp_entry)
    db.commit()

    send_otp_email(
        email,
        otp_code,
        purpose
    )


# =========================
# VERIFY OTP
# =========================

def verify_otp(
    db: Session,
    email: str,
    otp_code: str,
    purpose: str
) -> bool:
    normalized_email = email.strip().lower()
    otp_entry = (
        db.query(OTP)
        .filter(
            func.lower(OTP.email) == normalized_email,
            OTP.otp_code == otp_code.strip(),
            OTP.purpose == purpose,
            OTP.is_used == False
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not otp_entry:
        return False

    if otp_entry.expires_at < datetime.utcnow():
        return False

    otp_entry.is_used = True
    db.commit()

    return True
