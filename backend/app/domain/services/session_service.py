"""
FIA v3.0 - Session Service
Simple service for session token generation and URL building
"""

import secrets
from app.infrastructure.settings import settings


class SessionService:
    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def build_session_url(token: str) -> str:
        return f"{settings.frontend_url}/session.html?token={token}"