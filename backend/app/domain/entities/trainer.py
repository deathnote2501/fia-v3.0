"""
FIA v3.0 - Pure Domain Trainer Entity
Business logic representation of a trainer without infrastructure dependencies
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4


class Trainer:
    """Pure domain entity representing a trainer in the system"""
    
    def __init__(
        self,
        email: str,
        first_name: str,
        last_name: str,
        trainer_id: Optional[UUID] = None,
        is_active: bool = True,
        is_verified: bool = False,
        is_superuser: bool = False,
        language: str = 'fr',
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = trainer_id or uuid4()
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.is_verified = is_verified
        self.is_superuser = is_superuser
        self.language = language
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Domain validation
        self._validate()
    
    def _validate(self) -> None:
        """Validate domain rules"""
        if not self.email or '@' not in self.email:
            raise ValueError("Valid email is required")
        
        if not self.first_name or len(self.first_name.strip()) == 0:
            raise ValueError("First name is required")
            
        if not self.last_name or len(self.last_name.strip()) == 0:
            raise ValueError("Last name is required")
        
        # Validate language code
        if self.language not in ['fr', 'en', 'es', 'de']:
            raise ValueError("Language must be one of: fr, en, es, de")
    
    def get_full_name(self) -> str:
        """Business logic: Get trainer's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def update_profile(self, first_name: Optional[str] = None, last_name: Optional[str] = None, language: Optional[str] = None) -> None:
        """Business logic: Update trainer profile"""
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if language:
            self.language = language
        self.updated_at = datetime.utcnow()
        self._validate()
    
    def set_language(self, language: str) -> None:
        """Business logic: Set trainer's preferred language"""
        self.language = language
        self.updated_at = datetime.utcnow()
        self._validate()
    
    def deactivate(self) -> None:
        """Business logic: Deactivate trainer account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Business logic: Activate trainer account"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def verify_account(self) -> None:
        """Business logic: Verify trainer account"""
        self.is_verified = True
        self.updated_at = datetime.utcnow()
    
    def grant_admin_privileges(self) -> None:
        """Business logic: Grant administrator privileges"""
        self.is_superuser = True
        self.updated_at = datetime.utcnow()
    
    def revoke_admin_privileges(self) -> None:
        """Business logic: Revoke administrator privileges"""
        self.is_superuser = False
        self.updated_at = datetime.utcnow()
    
    def has_admin_privileges(self) -> bool:
        """Business logic: Check if trainer has admin privileges"""
        return self.is_superuser and self.is_active
    
    def __str__(self) -> str:
        return f"Trainer({self.email}, {self.get_full_name()})"
    
    def __repr__(self) -> str:
        return f"Trainer(id={self.id}, email='{self.email}', name='{self.get_full_name()}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Trainer):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)