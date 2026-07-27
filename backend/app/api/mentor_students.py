from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.schemas.user import UserOut

router = APIRouter(prefix="/mentor/students", tags=["mentor_students"])


@router.get("", response_model=list[UserOut])
def list_students(
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> list[UserOut]:
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    return [UserOut(id=student.id, full_name=student.full_name, email=student.email, role=student.role) for student in students]
