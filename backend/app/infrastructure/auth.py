"""
FIA v3.0 - Authentication Configuration
FastAPI-Users authentication setup with Bearer transport and JWT strategy
"""

import uuid
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from app.infrastructure.settings import settings
from app.domain.entities.trainer import Trainer
from app.infrastructure.user_manager import get_user_manager

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.jwt_secret_key, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[Trainer, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Authentication dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

# Alias for training context
get_current_trainer = current_active_user