from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.problems import router as problems_router
from app.api.routes import router as protected_router

__all__ = ["auth_router", "problems_router", "admin_router", "protected_router"]
