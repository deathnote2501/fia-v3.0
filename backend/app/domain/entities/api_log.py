"""
FIA v3.0 - Pure Domain API Log Entity
Business logic representation of an API log without infrastructure dependencies
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class ApiLog:
    """Pure domain entity representing an API log in the system"""
    
    def __init__(
        self,
        service_name: str,
        endpoint: str,
        method: str,
        api_log_id: Optional[UUID] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        cost_estimate: Optional[str] = None,
        learner_session_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = api_log_id or uuid4()
        self.service_name = service_name
        self.endpoint = endpoint
        self.method = method
        self.request_data = request_data or {}
        self.response_data = response_data or {}
        self.status_code = status_code
        self.response_time_ms = response_time_ms
        self.tokens_used = tokens_used
        self.cost_estimate = cost_estimate
        self.learner_session_id = learner_session_id
        self.created_at = created_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate business rules for API log"""
        if not self.service_name.strip():
            raise ValueError("Service name is required")
        
        if not self.endpoint.strip():
            raise ValueError("Endpoint is required")
        
        if not self.method.strip():
            raise ValueError("HTTP method is required")
        
        if self.status_code is not None and (self.status_code < 100 or self.status_code > 599):
            raise ValueError("Status code must be between 100 and 599")
        
        if self.response_time_ms is not None and self.response_time_ms < 0:
            raise ValueError("Response time cannot be negative")
        
        if self.tokens_used is not None and self.tokens_used < 0:
            raise ValueError("Tokens used cannot be negative")
    
    def is_successful(self) -> bool:
        """Check if the API call was successful"""
        return self.status_code is not None and 200 <= self.status_code < 300
    
    def is_error(self) -> bool:
        """Check if the API call resulted in an error"""
        return self.status_code is not None and self.status_code >= 400
    
    def get_performance_category(self) -> str:
        """Get performance category based on response time"""
        if self.response_time_ms is None:
            return "unknown"
        elif self.response_time_ms < 500:
            return "fast"
        elif self.response_time_ms < 2000:
            return "medium"
        else:
            return "slow"
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get a summary of the API log"""
        return {
            "id": str(self.id),
            "service": self.service_name,
            "endpoint": self.endpoint,
            "method": self.method,
            "status": self.status_code,
            "success": self.is_successful(),
            "response_time_ms": self.response_time_ms,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def calculate_estimated_cost(self, cost_per_token: float = 0.0001) -> float:
        """Calculate estimated cost based on tokens used"""
        if self.tokens_used is None:
            return 0.0
        return self.tokens_used * cost_per_token
    
    def add_learner_context(self, learner_session_id: UUID) -> None:
        """Add learner session context to the log"""
        self.learner_session_id = learner_session_id
    
    def update_response_metrics(
        self, 
        status_code: int, 
        response_time_ms: int, 
        response_data: Dict[str, Any],
        tokens_used: Optional[int] = None
    ) -> None:
        """Update response metrics for the API call"""
        self.status_code = status_code
        self.response_time_ms = response_time_ms
        self.response_data = response_data
        if tokens_used is not None:
            self.tokens_used = tokens_used
        
        # Re-validate after update
        self._validate()