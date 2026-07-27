from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_role
from app.models.user import UserRole

router = APIRouter()


@router.get("/student/dashboard")
def student_dashboard(current_user=Depends(require_role(UserRole.STUDENT.value))):
    return {"message": "Student dashboard ready", "user": current_user.full_name}


@router.get("/mentor/dashboard")
def mentor_dashboard(current_user=Depends(require_role(UserRole.MENTOR.value))):
    return {"message": "Mentor dashboard ready", "user": current_user.full_name}




