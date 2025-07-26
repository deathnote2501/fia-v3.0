"""
FIA v3.0 - Engagement Analysis Outbound Adapter
Implementation of engagement analysis service using Gemini 2.0 Flash
"""

import json
import logging
from typing import Dict, Any, List
from uuid import UUID

import google.generativeai as genai
from google.generativeai.types import GenerateContentConfig

from app.domain.ports.outbound_ports import EngagementAnalysisServicePort
from app.infrastructure.settings import settings
from app.infrastructure.rate_limiter import gemini_rate_limiter

logger = logging.getLogger(__name__)


class EngagementAdapter(EngagementAnalysisServicePort):
    """Outbound adapter for engagement analysis using Gemini AI"""
    
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_region
        )
        self.model_name = settings.gemini_model_name
        
    async def analyze_session_engagement(
        self,
        learner_session_id: UUID,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze overall session engagement metrics using AI"""
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_session_analysis_prompt(activity_data)
            
            config = GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self._get_engagement_analysis_schema(),
                temperature=0.2  # Low temperature for consistent analysis
            )
            
            response = await self.client.models.generate_content_async(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            logger.info(f"Analyzed session engagement for learner {learner_session_id}")
            
            # Parse and validate response
            analysis_result = json.loads(response.text)
            
            # Add metadata
            analysis_result["metadata"] = {
                "model_used": self.model_name,
                "tokens_used": getattr(response.usage_metadata, 'total_token_count', 0),
                "analysis_method": "ai_powered"
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze session engagement: {str(e)}")
            # Return fallback analysis
            return self._get_fallback_session_analysis(activity_data)
    
    async def analyze_slide_engagement(
        self,
        slide_id: UUID,
        time_spent: float,
        interactions: List[Dict[str, Any]],
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze engagement for a specific slide"""
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_slide_analysis_prompt(
                slide_id, time_spent, interactions, learner_profile
            )
            
            config = GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self._get_slide_analysis_schema(),
                temperature=0.3
            )
            
            response = await self.client.models.generate_content_async(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            logger.info(f"Analyzed slide engagement for slide {slide_id}")
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Failed to analyze slide engagement: {str(e)}")
            return self._get_fallback_slide_analysis(time_spent, interactions)
    
    async def detect_learning_difficulties(
        self,
        learner_session_id: UUID,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect potential learning difficulties using AI analysis"""
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_difficulty_detection_prompt(performance_data)
            
            config = GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self._get_difficulty_detection_schema(),
                temperature=0.1  # Very low temperature for consistent diagnostic analysis
            )
            
            response = await self.client.models.generate_content_async(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            logger.info(f"Detected learning difficulties for session {learner_session_id}")
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Failed to detect learning difficulties: {str(e)}")
            return {"difficulties": [], "confidence": 0.5}
    
    async def generate_progress_insights(
        self,
        learner_session_id: UUID,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights about learner progress"""
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_progress_insights_prompt(completion_data)
            
            config = GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self._get_progress_insights_schema(),
                temperature=0.4
            )
            
            response = await self.client.models.generate_content_async(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            logger.info(f"Generated progress insights for session {learner_session_id}")
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Failed to generate progress insights: {str(e)}")
            return {"insights": [], "recommendations": []}
    
    def _build_session_analysis_prompt(self, activity_data: Dict[str, Any]) -> str:
        """Build prompt for session engagement analysis"""
        
        return f"""You are an AI learning analytics expert analyzing learner engagement data.

SESSION ACTIVITY DATA:
- Total time spent: {activity_data.get('total_time_spent', 0)} seconds
- Slides viewed: {len(activity_data.get('slides_viewed', []))} slides
- Chat messages sent: {activity_data.get('chat_messages_sent', 0)}
- Questions asked: {activity_data.get('questions_asked', 0)}
- Hints requested: {activity_data.get('hints_requested', 0)}
- Session duration: {activity_data.get('session_duration', 'unknown')}

SLIDE ENGAGEMENT DETAILS:
{self._format_slide_data(activity_data.get('slides_viewed', []))}

TASK:
Analyze this learner's engagement and provide comprehensive metrics and insights.

Consider:
1. Time spent patterns (too fast, appropriate, or too slow)
2. Interaction frequency and quality
3. Help-seeking behavior (questions and hints)
4. Progression patterns through slides
5. Potential engagement issues or strengths

Calculate engagement scores on a 0-100 scale and identify any risk factors."""
    
    def _build_slide_analysis_prompt(
        self, 
        slide_id: UUID, 
        time_spent: float, 
        interactions: List[Dict[str, Any]],
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build prompt for slide-specific analysis"""
        
        interaction_summary = f"Total interactions: {len(interactions)}\n"
        for interaction in interactions[:5]:  # First 5 interactions
            interaction_summary += f"- {interaction.get('type', 'unknown')} at {interaction.get('timestamp', 'unknown')}\n"
        
        return f"""Analyze engagement for a specific slide in a training session.

SLIDE DETAILS:
- Slide ID: {slide_id}
- Time spent: {time_spent} seconds
- Total interactions: {len(interactions)}

LEARNER PROFILE:
- Experience level: {learner_profile.get('experience_level', 'unknown')}
- Learning style: {learner_profile.get('learning_style', 'unknown')}

INTERACTION DETAILS:
{interaction_summary}

TASK:
Analyze this slide's engagement patterns and determine:
1. Whether time spent is appropriate for the content
2. Quality and frequency of interactions
3. Signs of confusion or mastery
4. Recommendations for this specific slide"""
    
    def _build_difficulty_detection_prompt(self, performance_data: Dict[str, Any]) -> str:
        """Build prompt for learning difficulty detection"""
        
        return f"""You are an educational psychologist analyzing performance data to detect learning difficulties.

PERFORMANCE DATA:
- Completion rate: {performance_data.get('completion_rate', 0)}%
- Average time per slide: {performance_data.get('avg_time_per_slide', 0)} seconds
- Question accuracy: {performance_data.get('question_accuracy', 'unknown')}%
- Help requests: {performance_data.get('help_requests', 0)}
- Struggle indicators: {performance_data.get('struggle_indicators', [])}
- Behavioral patterns: {performance_data.get('behavioral_patterns', [])}

TASK:
Identify potential learning difficulties and their severity levels.

Look for patterns indicating:
1. Comprehension difficulties (slow progress, many questions)
2. Attention issues (quick skipping, low interaction)
3. Pace problems (too fast or too slow)
4. Motivation issues (abandonment patterns)
5. Technical difficulties (interaction problems)

Provide evidence-based assessments with confidence scores."""
    
    def _build_progress_insights_prompt(self, completion_data: Dict[str, Any]) -> str:
        """Build prompt for progress insights generation"""
        
        return f"""Generate insights about learner progress and provide actionable recommendations.

COMPLETION DATA:
- Overall progress: {completion_data.get('progress_percentage', 0)}%
- Modules completed: {completion_data.get('modules_completed', 0)}
- Skills demonstrated: {completion_data.get('skills_demonstrated', [])}
- Knowledge gaps: {completion_data.get('knowledge_gaps', [])}
- Strengths identified: {completion_data.get('strengths', [])}
- Learning velocity: {completion_data.get('learning_velocity', 'unknown')}

TASK:
Generate meaningful insights and recommendations including:

1. Strengths to build upon
2. Areas needing improvement
3. Personalized recommendations
4. Next steps for continued learning
5. Achievement recognition

Focus on actionable, encouraging, and specific guidance."""
    
    def _format_slide_data(self, slides_data: List[Dict[str, Any]]) -> str:
        """Format slide engagement data for prompt"""
        if not slides_data:
            return "No slide data available"
        
        formatted = ""
        for slide in slides_data[:10]:  # First 10 slides
            formatted += f"Slide {slide.get('slide_number', '?')}: "
            formatted += f"{slide.get('time_spent', 0)}s, "
            formatted += f"{len(slide.get('interactions', []))} interactions, "
            formatted += f"{slide.get('completion_percentage', 0)}% complete\n"
        
        return formatted
    
    def _get_engagement_analysis_schema(self) -> Dict[str, Any]:
        """JSON schema for engagement analysis response"""
        return {
            "type": "object",
            "properties": {
                "engagement_score": {"type": "number", "minimum": 0, "maximum": 100},
                "attention_score": {"type": "number", "minimum": 0, "maximum": 100},
                "interaction_frequency": {"type": "number", "minimum": 0},
                "progress_velocity": {"type": "number", "minimum": 0},
                "comprehension_indicators": {"type": "object"},
                "risk_factors": {"type": "array", "items": {"type": "string"}},
                "difficulties": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "severity": {"type": "string"},
                            "evidence": {"type": "array", "items": {"type": "string"}},
                            "affected_concepts": {"type": "array", "items": {"type": "string"}},
                            "interventions": {"type": "array", "items": {"type": "string"}},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                },
                "insights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "category": {"type": "string"},
                            "description": {"type": "string"},
                            "evidence": {"type": "array", "items": {"type": "string"}},
                            "recommendation": {"type": "string"},
                            "priority": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["engagement_score", "attention_score", "interaction_frequency", "progress_velocity"]
        }
    
    def _get_slide_analysis_schema(self) -> Dict[str, Any]:
        """JSON schema for slide analysis response"""
        return {
            "type": "object",
            "properties": {
                "engagement_level": {"type": "string"},
                "time_appropriateness": {"type": "string"},
                "interaction_quality": {"type": "string"},
                "comprehension_indicators": {"type": "object"},
                "recommendations": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["engagement_level", "time_appropriateness", "interaction_quality"]
        }
    
    def _get_difficulty_detection_schema(self) -> Dict[str, Any]:
        """JSON schema for difficulty detection response"""
        return {
            "type": "object",
            "properties": {
                "difficulties": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "severity": {"type": "string"},
                            "evidence": {"type": "array", "items": {"type": "string"}},
                            "affected_concepts": {"type": "array", "items": {"type": "string"}},
                            "interventions": {"type": "array", "items": {"type": "string"}},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                },
                "overall_risk_level": {"type": "string"},
                "priority_interventions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["difficulties"]
        }
    
    def _get_progress_insights_schema(self) -> Dict[str, Any]:
        """JSON schema for progress insights response"""
        return {
            "type": "object",
            "properties": {
                "insights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "category": {"type": "string"},
                            "description": {"type": "string"},
                            "evidence": {"type": "array", "items": {"type": "string"}},
                            "recommendation": {"type": "string"},
                            "priority": {"type": "string"}
                        }
                    }
                },
                "next_steps": {"type": "array", "items": {"type": "string"}},
                "achievements": {"type": "array", "items": {"type": "string"}},
                "focus_areas": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["insights"]
        }
    
    def _get_fallback_session_analysis(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        slides_viewed = len(activity_data.get('slides_viewed', []))
        time_spent = activity_data.get('total_time_spent', 0)
        
        # Simple rule-based engagement calculation
        engagement_score = min(100, max(0, slides_viewed * 10 + (time_spent / 60)))
        
        return {
            "engagement_score": engagement_score,
            "attention_score": 75.0,
            "interaction_frequency": activity_data.get('chat_messages_sent', 0) / max(1, time_spent / 60),
            "progress_velocity": slides_viewed / max(1, time_spent / 3600),
            "comprehension_indicators": {},
            "risk_factors": [] if engagement_score > 50 else ["Low engagement detected"],
            "difficulties": [],
            "insights": [],
            "metadata": {"fallback": True, "reason": "AI analysis unavailable"}
        }
    
    def _get_fallback_slide_analysis(
        self, 
        time_spent: float, 
        interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback slide analysis when AI fails"""
        return {
            "engagement_level": "moderate" if time_spent > 30 else "low",
            "time_appropriateness": "appropriate" if 30 <= time_spent <= 300 else "inappropriate",
            "interaction_quality": "good" if len(interactions) > 2 else "limited",
            "comprehension_indicators": {},
            "recommendations": ["Continue with current pace"],
            "metadata": {"fallback": True}
        }