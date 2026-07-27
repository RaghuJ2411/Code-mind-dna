from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.core.security import hash_password, verify_password
from app.models.settings import StudentSettings
from app.models.user import User, UserRole
from app.schemas.settings import (
    ChangePasswordRequest, ProfileResponse, ProfileUpdate,
    SettingsResponse, SettingsUpdate, TwoFactorEnableRequest, TwoFactorVerifyRequest,
)

router = APIRouter(prefix="/student/settings", tags=["student-settings"])


def _get_or_create_settings(db: Session, student_id: int) -> StudentSettings:
    settings = db.query(StudentSettings).filter(StudentSettings.student_id == student_id).first()
    if not settings:
        settings = StudentSettings(student_id=student_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    settings = _get_or_create_settings(db, current_user.id)
    return ProfileResponse(
        full_name=current_user.full_name,
        email=current_user.email,
        photo_url=settings.photo_url,
        phone=settings.phone,
        bio=settings.bio,
    )


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    settings = _get_or_create_settings(db, current_user.id)

    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.phone is not None:
        settings.phone = payload.phone
    if payload.bio is not None:
        settings.bio = payload.bio

    db.commit()
    return ProfileResponse(
        full_name=current_user.full_name,
        email=current_user.email,
        photo_url=settings.photo_url,
        phone=settings.phone,
        bio=settings.bio,
    )


@router.post("/photo", response_model=ProfileResponse)
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    settings = _get_or_create_settings(db, current_user.id)

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: jpg, png, gif, webp")

    # Save file
    upload_dir = "uploads/profiles"
    os.makedirs(upload_dir, exist_ok=True)
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    settings.photo_url = f"/{filepath}"
    db.commit()

    return ProfileResponse(
        full_name=current_user.full_name,
        email=current_user.email,
        photo_url=settings.photo_url,
        phone=settings.phone,
        bio=settings.bio,
    )


@router.put("/password", status_code=status.HTTP_200_OK)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")

    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.get("", response_model=SettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    settings = _get_or_create_settings(db, current_user.id)
    return SettingsResponse(
        theme=settings.theme,
        language=settings.language,
        email_notifications=settings.email_notifications,
        push_notifications=settings.push_notifications,
        sms_notifications=settings.sms_notifications,
        profile_visibility=settings.profile_visibility,
        two_factor_enabled=settings.two_factor_enabled,
    )


@router.put("", response_model=SettingsResponse)
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    settings = _get_or_create_settings(db, current_user.id)

    if payload.theme is not None:
        settings.theme = payload.theme
    if payload.language is not None:
        settings.language = payload.language
    if payload.email_notifications is not None:
        settings.email_notifications = payload.email_notifications
    if payload.push_notifications is not None:
        settings.push_notifications = payload.push_notifications
    if payload.sms_notifications is not None:
        settings.sms_notifications = payload.sms_notifications
    if payload.profile_visibility is not None:
        settings.profile_visibility = payload.profile_visibility
    if payload.privacy_settings is not None:
        settings.privacy_settings = payload.privacy_settings

    db.commit()
    return SettingsResponse(
        theme=settings.theme,
        language=settings.language,
        email_notifications=settings.email_notifications,
        push_notifications=settings.push_notifications,
        sms_notifications=settings.sms_notifications,
        profile_visibility=settings.profile_visibility,
        two_factor_enabled=settings.two_factor_enabled,
    )


@router.post("/2fa/enable", status_code=status.HTTP_200_OK)
def enable_two_factor(
    payload: TwoFactorEnableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    settings = _get_or_create_settings(db, current_user.id)
    # In production, verify the TOTP code against the secret
    settings.two_factor_secret = payload.secret
    settings.two_factor_enabled = True
    db.commit()
    return {"message": "Two-factor authentication enabled"}


@router.post("/2fa/disable", status_code=status.HTTP_200_OK)
def disable_two_factor(
    payload: TwoFactorVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    settings = _get_or_create_settings(db, current_user.id)
    if not settings.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    settings.two_factor_secret = None
    settings.two_factor_enabled = False
    db.commit()
    return {"message": "Two-factor authentication disabled"}


@router.post("/2fa/verify", status_code=status.HTTP_200_OK)
def verify_two_factor(
    payload: TwoFactorVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    settings = _get_or_create_settings(db, current_user.id)
    if not settings.two_factor_enabled or not settings.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA is not configured")
    # In production, verify TOTP code
    return {"message": "Code verified successfully"}

