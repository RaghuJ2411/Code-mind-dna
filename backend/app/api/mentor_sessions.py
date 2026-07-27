from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.schemas.mentor import (
    MentorSessionCreate,
    MentorSessionResponse,
    MentorSessionUpdate,
)

router = APIRouter(prefix="/mentor/sessions", tags=["mentor-sessions"])


@router.get("", response_model=list[MentorSessionResponse])
def list_sessions(
    status_filter: str | None = Query(None, alias="status"),
    session_type: str | None = Query(None),
    upcoming: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.mentor_alert import MentorRiskAlert

    query = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.mentor_id == current_user.id
    )
    # We'll use a simpler approach - query sessions from mentor alert model
    # For now return a placeholder structure that matches the schema
    sessions = []
    alerts = query.order_by(MentorRiskAlert.created_at.desc()).all()
    for alert in alerts:
        sessions.append(MentorSessionResponse(
            id=alert.id,
            mentor_id=current_user.id,
            title=f"Session re: {alert.message[:50] if alert.message else 'Follow-up'}",
            description=alert.message,
            session_type="ONE_ON_ONE",
            student_ids=[alert.student_id] if alert.student_id else [],
            scheduled_at=alert.created_at,
            duration_minutes=60,
            meeting_link=None,
            status="SCHEDULED" if alert.status == "OPEN" else "COMPLETED",
            notes=None,
            created_at=alert.created_at,
            updated_at=alert.created_at,
        ))
    return sessions


@router.post("", response_model=MentorSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: MentorSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.mentor_alert import MentorRiskAlert

    alert = MentorRiskAlert(
        mentor_id=current_user.id,
        student_id=payload.student_ids[0] if payload.student_ids else None,
        message=f"Session: {payload.title} - {payload.description or ''}",
        severity="INFO",
        category="SESSION",
        status="OPEN",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    return MentorSessionResponse(
        id=alert.id,
        mentor_id=current_user.id,
        title=payload.title,
        description=payload.description,
        session_type=payload.session_type,
        student_ids=payload.student_ids,
        scheduled_at=payload.scheduled_at,
        duration_minutes=payload.duration_minutes,
        meeting_link=payload.meeting_link,
        status=payload.status,
        notes=payload.notes,
        created_at=alert.created_at,
        updated_at=alert.created_at,
    )


@router.get("/{session_id}", response_model=MentorSessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.mentor_alert import MentorRiskAlert

    alert = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.id == session_id,
        MentorRiskAlert.mentor_id == current_user.id,
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Session not found")

    return MentorSessionResponse(
        id=alert.id,
        mentor_id=current_user.id,
        title=f"Session #{alert.id}",
        description=alert.message,
        session_type="ONE_ON_ONE",
        student_ids=[alert.student_id] if alert.student_id else [],
        scheduled_at=alert.created_at,
        duration_minutes=60,
        meeting_link=None,
        status="SCHEDULED" if alert.status == "OPEN" else "COMPLETED",
        notes=None,
        created_at=alert.created_at,
        updated_at=alert.created_at,
    )


@router.put("/{session_id}", response_model=MentorSessionResponse)
def update_session(
    session_id: int,
    payload: MentorSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.mentor_alert import MentorRiskAlert

    alert = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.id == session_id,
        MentorRiskAlert.mentor_id == current_user.id,
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Session not found")

    if payload.status:
        alert.status = "RESOLVED" if payload.status == "COMPLETED" else "OPEN"
    if payload.notes:
        alert.message = f"{alert.message}\nNotes: {payload.notes}"

    db.commit()
    db.refresh(alert)

    return MentorSessionResponse(
        id=alert.id,
        mentor_id=current_user.id,
        title=f"Session #{alert.id}",
        description=alert.message,
        session_type="ONE_ON_ONE",
        student_ids=[alert.student_id] if alert.student_id else [],
        scheduled_at=alert.created_at,
        duration_minutes=60,
        meeting_link=None,
        status="COMPLETED" if alert.status == "RESOLVED" else "SCHEDULED",
        notes=payload.notes,
        created_at=alert.created_at,
        updated_at=alert.created_at,
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.mentor_alert import MentorRiskAlert

    alert = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.id == session_id,
        MentorRiskAlert.mentor_id == current_user.id,
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(alert)
    db.commit()

