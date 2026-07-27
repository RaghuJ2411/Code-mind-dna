import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy.orm import Session

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Test environment configuration
os.environ["PASSWORD_REQUIRE_UPPERCASE"] = "false"
os.environ["PASSWORD_REQUIRE_LOWERCASE"] = "false"
os.environ["PASSWORD_REQUIRE_DIGIT"] = "false"
os.environ["PASSWORD_REQUIRE_SPECIAL_CHAR"] = "false"
os.environ["AUTH_RATE_LIMIT_ATTEMPTS"] = "1000"
os.environ["SECURITY_HEADERS_ENABLED"] = "false"

# Must reload settings to pick up test env vars
from app.core.config import settings
settings.password_require_uppercase = False
settings.password_require_lowercase = False
settings.password_require_digit = False
settings.password_require_special_char = False
settings.auth_rate_limit_attempts = 1000


@pytest.fixture(autouse=True)
def reset_database():
    """Reset the shared in-memory database before each test."""
    import app.models  # noqa: F401
    from app.core.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a test database session."""
    from app.core.database import SessionLocal

    session = SessionLocal()

    yield session

    session.close()
