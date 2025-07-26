"""
FIA v3.0 - Engagement Analysis Service
Domain service for analyzing learner engagement and progress
"""

import logging
from typing import Dict, Any, List
from uuid import UUID

from app.domain.ports.outbound_ports import EngagementAnalysisServicePort
from app.domain.schemas.engagement import (
    EngagementAnalysisRequest,
    EngagementAnalysisResponse,
    SlideEngagementAnalysisRequest,
    EngagementMetrics,
    LearningDifficulty,
    ProgressInsight,
    ComprehensionIndicator
)

logger = logging.getLogger(__name__)


class EngagementAnalysisService:
    """Domain service for analyzing learner engagement"""
    
    def __init__(self, engagement_port: EngagementAnalysisServicePort):
        """Initialize engagement service with port dependency"""
        self.engagement_port = engagement_port
        
    async def analyze_session_engagement(
        self, 
        analysis_request: EngagementAnalysisRequest
    ) -> EngagementAnalysisResponse:
        """
        Analyze overall engagement for a learner session
        
        Args:
            analysis_request: Request with session activity data
            
        Returns:
            EngagementAnalysisResponse with comprehensive analysis
        """
        try:
            logger.info(f"Analyzing session engagement for learner {analysis_request.learner_session_id}")
            
            # Convert activity data to dict for the port
            activity_dict = {
                "learner_session_id": str(analysis_request.activity_data.learner_session_id),
                "session_start": analysis_request.activity_data.session_start.isoformat(),
                "session_end": analysis_request.activity_data.session_end.isoformat() if analysis_request.activity_data.session_end else None,
                "total_time_spent": analysis_request.activity_data.total_time_spent,
                "slides_viewed": [
                    {
                        "slide_id": str(slide.slide_id),
                        "slide_number": slide.slide_number,
                        "time_spent": slide.time_spent,
                        "interactions": [
                            {
                                "type": interaction.interaction_type,
                                "timestamp": interaction.timestamp.isoformat(),
                                "element_id": interaction.element_id,
                                "duration": interaction.duration
                            }
                            for interaction in slide.interactions
                        ],
                        "completion_percentage": slide.completion_percentage,
                        "revisit_count": slide.revisit_count
                    }
                    for slide in analysis_request.activity_data.slides_viewed
                ],
                "chat_messages_sent": analysis_request.activity_data.chat_messages_sent,
                "questions_asked": analysis_request.activity_data.questions_asked,
                "hints_requested": analysis_request.activity_data.hints_requested
            }
            
            # Call the outbound port
            analysis_result = await self.engagement_port.analyze_session_engagement(
                learner_session_id=analysis_request.learner_session_id,
                activity_data=activity_dict
            )
            
            # Convert port response to domain schema
            metrics = EngagementMetrics(
                engagement_score=analysis_result.get("engagement_score", 75.0),
                attention_score=analysis_result.get("attention_score", 80.0),
                interaction_frequency=analysis_result.get("interaction_frequency", 5.2),
                progress_velocity=analysis_result.get("progress_velocity", 12.5),
                comprehension_indicators=analysis_result.get("comprehension_indicators", {}),
                risk_factors=analysis_result.get("risk_factors", [])
            )
            
            # Parse difficulties
            difficulties = []
            for diff_data in analysis_result.get("difficulties", []):
                difficulty = LearningDifficulty(
                    difficulty_type=diff_data.get("type", "comprehension"),
                    severity=diff_data.get("severity", "medium"),
                    evidence=diff_data.get("evidence", []),
                    affected_concepts=diff_data.get("affected_concepts", []),
                    suggested_interventions=diff_data.get("interventions", []),
                    confidence_score=diff_data.get("confidence", 0.7)
                )
                difficulties.append(difficulty)
            
            # Parse insights
            insights = []
            for insight_data in analysis_result.get("insights", []):
                insight = ProgressInsight(
                    insight_type=insight_data.get("type", "recommendation"),
                    category=insight_data.get("category", "engagement"),
                    description=insight_data.get("description", ""),
                    evidence=insight_data.get("evidence", []),
                    actionable_recommendation=insight_data.get("recommendation"),
                    priority=insight_data.get("priority", "medium")
                )
                insights.append(insight)
            
            response = EngagementAnalysisResponse(
                learner_session_id=analysis_request.learner_session_id,
                analysis_type=analysis_request.analysis_type,
                metrics=metrics,
                difficulties=difficulties,
                insights=insights,
                predictions=analysis_result.get("predictions"),
                analysis_metadata=analysis_result.get("metadata", {})
            )
            
            logger.info(f"Session analysis completed: {metrics.engagement_score}% engagement score")
            return response
            
        except Exception as e:
            logger.error(f"Failed to analyze session engagement: {str(e)}")
            raise Exception(f"Engagement analysis error: {str(e)}")
    
    async def analyze_slide_engagement(
        self, 
        slide_request: SlideEngagementAnalysisRequest
    ) -> Dict[str, Any]:
        """
        Analyze engagement for a specific slide
        
        Args:
            slide_request: Request with slide engagement data
            
        Returns:
            Analysis results for the slide
        """
        try:
            logger.info(f"Analyzing slide engagement for slide {slide_request.slide_id}")
            
            # Prepare interactions data
            interactions = [
                {
                    "type": interaction.interaction_type,
                    "timestamp": interaction.timestamp.isoformat(),
                    "element_id": interaction.element_id,
                    "coordinates": interaction.coordinates,
                    "duration": interaction.duration
                }
                for interaction in slide_request.engagement_data.interactions
            ]
            
            # Call the outbound port
            slide_analysis = await self.engagement_port.analyze_slide_engagement(
                slide_id=slide_request.slide_id,
                time_spent=slide_request.engagement_data.time_spent,
                interactions=interactions,
                learner_profile=slide_request.learner_profile
            )
            
            logger.info(f"Slide analysis completed for slide {slide_request.slide_id}")
            return slide_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze slide engagement: {str(e)}")
            raise Exception(f"Slide engagement analysis error: {str(e)}")
    
    async def detect_learning_difficulties(
        self, 
        learner_session_id: UUID,
        performance_data: Dict[str, Any]
    ) -> List[LearningDifficulty]:
        """
        Detect potential learning difficulties for a learner
        
        Args:
            learner_session_id: ID of the learner session
            performance_data: Performance and behavior data
            
        Returns:
            List of detected learning difficulties
        """
        try:
            logger.info(f"Detecting learning difficulties for session {learner_session_id}")
            
            # Call the outbound port
            difficulty_results = await self.engagement_port.detect_learning_difficulties(
                learner_session_id=learner_session_id,
                performance_data=performance_data
            )
            
            # Convert to domain objects
            difficulties = []
            for diff_data in difficulty_results.get("difficulties", []):
                difficulty = LearningDifficulty(
                    difficulty_type=diff_data.get("type", "comprehension"),
                    severity=diff_data.get("severity", "medium"),
                    evidence=diff_data.get("evidence", []),
                    affected_concepts=diff_data.get("affected_concepts", []),
                    suggested_interventions=diff_data.get("interventions", []),
                    confidence_score=diff_data.get("confidence", 0.7)
                )
                difficulties.append(difficulty)
            
            logger.info(f"Detected {len(difficulties)} potential learning difficulties")
            return difficulties
            
        except Exception as e:
            logger.error(f"Failed to detect learning difficulties: {str(e)}")
            raise Exception(f"Difficulty detection error: {str(e)}")
    
    async def generate_progress_insights(
        self, 
        learner_session_id: UUID,
        completion_data: Dict[str, Any]
    ) -> List[ProgressInsight]:
        """
        Generate insights about learner progress
        
        Args:
            learner_session_id: ID of the learner session
            completion_data: Progress and completion data
            
        Returns:
            List of progress insights and recommendations
        """
        try:
            logger.info(f"Generating progress insights for session {learner_session_id}")
            
            # Call the outbound port
            insight_results = await self.engagement_port.generate_progress_insights(
                learner_session_id=learner_session_id,
                completion_data=completion_data
            )
            
            # Convert to domain objects
            insights = []
            for insight_data in insight_results.get("insights", []):
                insight = ProgressInsight(
                    insight_type=insight_data.get("type", "recommendation"),
                    category=insight_data.get("category", "progress"),
                    description=insight_data.get("description", ""),
                    evidence=insight_data.get("evidence", []),
                    actionable_recommendation=insight_data.get("recommendation"),
                    priority=insight_data.get("priority", "medium")
                )
                insights.append(insight)
            
            logger.info(f"Generated {len(insights)} progress insights")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate progress insights: {str(e)}")
            raise Exception(f"Progress insight generation error: {str(e)}")
    
    def calculate_comprehension_indicators(
        self, 
        activity_data: Dict[str, Any],
        expected_benchmarks: Dict[str, float]
    ) -> List[ComprehensionIndicator]:
        """
        Calculate comprehension indicators from activity data
        
        Args:
            activity_data: Learner activity data
            expected_benchmarks: Expected performance benchmarks
            
        Returns:
            List of comprehension indicators
        """
        try:
            logger.info("Calculating comprehension indicators")
            
            indicators = []
            
            # Time spent indicator
            time_spent = activity_data.get("total_time_spent", 0)
            expected_time = expected_benchmarks.get("expected_time", 3600)  # 1 hour
            time_ratio = time_spent / expected_time if expected_time > 0 else 0
            
            time_indicator = ComprehensionIndicator(
                indicator_type="time_spent",
                value=time_ratio,
                interpretation="positive" if 0.8 <= time_ratio <= 1.5 else "negative" if time_ratio < 0.5 else "neutral",
                weight=0.3,
                description=f"Time spent ratio: {time_ratio:.2f} (actual: {time_spent}s, expected: {expected_time}s)"
            )
            indicators.append(time_indicator)
            
            # Interaction pattern indicator
            interaction_count = activity_data.get("total_interactions", 0)
            slides_viewed = len(activity_data.get("slides_viewed", []))
            interaction_density = interaction_count / slides_viewed if slides_viewed > 0 else 0
            
            interaction_indicator = ComprehensionIndicator(
                indicator_type="interaction_pattern",
                value=interaction_density,
                interpretation="positive" if interaction_density >= 3 else "neutral" if interaction_density >= 1 else "negative",
                weight=0.25,
                description=f"Interaction density: {interaction_density:.2f} interactions per slide"
            )
            indicators.append(interaction_indicator)
            
            # Question quality indicator
            questions_asked = activity_data.get("questions_asked", 0)
            question_quality_score = min(questions_asked / 5.0, 1.0)  # Normalize to 0-1
            
            question_indicator = ComprehensionIndicator(
                indicator_type="question_quality",
                value=question_quality_score,
                interpretation="positive" if question_quality_score >= 0.3 else "neutral",
                weight=0.25,
                description=f"Questions asked: {questions_asked} (quality score: {question_quality_score:.2f})"
            )
            indicators.append(question_indicator)
            
            # Hint usage indicator
            hints_requested = activity_data.get("hints_requested", 0)
            hint_usage_ratio = hints_requested / slides_viewed if slides_viewed > 0 else 0
            
            hint_indicator = ComprehensionIndicator(
                indicator_type="hint_usage",
                value=hint_usage_ratio,
                interpretation="neutral" if hint_usage_ratio <= 0.3 else "negative",
                weight=0.2,
                description=f"Hint usage ratio: {hint_usage_ratio:.2f} (hints: {hints_requested}, slides: {slides_viewed})"
            )
            indicators.append(hint_indicator)
            
            logger.info(f"Calculated {len(indicators)} comprehension indicators")
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to calculate comprehension indicators: {str(e)}")
            raise Exception(f"Comprehension indicator calculation error: {str(e)}")