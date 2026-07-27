from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.settings import StudentSettings
from app.models.user import User, UserRole
from app.schemas.mentor import (
    MentorProfileResponse,
    MentorProfileUpdate,
)

router = APIRouter(prefix="/mentor/profile", tags=["mentor-profile"])


@router.get("", response_model=MentorProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    settings = db.query(StudentSettings).filter(
        StudentSettings.student_id == current_user.id
    ).first()

    return MentorProfileResponse(
        id=current_user.id,
        mentor_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        title=None,
        department=None,
        specialization=None,
        bio=None,
        phone=settings.phone if settings else None,
        photo_url=settings.photo_url if settings else None,
        experience_years=None,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put("", response_model=MentorProfileResponse)
def update_profile(
    payload: MentorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    settings = db.query(StudentSettings).filter(
        StudentSettings.student_id == current_user.id
    ).first()
    if not settings:
        settings = StudentSettings(student_id=current_user.id)
        db.add(settings)

    if payload.phone is not None:
        settings.phone = payload.phone
    if payload.bio is not None:
        settings.bio = payload.bio
    if payload.photo_url is not None:
        settings.photo_url = payload.photo_url

    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    db.commit()

    return MentorProfileResponse(
        id=current_user.id,
        mentor_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        title=payload.title,
        department=payload.department,
        specialization=payload.specialization,
        bio=payload.bio or settings.bio,
        phone=settings.phone,
        photo_url=settings.photo_url,
        experience_years=payload.experience_years,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/photo", response_model=MentorProfileResponse)
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    upload_dir = "uploads/mentor_profiles"
    os.makedirs(upload_dir, exist_ok=True)
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    settings = db.query(StudentSettings).filter(
        StudentSettings.student_id == current_user.id
    ).first()
    if not settings:
        settings = StudentSettings(student_id=current_user.id)
        db.add(settings)

    settings.photo_url = f"/{filepath}"
    db.commit()

    return MentorProfileResponse(
        id=current_user.id,
        mentor_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        photo_url=settings.photo_url,
        phone=settings.phone,
        bio=settings.bio,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )

