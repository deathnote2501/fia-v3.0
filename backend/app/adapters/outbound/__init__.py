"""
FIA v3.0 - Outbound Adapters
External services and infrastructure adapters
"""

from .gemini_adapter import GeminiAdapter
from .email_adapter import EmailAdapter
from .file_storage_adapter import FileStorageAdapter

__all__ = [
    "GeminiAdapter",
    "EmailAdapter", 
    "FileStorageAdapter"
]