import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    location: str = Field(..., min_length=2)
    password: str = Field(..., min_length=6)
    confirm_password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v):
        if isinstance(v, str):
            cleaned = re.sub(r"[\s\-\(\)\.]", "", v.strip())
            return cleaned
        return v

    @field_validator("name", "location", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v


class ResendOTPRequest(BaseModel):
    email: EmailStr
    purpose: str = "register"

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v


class OTPPendingResponse(BaseModel):
    message: str
    email: EmailStr


class AuthResponse(BaseModel):
    message: str
    token: str
    user_id: int
    name: str
    email: str
    phone: str
    location: str
