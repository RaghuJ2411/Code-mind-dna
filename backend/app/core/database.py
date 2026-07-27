from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

database_url = settings.database_url
database_config = make_url(database_url)
database_backend = database_config.get_backend_name()
engine_kwargs = {
    "future": True,
    "pool_pre_ping": database_backend != "sqlite",
}

if database_backend == "sqlite":
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    if database_config.database in (None, "", ":memory:"):
        engine_kwargs["poolclass"] = StaticPool

engine = create_engine(
    database_url,
    **engine_kwargs,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
