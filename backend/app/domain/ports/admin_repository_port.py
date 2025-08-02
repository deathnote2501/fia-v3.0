"""
Admin Repository Port - Domain Interface for Admin Operations
Pure domain interface without infrastructure dependencies
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AdminRepositoryPort(ABC):
    """Port for admin repository operations from domain layer"""
    
    @abstractmethod
    async def get_trainers_overview(self) -> List[Dict[str, Any]]:
        """Get comprehensive overview of all trainers with their statistics"""
        pass
    
    @abstractmethod
    async def get_global_statistics(self) -> Dict[str, Any]:
        """Get global platform statistics"""
        pass
    
    @abstractmethod
    async def get_trainer_activity(self, trainer_id: str) -> Dict[str, Any]:
        """Get specific trainer activity and statistics"""
        pass