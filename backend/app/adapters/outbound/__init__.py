"""
FIA v3.0 - Outbound Adapters
External services and infrastructure adapters
"""

from .conversation_adapter import ConversationAdapter
from .email_adapter import EmailAdapter
from .file_storage_adapter import FileStorageAdapter

__all__ = [
    "ConversationAdapter",
    "EmailAdapter", 
    "FileStorageAdapter"
]