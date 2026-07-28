from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    location: str
    password: str
    confirmPassword: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    location: str
    role: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    token: str