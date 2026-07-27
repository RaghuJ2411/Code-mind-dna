from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.student_goal import StudentGoal
from app.models.user import UserRole
from app.schemas.goals import StudentGoalCreate, StudentGoalResponse

router = APIRouter(prefix="/student/goals", tags=["goals"])


@router.post("", response_model=StudentGoalResponse)
def create_goal(
    payload: StudentGoalCreate,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentGoalResponse:
    goal = StudentGoal(
        student_id=current_user.id,
        goal_type=payload.goal_type.value,
        title=payload.title,
        description=payload.description,
        target_value=payload.target_value,
        current_value=0,
        period_start=payload.period_start,
        period_end=payload.period_end,
        status="ACTIVE",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return StudentGoalResponse.model_validate(goal)


@router.get("", response_model=list[StudentGoalResponse])
def list_goals(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> list[StudentGoalResponse]:
    goals = db.query(StudentGoal).filter(StudentGoal.student_id == current_user.id).all()
    return [StudentGoalResponse.model_validate(goal) for goal in goals]


@router.patch("/{goal_id}", response_model=StudentGoalResponse)
def update_goal(
    goal_id: int,
    payload: StudentGoalCreate,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentGoalResponse:
    goal = db.query(StudentGoal).filter(StudentGoal.id == goal_id, StudentGoal.student_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    goal.goal_type = payload.goal_type.value
    goal.title = payload.title
    goal.description = payload.description
    goal.target_value = payload.target_value
    goal.period_start = payload.period_start
    goal.period_end = payload.period_end
    db.commit()
    db.refresh(goal)
    return StudentGoalResponse.model_validate(goal)


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    goal = db.query(StudentGoal).filter(StudentGoal.id == goal_id, StudentGoal.student_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"status": "deleted"}
