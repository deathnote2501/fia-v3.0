"""
Admin Repository Port - Domain Interface for Admin Operations
Pure domain interface without infrastructure dependencies
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AdminRepositoryPort(ABC):
    """Port for admin repository operations from domain layer"""
    
    @abstractmethod
    async def get_trainers_overview_statistics(self) -> List[Dict[str, Any]]:
        """Get comprehensive overview of all trainers with their statistics"""
        pass
    
    @abstractmethod
    async def get_trainees_overview_statistics(self) -> List[Dict[str, Any]]:
        """Get comprehensive overview of all trainees with their learning statistics"""
        pass
    
    @abstractmethod
    async def get_trainings_overview_statistics(self) -> List[Dict[str, Any]]:
        """Get comprehensive overview of all trainings with their statistics"""
        pass
    
    @abstractmethod
    async def get_sessions_overview_statistics(self) -> List[Dict[str, Any]]:
        """Get comprehensive overview of all training sessions with their statistics"""
        pass
    
    @abstractmethod
    async def get_global_admin_statistics(self) -> Dict[str, Any]:
        """Get global platform statistics for admin dashboard"""
        pass