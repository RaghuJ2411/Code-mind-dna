from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.learning import LearningCourse
from app.models.user import User, UserRole
from app.schemas.mentor import (
    MentorResourceCreate,
    MentorResourceResponse,
    MentorResourceUpdate,
)

router = APIRouter(prefix="/mentor/resources", tags=["mentor-resources"])


@router.get("", response_model=list[MentorResourceResponse])
def list_resources(
    resource_type: str | None = Query(None),
    category: str | None = Query(None),
    difficulty: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    query = db.query(LearningCourse).filter(LearningCourse.is_active.is_(True))
    if category:
        query = query.filter(LearningCourse.category == category)
    if difficulty:
        query = query.filter(LearningCourse.difficulty == difficulty)
    if search:
        pattern = f"%{search}%"
        query = query.filter(LearningCourse.title.ilike(pattern))

    courses = query.order_by(LearningCourse.created_at.desc()).all()
    return [
        MentorResourceResponse(
            id=course.id,
            mentor_id=current_user.id,
            title=course.title,
            description=course.description,
            resource_type="COURSE",
            url=None,
            content=course.content_json.get("overview", "") if course.content_json else "",
            tags=course.skills_covered or [],
            difficulty=course.difficulty.upper() if course.difficulty else "INTERMEDIATE",
            category=course.category or "GENERAL",
            is_active=course.is_active,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )
        for course in courses
    ]


@router.post("", response_model=MentorResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(
    payload: MentorResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    resource = LearningCourse(
        title=payload.title,
        description=payload.description,
        category=payload.category or "GENERAL",
        difficulty=payload.difficulty.lower() if payload.difficulty else "intermediate",
        skills_covered=payload.tags or [],
        content_json={"overview": payload.content or "", "url": payload.url or ""},
        is_active=True,
        created_by=current_user.id,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)

    return MentorResourceResponse(
        id=resource.id,
        mentor_id=current_user.id,
        title=resource.title,
        description=resource.description,
        resource_type=payload.resource_type,
        url=payload.url,
        content=payload.content,
        tags=payload.tags or [],
        difficulty=payload.difficulty,
        category=payload.category,
        is_active=True,
        created_at=resource.created_at,
        updated_at=resource.updated_at,
    )


@router.get("/{resource_id}", response_model=MentorResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    course = db.query(LearningCourse).filter(
        LearningCourse.id == resource_id,
        LearningCourse.is_active.is_(True),
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Resource not found")

    return MentorResourceResponse(
        id=course.id,
        mentor_id=current_user.id,
        title=course.title,
        description=course.description,
        resource_type="COURSE",
        url=course.content_json.get("url", "") if course.content_json else "",
        content=course.content_json.get("overview", "") if course.content_json else "",
        tags=course.skills_covered or [],
        difficulty=course.difficulty.upper() if course.difficulty else "INTERMEDIATE",
        category=course.category or "GENERAL",
        is_active=course.is_active,
        created_at=course.created_at,
        updated_at=course.updated_at,
    )


@router.put("/{resource_id}", response_model=MentorResourceResponse)
def update_resource(
    resource_id: int,
    payload: MentorResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    course = db.query(LearningCourse).filter(LearningCourse.id == resource_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Resource not found")

    if payload.title is not None:
        course.title = payload.title
    if payload.description is not None:
        course.description = payload.description
    if payload.tags is not None:
        course.skills_covered = payload.tags
    if payload.difficulty is not None:
        course.difficulty = payload.difficulty.lower()
    if payload.is_active is not None:
        course.is_active = payload.is_active
    if payload.content:
        content = course.content_json or {}
        content["overview"] = payload.content
        course.content_json = content
    if payload.url:
        content = course.content_json or {}
        content["url"] = payload.url
        course.content_json = content

    db.commit()
    db.refresh(course)

    return MentorResourceResponse(
        id=course.id,
        mentor_id=current_user.id,
        title=course.title,
        description=course.description,
        resource_type=payload.resource_type or "COURSE",
        url=payload.url,
        content=payload.content,
        tags=payload.tags or [],
        difficulty=payload.difficulty or course.difficulty.upper(),
        category=course.category,
        is_active=course.is_active,
        created_at=course.created_at,
        updated_at=course.updated_at,
    )


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    course = db.query(LearningCourse).filter(LearningCourse.id == resource_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Resource not found")

    course.is_active = False
    db.commit()

