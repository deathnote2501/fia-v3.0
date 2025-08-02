"""
FIA v3.0 - Session Service
Simple service for session token generation and URL building
"""

import secrets
from app.domain.ports.settings_port import SettingsPort


class SessionService:
    def __init__(self, settings_port: SettingsPort):
        self.settings = settings_port
    
    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)
    
    def build_session_url(self, token: str) -> str:
        frontend_url = self.settings.get_setting('FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/session.html?token={token}"