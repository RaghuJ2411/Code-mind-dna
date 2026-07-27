from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.models.user import UserRole
from app.core.config import settings


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < settings.password_min_length:
            raise ValueError(f"Password must be at least {settings.password_min_length} characters long")
        if settings.password_require_uppercase and not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if settings.password_require_lowercase and not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if settings.password_require_digit and not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        if settings.password_require_special_char and not any(c in "!@#$%^&*(),.?\":{}|<>_-+=\\[\\];'/`~" for c in value):
            raise ValueError("Password must contain at least one special character")
        return value


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
