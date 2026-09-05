from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)

    email: EmailStr

    phone: str = Field(
        ...,
        min_length=10,
        max_length=15
    )

    location: str = Field(..., min_length=2)

    password: str = Field(
        ...,
        min_length=6
    )

    confirm_password: str


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str    


class ResendOTPRequest(BaseModel):
    email: EmailStr

    purpose: str = "register"


class LoginRequest(BaseModel):
    email: EmailStr

    password: str


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