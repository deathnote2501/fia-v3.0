"""
FIA v3.0 - User Manager
FastAPI-Users UserManager with basic hooks
"""

import uuid
import logging
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from app.infrastructure.models.trainer_model import TrainerModel
from app.infrastructure.database import get_database_session
from app.infrastructure.settings import settings

logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[TrainerModel, uuid.UUID]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: TrainerModel, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")

    async def on_after_login(
        self, user: TrainerModel, request: Optional[Request] = None, response: Optional = None
    ):
        logger.info(f"User {user.id} logged in.")


async def get_user_db(session = Depends(get_database_session)):
    yield SQLAlchemyUserDatabase(session, TrainerModel)


async def get_user_manager(user_db = Depends(get_user_db)):
    yield UserManager(user_db)