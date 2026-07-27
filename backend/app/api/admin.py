from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.problem import Problem
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminDashboardResponse,
    AuditLogListResponse,
    UserAdminResponse,
    UserListResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    total_users = db.scalar(select(func.count(User.id))) or 0
    active_users = db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
    role_counts = {
        role.value: db.scalar(select(func.count(User.id)).where(User.role == role)) or 0
        for role in UserRole
    }
    total_problems = db.scalar(select(func.count(Problem.id))) or 0
    active_problems = db.scalar(select(func.count(Problem.id)).where(Problem.is_active.is_(True))) or 0
    total_audit_events = db.scalar(select(func.count(AuditLog.id))) or 0
    return AdminDashboardResponse(
        total_users=total_users,
        active_users=active_users,
        role_counts=role_counts,
        total_problems=total_problems,
        active_problems=active_problems,
        total_audit_events=total_audit_events,
    )


@router.get("/users", response_model=UserListResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    role: UserRole | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    query = db.query(User)
    if search:
        pattern = f"%{search}%"
        query = query.filter((User.full_name.ilike(pattern)) | (User.email.ilike(pattern)))
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active.is_(is_active))

    total = query.count()
    items = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return UserListResponse(
        items=[UserAdminResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=max((total + page_size - 1) // page_size, 1),
    )


@router.put("/users/{user_id}", response_model=UserAdminResponse)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        if user.id == current_user.id and not payload.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate own account")
        user.is_active = payload.is_active
    user.updated_at = None
    db.commit()
    db.refresh(user)
    return UserAdminResponse.model_validate(user)


@router.get("/audit-logs", response_model=AuditLogListResponse)
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_email: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    query = db.query(AuditLog)
    if user_email:
        query = query.filter(AuditLog.user_email.ilike(f"%{user_email}%"))
    if path:
        query = query.filter(AuditLog.path.ilike(f"%{path}%"))
    if status_code is not None:
        query = query.filter(AuditLog.status_code == status_code)

    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return AuditLogListResponse(
        items=[item for item in items],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=max((total + page_size - 1) // page_size, 1),
    )
