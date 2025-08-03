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
        # Normalize URL to ensure proper protocol
        normalized_url = self._normalize_frontend_url(frontend_url)
        return f"{normalized_url}/session.html?token={token}"
    
    def _normalize_frontend_url(self, frontend_url: str) -> str:
        """Normalize frontend URL to ensure it has proper protocol"""
        if not frontend_url:
            return "https://localhost:8000"
        
        # If already has protocol, return as-is
        if frontend_url.startswith(('http://', 'https://')):
            return frontend_url
        
        # Add https:// protocol for production domains
        return f"https://{frontend_url}"