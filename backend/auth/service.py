import os
import random
import smtplib

from datetime import datetime, timedelta
from email.message import EmailMessage

from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

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


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


# =========================
# JWT
# =========================

def create_access_token(data: dict):

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


def is_token_revoked(db: Session, token: str):
    return (
        db.query(RevokedToken)
        .filter(RevokedToken.token == token)
        .first()
        is not None
    )


def get_current_user(db: Session, authorization: str):
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

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

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

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_phone(db: Session, phone: str):

    return (
        db.query(User)
        .filter(User.phone == phone)
        .first()
    )


# =========================
# OTP
# =========================

def generate_otp_code():

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
):
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
            int(smtp_port)
        ) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
    except (
        smtplib.SMTPAuthenticationError,
        smtplib.SMTPException,
        TimeoutError,
        OSError,
        ValueError
    ) as exc:
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
        email=email,
        phone=phone,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=expires_at,
        is_used=False
    )

    db.add(otp_entry)
    db.commit()

    # Send OTP to registered email address only
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
):
    otp_entry = (
        db.query(OTP)
        .filter(
            OTP.email == email,
            OTP.otp_code == otp_code,
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