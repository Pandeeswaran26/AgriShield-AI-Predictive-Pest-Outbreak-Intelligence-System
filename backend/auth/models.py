from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)

    phone = Column(String, unique=True, index=True, nullable=False)

    location = Column(String, nullable=False)

    password = Column(String, nullable=False)

    is_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, nullable=False)

    phone = Column(String, nullable=False)

    otp_code = Column(String, nullable=False)

    purpose = Column(String, nullable=False)

    is_used = Column(Boolean, default=False, nullable=False)

    expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)

    token = Column(String, unique=True, index=True, nullable=False)

    email = Column(String, nullable=False)

    expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)