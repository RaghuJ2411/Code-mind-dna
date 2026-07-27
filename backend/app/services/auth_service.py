from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    revoke_user,
    verify_password,
    validate_password_complexity,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserCreate, UserOut


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def register(self, payload: UserCreate) -> TokenResponse:
        if self.repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        # Validate password complexity
        validate_password_complexity(payload.password)

        user = User(
            full_name=payload.full_name,
            email=str(payload.email),
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        self.repository.create(user)
        return self._build_token_response(user)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
        return self._build_token_response(user)

    def get_current_user(self, token: str) -> User:
        from app.core.security import decode_access_token

        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = self.repository.get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    def logout(self, user: User) -> None:
        revoke_user(user.email)

    def _build_token_response(self, user: User) -> TokenResponse:
        token = create_access_token(user.email)
        user_out = UserOut(id=user.id, full_name=user.full_name, email=user.email, role=user.role)
        return TokenResponse(access_token=token, user=user_out)


def require_role(*allowed_roles: UserRole):
    def role_checker(current_user: User = None):
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return current_user

    return role_checker
