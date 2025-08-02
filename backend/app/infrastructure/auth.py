"""
FIA v3.0 - Authentication Configuration
FastAPI-Users authentication setup with Bearer transport and JWT strategy
"""

import uuid
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from app.infrastructure.settings import settings
from app.infrastructure.models.trainer_model import TrainerModel
from app.infrastructure.user_manager import get_user_manager

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.jwt_secret_key, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[TrainerModel, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Authentication dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

# Convert to domain entity
async def get_current_trainer(
    user_model: TrainerModel = Depends(current_active_user)
) -> 'Trainer':
    """Convert TrainerModel to Trainer domain entity"""
    from app.domain.entities.trainer import Trainer
    
    return Trainer(
        email=user_model.email,
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        trainer_id=user_model.id,
        is_active=user_model.is_active,
        is_verified=user_model.is_verified,
        is_superuser=user_model.is_superuser,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at
    )