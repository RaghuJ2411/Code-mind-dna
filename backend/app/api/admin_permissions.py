from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.user import UserRole
from app.schemas.admin import (
    PermissionsListResponse,
    PermissionsUpdateRequest,
    RolePermissionItem,
)

router = APIRouter(prefix="/admin/permissions", tags=["admin-permissions"])


ALL_PERMISSIONS = [
    "users:read", "users:write", "users:delete",
    "problems:read", "problems:write", "problems:delete",
    "analytics:read",
    "audit:read",
    "settings:read", "settings:write",
    "reports:read", "reports:generate",
    "ai:monitor", "ai:limits",
    "system:monitor",
    "database:monitor",
]

DEFAULT_ROLE_PERMISSIONS = {
    UserRole.ADMIN.value: ALL_PERMISSIONS,
    UserRole.MENTOR.value: [
        "users:read",
        "problems:read",
        "analytics:read",
        "reports:read",
        "reports:generate",
    ],
    UserRole.RECRUITER.value: [
        "users:read",
        "analytics:read",
        "reports:read",
        "reports:generate",
    ],
    UserRole.STUDENT.value: [
        "problems:read",
        "analytics:read",
    ],
}

# In-memory store (would be DB-backed in production)
_role_permissions = {role: list(perms) for role, perms in DEFAULT_ROLE_PERMISSIONS.items()}


@router.get("", response_model=PermissionsListResponse)
def list_permissions(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    roles = [
        RolePermissionItem(
            role=role,
            permissions=perms,
            description=f"Default permissions for {role}",
        )
        for role, perms in _role_permissions.items()
    ]
    return PermissionsListResponse(roles=roles, all_permissions=ALL_PERMISSIONS)


@router.get("/roles/{role}", response_model=RolePermissionItem)
def get_role_permissions(
    role: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    if role not in _role_permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role}' not found")
    return RolePermissionItem(
        role=role,
        permissions=_role_permissions[role],
        description=f"Permissions for {role}",
    )


@router.put("/roles/{role}", response_model=RolePermissionItem)
def update_role_permissions(
    role: str,
    payload: PermissionsUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    if role not in _role_permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role}' not found")

    for perm in payload.permissions:
        if perm not in ALL_PERMISSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid permission: {perm}",
            )

    _role_permissions[role] = payload.permissions
    return RolePermissionItem(
        role=role,
        permissions=_role_permissions[role],
        description=f"Permissions for {role}",
    )

