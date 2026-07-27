import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User

REVOKED_USER_EMAILS: set[str] = set()


def validate_password_complexity(password: str) -> None:
    """Validate password meets complexity requirements defined in settings."""
    if len(password) < settings.password_min_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at least {settings.password_min_length} characters long",
        )
    if settings.password_require_uppercase and not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one uppercase letter",
        )
    if settings.password_require_lowercase and not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one lowercase letter",
        )
    if settings.password_require_digit and not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one digit",
        )
    if settings.password_require_special_char and not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one special character",
        )


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire, "iat": int(datetime.now(timezone.utc).timestamp())}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def revoke_user(subject: str) -> None:
    """Add user to in-memory revocation set (legacy)."""
    REVOKED_USER_EMAILS.add(subject)


def is_user_revoked(subject: str) -> bool:
    """Check in-memory revocation set (legacy)."""
    return subject in REVOKED_USER_EMAILS


def revoke_user_persistent(db: Session, user_id: int) -> None:
    """Persistently revoke all tokens for a user by setting is_active=False."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()


def check_user_active(db: Session, email: str) -> bool:
    """Check if user account is active (not revoked)."""
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return False
    return user.is_active and not is_user_revoked(email)
