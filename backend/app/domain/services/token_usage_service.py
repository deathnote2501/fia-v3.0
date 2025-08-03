"""
FIA v3.0 - Token Usage Service
Domain service for analyzing and aggregating AI token usage statistics
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.domain.ports.outbound_ports import LoggerAdapterPort

logger = logging.getLogger(__name__)


class TokenUsageService:
    """Domain service for managing token usage statistics and analytics"""
    
    def __init__(self, logger_adapter: LoggerAdapterPort):
        """
        Initialize service with logger adapter dependency injection
        
        Args:
            logger_adapter: Port for accessing application logs
        """
        self.logger_adapter = logger_adapter
        logger.info("🪙 TOKEN_USAGE_SERVICE [INIT] Service initialized with dependency injection")
    
    async def get_session_token_stats(
        self, 
        learner_session_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive token usage statistics for a learner session
        
        Args:
            learner_session_id: ID of the learner session
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            
        Returns:
            Dict containing comprehensive token usage data:
            - summary: Overall statistics
            - by_service_type: Breakdown by AI service type
            - recent_calls: Recent AI calls
            - cost_estimation: Estimated costs
        """
        try:
            logger.info(f"🪙 TOKEN_USAGE_SERVICE [GET_STATS] Retrieving token stats for session: {learner_session_id}")
            
            # Get base token usage data
            usage_data = await self.logger_adapter.get_token_usage_by_session(
                learner_session_id=learner_session_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Get service type breakdown
            service_breakdown = await self.logger_adapter.get_service_type_breakdown(
                learner_session_id=learner_session_id
            )
            
            # Get recent calls for timeline
            recent_calls = await self.logger_adapter.get_recent_calls(
                learner_session_id=learner_session_id,
                limit=10
            )
            
            # Calculate cost estimation (basic Gemini pricing)
            cost_estimation = self._calculate_cost_estimation(usage_data)
            
            # Build comprehensive response
            result = {
                "learner_session_id": learner_session_id,
                "query_time": datetime.now(timezone.utc).isoformat(),
                "time_range": {
                    "start_time": start_time,
                    "end_time": end_time
                },
                "summary": {
                    "total_tokens": usage_data.get("total_tokens", 0),
                    "input_tokens": usage_data.get("input_tokens", 0),
                    "output_tokens": usage_data.get("output_tokens", 0),
                    "total_calls": usage_data.get("call_count", 0),
                    "session_duration_seconds": usage_data.get("session_duration")
                },
                "by_service_type": service_breakdown,
                "recent_calls": recent_calls,
                "cost_estimation": cost_estimation,
                "metadata": {
                    "data_source": "application_logs",
                    "estimation_accuracy": "high" if self._has_real_token_data(usage_data) else "estimated"
                }
            }
            
            logger.info(f"✅ TOKEN_USAGE_SERVICE [GET_STATS] Success - Total tokens: {result['summary']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ TOKEN_USAGE_SERVICE [GET_STATS] Failed for session {learner_session_id}: {str(e)}")
            # Return default structure with error info
            return {
                "learner_session_id": learner_session_id,
                "query_time": datetime.now(timezone.utc).isoformat(),
                "error": {
                    "message": "Failed to retrieve token usage statistics",
                    "details": str(e)
                },
                "summary": {
                    "total_tokens": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_calls": 0,
                    "session_duration_seconds": None
                },
                "by_service_type": {},
                "recent_calls": [],
                "cost_estimation": {"error": "Unable to calculate costs"}
            }
    
    async def get_service_type_analytics(self, learner_session_id: str) -> Dict[str, Any]:
        """
        Get detailed analytics broken down by AI service type
        
        Args:
            learner_session_id: ID of the learner session
            
        Returns:
            Dict with service-specific analytics and insights
        """
        try:
            logger.info(f"🪙 TOKEN_USAGE_SERVICE [ANALYTICS] Analyzing service types for session: {learner_session_id}")
            
            service_breakdown = await self.logger_adapter.get_service_type_breakdown(
                learner_session_id=learner_session_id
            )
            
            # Add analytics insights
            analytics = {
                "learner_session_id": learner_session_id,
                "service_types": service_breakdown,
                "insights": self._generate_usage_insights(service_breakdown),
                "recommendations": self._generate_optimization_recommendations(service_breakdown)
            }
            
            logger.info(f"✅ TOKEN_USAGE_SERVICE [ANALYTICS] Generated insights for {len(service_breakdown)} service types")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ TOKEN_USAGE_SERVICE [ANALYTICS] Failed: {str(e)}")
            return {
                "learner_session_id": learner_session_id,
                "error": str(e),
                "service_types": {},
                "insights": [],
                "recommendations": []
            }
    
    def _calculate_cost_estimation(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate estimated costs based on token usage
        
        Args:
            usage_data: Token usage statistics
            
        Returns:
            Dict with cost estimations
        """
        # Gemini 2.0 Flash pricing (approximate)
        INPUT_TOKEN_COST_PER_1K = 0.000075  # $0.075 per 1K input tokens
        OUTPUT_TOKEN_COST_PER_1K = 0.0003    # $0.30 per 1K output tokens
        
        input_tokens = usage_data.get("input_tokens", 0)
        output_tokens = usage_data.get("output_tokens", 0)
        
        input_cost = (input_tokens / 1000) * INPUT_TOKEN_COST_PER_1K
        output_cost = (output_tokens / 1000) * OUTPUT_TOKEN_COST_PER_1K
        total_cost = input_cost + output_cost
        
        return {
            "currency": "USD",
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "cost_breakdown": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_rate_per_1k": INPUT_TOKEN_COST_PER_1K,
                "output_rate_per_1k": OUTPUT_TOKEN_COST_PER_1K
            },
            "note": "Estimated costs based on Gemini 2.0 Flash pricing"
        }
    
    def _has_real_token_data(self, usage_data: Dict[str, Any]) -> bool:
        """Check if we have real token data vs estimations"""
        return usage_data.get("total_tokens", 0) > 0
    
    def _generate_usage_insights(self, service_breakdown: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate insights from service usage patterns"""
        insights = []
        
        if not service_breakdown:
            return ["No AI service usage detected for this session"]
        
        # Find most used service
        max_tokens = 0
        most_used_service = None
        total_calls = 0
        
        for service_type, stats in service_breakdown.items():
            service_total = stats.get("input_tokens", 0) + stats.get("output_tokens", 0)
            total_calls += stats.get("calls", 0)
            
            if service_total > max_tokens:
                max_tokens = service_total
                most_used_service = service_type
        
        if most_used_service:
            insights.append(f"Most token-intensive service: {most_used_service} ({max_tokens} tokens)")
        
        insights.append(f"Total AI interactions: {total_calls} calls")
        
        # Check for conversation-heavy usage
        conversation_tokens = service_breakdown.get("conversation", {}).get("input_tokens", 0) + service_breakdown.get("conversation", {}).get("output_tokens", 0)
        if conversation_tokens > max_tokens * 0.6:
            insights.append("High conversation engagement detected - learner actively asking questions")
        
        return insights
    
    def _generate_optimization_recommendations(self, service_breakdown: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for high token usage
        total_tokens = sum(
            stats.get("input_tokens", 0) + stats.get("output_tokens", 0)
            for stats in service_breakdown.values()
        )
        
        if total_tokens > 10000:
            recommendations.append("Consider using context caching for frequently accessed training materials")
        
        # Check conversation patterns
        conversation_calls = service_breakdown.get("conversation", {}).get("calls", 0)
        if conversation_calls > 20:
            recommendations.append("High conversation activity - ensure responses are concise and helpful")
        
        if not recommendations:
            recommendations.append("Token usage is within normal ranges")
        
        return recommendations