from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.mentor_alert import MentorRiskAlert
from app.models.user import User, UserRole
from app.schemas.mentor_alerts import (
    MentorRiskAlertCreate,
    MentorRiskAlertListResponse,
    MentorRiskAlertResponse,
    MentorAlertStatus,
    MentorAlertType,
)
from app.services.analytics.behavior_feature_service import BehaviorFeatureService

router = APIRouter(prefix="/mentor/alerts", tags=["mentor_alerts"])


def _to_response(alert: MentorRiskAlert) -> MentorRiskAlertResponse:
    return MentorRiskAlertResponse(
        id=alert.id,
        mentor_id=alert.mentor_id,
        student_id=alert.student_id,
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=alert.message,
        status=alert.status,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
    )


@router.post("", response_model=MentorRiskAlertResponse)
def create_alert(
    payload: MentorRiskAlertCreate,
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> MentorRiskAlertResponse:
    alert = MentorRiskAlert(
        mentor_id=current_user.id,
        student_id=payload.student_id,
        alert_type=payload.alert_type.value,
        severity=payload.severity.value,
        message=payload.message,
        status=MentorAlertStatus.OPEN.value,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return _to_response(alert)


@router.post("/generate", response_model=MentorRiskAlertListResponse)
def generate_alerts(
    student_id: int | None = None,
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> MentorRiskAlertListResponse:
    query = db.query(User).filter(User.role == UserRole.STUDENT)
    if student_id is not None:
        query = query.filter(User.id == student_id)

    students = query.all()
    created_alerts: list[MentorRiskAlert] = []
    feature_service = BehaviorFeatureService(db)

    for student in students:
        if student.id == current_user.id:
            continue

        profile = feature_service.build_behavior_profile(student.id, date_range_days=30)
        solve_rate = profile["success"]["solve_rate"]
        should_alert = profile["evidence_status"] in {"NO_DATA", "LIMITED_DATA"} and solve_rate < 0.4
        if not should_alert:
            continue

        existing_alert = (
            db.query(MentorRiskAlert)
            .filter(
                MentorRiskAlert.mentor_id == current_user.id,
                MentorRiskAlert.student_id == student.id,
                MentorRiskAlert.alert_type == MentorAlertType.ENGAGEMENT_DROP.value,
            )
            .first()
        )
        if existing_alert:
            continue

        alert = MentorRiskAlert(
            mentor_id=current_user.id,
            student_id=student.id,
            alert_type=MentorAlertType.ENGAGEMENT_DROP.value,
            severity="HIGH",
            message=f"{student.full_name or student.email} needs follow-up due to weak recent practice signals.",
            status=MentorAlertStatus.OPEN.value,
        )
        db.add(alert)
        created_alerts.append(alert)

    if created_alerts:
        db.commit()
        for alert in created_alerts:
            db.refresh(alert)

    return MentorRiskAlertListResponse(items=[_to_response(alert) for alert in created_alerts])


@router.get("", response_model=MentorRiskAlertListResponse)
def list_alerts(
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> MentorRiskAlertListResponse:
    items = (
        db.query(MentorRiskAlert)
        .filter(MentorRiskAlert.mentor_id == current_user.id)
        .order_by(MentorRiskAlert.created_at.desc())
        .all()
    )
    return MentorRiskAlertListResponse(items=[_to_response(item) for item in items])


@router.post("/{alert_id}/acknowledge", response_model=MentorRiskAlertResponse)
def acknowledge_alert(
    alert_id: int,
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> MentorRiskAlertResponse:
    alert = (
        db.query(MentorRiskAlert)
        .filter(MentorRiskAlert.id == alert_id, MentorRiskAlert.mentor_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = MentorAlertStatus.ACKNOWLEDGED.value
    db.commit()
    db.refresh(alert)
    return _to_response(alert)


@router.post("/{alert_id}/resolve", response_model=MentorRiskAlertResponse)
def resolve_alert(
    alert_id: int,
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> MentorRiskAlertResponse:
    alert = (
        db.query(MentorRiskAlert)
        .filter(MentorRiskAlert.id == alert_id, MentorRiskAlert.mentor_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = MentorAlertStatus.RESOLVED.value
    db.commit()
    db.refresh(alert)
    return _to_response(alert)
