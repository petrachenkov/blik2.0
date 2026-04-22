from .auth import router as auth_router
from .tickets import router as tickets_router
from .admin import router as admin_router

__all__ = ["auth_router", "tickets_router", "admin_router"]
