from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    full_name: str
    email: str
    photo_url: str | None = None
    phone: str | None = None
    bio: str | None = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    bio: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class SettingsResponse(BaseModel):
    theme: str = "light"
    language: str = "en"
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    profile_visibility: str = "public"
    two_factor_enabled: bool = False

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    sms_notifications: bool | None = None
    profile_visibility: str | None = None
    privacy_settings: dict | None = None


class TwoFactorEnableRequest(BaseModel):
    secret: str
    code: str


class TwoFactorVerifyRequest(BaseModel):
    code: str

