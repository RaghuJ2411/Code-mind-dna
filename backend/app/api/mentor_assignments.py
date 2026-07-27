from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.schemas.mentor import (
    MentorAssignmentCreate,
    MentorAssignmentResponse,
    MentorAssignmentUpdate,
)

router = APIRouter(prefix="/mentor/assignments", tags=["mentor-assignments"])


@router.get("", response_model=list[MentorAssignmentResponse])
def list_assignments(
    assignment_type: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.student_goal import StudentGoal

    query = db.query(StudentGoal).filter(
        StudentGoal.student_id.in_(
            db.query(User.id).filter(User.role == UserRole.STUDENT)
        )
    )
    if assignment_type:
        query = query.filter(StudentGoal.goal_type == assignment_type)

    goals = query.order_by(StudentGoal.created_at.desc()).all()
    return [
        MentorAssignmentResponse(
            id=goal.id,
            mentor_id=current_user.id,
            title=goal.title,
            description=goal.description,
            assignment_type=goal.goal_type or "CODING",
            student_ids=[goal.student_id],
            due_date=None,
            content_json={},
            max_score=100,
            passing_score=60,
            is_active=goal.status != "COMPLETED",
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )
        for goal in goals
    ]


@router.post("", response_model=MentorAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: MentorAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.student_goal import StudentGoal

    for student_id in payload.student_ids:
        goal = StudentGoal(
            student_id=student_id,
            title=payload.title,
            description=payload.description,
            goal_type=payload.assignment_type,
            target_value=payload.max_score,
            current_value=0,
            status="ACTIVE",
        )
        db.add(goal)

    db.commit()

    # Return first created goal as response
    first_goal = db.query(StudentGoal).order_by(StudentGoal.id.desc()).first()
    return MentorAssignmentResponse(
        id=first_goal.id,
        mentor_id=current_user.id,
        title=payload.title,
        description=payload.description,
        assignment_type=payload.assignment_type,
        student_ids=payload.student_ids,
        due_date=payload.due_date,
        content_json=payload.content_json,
        max_score=payload.max_score,
        passing_score=payload.passing_score,
        is_active=True,
        created_at=first_goal.created_at,
        updated_at=first_goal.updated_at,
    )


@router.get("/{assignment_id}", response_model=MentorAssignmentResponse)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.student_goal import StudentGoal

    goal = db.query(StudentGoal).filter(StudentGoal.id == assignment_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return MentorAssignmentResponse(
        id=goal.id,
        mentor_id=current_user.id,
        title=goal.title,
        description=goal.description,
        assignment_type=goal.goal_type or "CODING",
        student_ids=[goal.student_id],
        due_date=None,
        content_json={},
        max_score=100,
        passing_score=60,
        is_active=goal.status != "COMPLETED",
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


@router.put("/{assignment_id}", response_model=MentorAssignmentResponse)
def update_assignment(
    assignment_id: int,
    payload: MentorAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.student_goal import StudentGoal

    goal = db.query(StudentGoal).filter(StudentGoal.id == assignment_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if payload.title is not None:
        goal.title = payload.title
    if payload.description is not None:
        goal.description = payload.description
    if payload.is_active is not None:
        goal.status = "ACTIVE" if payload.is_active else "COMPLETED"

    db.commit()
    db.refresh(goal)

    return MentorAssignmentResponse(
        id=goal.id,
        mentor_id=current_user.id,
        title=goal.title,
        description=goal.description,
        assignment_type=goal.goal_type or "CODING",
        student_ids=[goal.student_id],
        due_date=None,
        content_json={},
        max_score=100,
        passing_score=60,
        is_active=goal.status != "COMPLETED",
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.student_goal import StudentGoal

    goal = db.query(StudentGoal).filter(StudentGoal.id == assignment_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(goal)
    db.commit()

