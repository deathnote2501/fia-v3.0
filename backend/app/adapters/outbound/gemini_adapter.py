"""
FIA v3.0 - Gemini Outbound Adapter
Implementation of Gemini AI service interactions
"""

import json
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

import google.generativeai as genai
from google.generativeai.types import GenerateContentConfig

from app.domain.ports.outbound_ports import GeminiServicePort
from app.infrastructure.settings import settings
from app.infrastructure.rate_limiter import gemini_rate_limiter, RateLimitExceeded


logger = logging.getLogger(__name__)


class GeminiAdapter(GeminiServicePort):
    """Outbound adapter for Gemini AI service"""
    
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_region
        )
        self.model_name = settings.gemini_model_name
        
    async def generate_training_plan(
        self, 
        learner_profile: Dict[str, Any], 
        training_content: str,
        context_cache_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate personalized training plan using Gemini"""
        try:
            # Apply rate limiting before API call
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_training_plan_prompt(learner_profile, training_content)
            
            config = GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self._get_training_plan_schema(),
                temperature=0.1
            )
            
            # Use context cache if available
            cache_args = {}
            if context_cache_id:
                cache_args["cached_content"] = context_cache_id
            
            response = await self.client.agenerate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
                **cache_args
            )
            
            result = json.loads(response.text)
            
            # Log the API call
            await self._log_api_call(
                operation_type="generate_plan",
                request_data={"profile": learner_profile, "cache_used": bool(context_cache_id)},
                response_data=result,
                response_time_ms=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            )
            
            return result
            
        except RateLimitExceeded as e:
            logger.warning(f"Rate limit exceeded for training plan generation: {str(e)}")
            await self._log_api_call(
                operation_type="generate_plan",
                request_data={"profile": learner_profile},
                response_data={"error": f"Rate limit exceeded: {str(e)}"},
                response_time_ms=0
            )
            raise
        except Exception as e:
            logger.error(f"Error generating training plan: {str(e)}")
            await self._log_api_call(
                operation_type="generate_plan",
                request_data={"profile": learner_profile},
                response_data={"error": str(e)},
                response_time_ms=0
            )
            raise
    
    async def generate_slide_content(
        self,
        slide_title: str,
        module_context: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate slide content using Gemini"""
        try:
            # Apply rate limiting before API call
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_slide_content_prompt(slide_title, module_context, learner_profile)
            
            config = GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self._get_slide_content_schema(),
                temperature=0.3
            )
            
            response = await self.client.agenerate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            result = json.loads(response.text)
            
            await self._log_api_call(
                operation_type="generate_slide",
                request_data={"title": slide_title, "profile": learner_profile},
                response_data=result,
                response_time_ms=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating slide content: {str(e)}")
            await self._log_api_call(
                operation_type="generate_slide",
                request_data={"title": slide_title},
                response_data={"error": str(e)},
                response_time_ms=0
            )
            raise
    
    async def chat_with_learner(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        training_context: str
    ) -> str:
        """Handle learner chat interactions"""
        try:
            # Apply rate limiting before API call
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_chat_prompt(message, conversation_history, training_context)
            
            config = GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
            
            response = await self.client.agenerate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            result = response.text
            
            await self._log_api_call(
                operation_type="chat",
                request_data={"message": message, "history_length": len(conversation_history)},
                response_data={"response": result},
                response_time_ms=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in chat interaction: {str(e)}")
            await self._log_api_call(
                operation_type="chat",
                request_data={"message": message},
                response_data={"error": str(e)},
                response_time_ms=0
            )
            raise
    
    async def analyze_engagement(
        self,
        learner_session_id: UUID,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze learner engagement"""
        try:
            # Apply rate limiting before API call
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_engagement_analysis_prompt(activity_data)
            
            config = GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self._get_engagement_analysis_schema(),
                temperature=0.1
            )
            
            response = await self.client.agenerate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            result = json.loads(response.text)
            
            await self._log_api_call(
                operation_type="analyze_engagement",
                request_data={"session_id": str(learner_session_id), "activity": activity_data},
                response_data=result,
                response_time_ms=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {str(e)}")
            await self._log_api_call(
                operation_type="analyze_engagement",
                request_data={"session_id": str(learner_session_id)},
                response_data={"error": str(e)},
                response_time_ms=0
            )
            raise
    
    def _build_training_plan_prompt(self, learner_profile: Dict[str, Any], training_content: str) -> str:
        """Build prompt for training plan generation"""
        return f"""
        You are an expert training designer. Create a personalized 5-stage training plan based on the learner profile and training content.

        Learner Profile:
        - Experience Level: {learner_profile.get('experience_level', 'beginner')}
        - Learning Style: {learner_profile.get('learning_style', 'visual')}
        - Job Position: {learner_profile.get('job_position', 'not specified')}
        - Activity Sector: {learner_profile.get('activity_sector', 'not specified')}
        - Country: {learner_profile.get('country', 'not specified')}
        - Language: {learner_profile.get('language', 'en')}

        Training Content Summary:
        {training_content}

        Create a structured plan with exactly 5 stages:
        1. Discovery - Context and objectives
        2. Fundamentals - Basic concepts
        3. Progressive Building - Step-by-step deepening
        4. Mastery - Advanced practice and autonomous work
        5. Validation - Final assessment

        Each stage should contain relevant modules, and each module should contain relevant submodules with slide titles.
        """
    
    def _build_slide_content_prompt(self, slide_title: str, module_context: str, learner_profile: Dict[str, Any]) -> str:
        """Build prompt for slide content generation"""
        return f"""
        Generate educational slide content for the title: "{slide_title}"
        
        Module Context: {module_context}
        
        Learner Profile:
        - Experience Level: {learner_profile.get('experience_level', 'beginner')}
        - Learning Style: {learner_profile.get('learning_style', 'visual')}
        
        Create engaging, educational content adapted to the learner's level and style.
        Include practical examples and clear explanations.
        """
    
    def _build_chat_prompt(self, message: str, conversation_history: List[Dict[str, Any]], training_context: str) -> str:
        """Build prompt for chat interactions"""
        history_text = "\n".join([f"{h['role']}: {h['content']}" for h in conversation_history[-5:]])
        
        return f"""
        You are an AI training assistant helping a learner with their personalized training.
        
        Training Context: {training_context}
        
        Recent Conversation:
        {history_text}
        
        Learner Message: {message}
        
        Provide a helpful, encouraging response related to the training content.
        """
    
    def _build_engagement_analysis_prompt(self, activity_data: Dict[str, Any]) -> str:
        """Build prompt for engagement analysis"""
        return f"""
        Analyze learner engagement based on the following activity data:
        
        {json.dumps(activity_data, indent=2)}
        
        Provide insights on:
        - Engagement level (high, medium, low)
        - Areas of interest
        - Potential challenges
        - Recommendations for improvement
        """
    
    def _get_training_plan_schema(self) -> Dict[str, Any]:
        """Get JSON schema for training plan response"""
        return {
            "type": "object",
            "properties": {
                "stages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "stage_number": {"type": "integer"},
                            "stage_title": {"type": "string"},
                            "stage_description": {"type": "string"},
                            "modules": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "module_title": {"type": "string"},
                                        "module_description": {"type": "string"},
                                        "submodules": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "submodule_title": {"type": "string"},
                                                    "submodule_description": {"type": "string"},
                                                    "slide_titles": {
                                                        "type": "array",
                                                        "items": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_slide_content_schema(self) -> Dict[str, Any]:
        """Get JSON schema for slide content response"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "examples": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    
    def _get_engagement_analysis_schema(self) -> Dict[str, Any]:
        """Get JSON schema for engagement analysis response"""
        return {
            "type": "object",
            "properties": {
                "engagement_level": {"type": "string"},
                "score": {"type": "number"},
                "strengths": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "challenges": {
                    "type": "array", 
                    "items": {"type": "string"}
                },
                "recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    
    async def _log_api_call(
        self,
        operation_type: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        response_time_ms: int
    ) -> None:
        """Log API call for monitoring"""
        # This would typically save to database via repository
        log_entry = {
            "operation_type": operation_type,
            "model_name": self.model_name,
            "request_data": request_data,
            "response_data": response_data,
            "response_time_ms": response_time_ms,
            "success": "error" not in response_data
        }
        logger.info(f"Gemini API Call: {json.dumps(log_entry)}")