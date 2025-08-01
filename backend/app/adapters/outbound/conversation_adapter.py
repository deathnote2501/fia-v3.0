"""
FIA v3.0 - Conversation Outbound Adapter
Implementation of AI conversation service using Vertex AI
"""

import json
import logging
from typing import Dict, Any, List
from uuid import UUID

from app.domain.ports.outbound_ports import ConversationServicePort
from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter
from app.infrastructure.rate_limiter import gemini_rate_limiter
from app.infrastructure.gemini_call_logger import gemini_call_logger
from app.domain.services.learner_profile_enrichment_service import LearnerProfileEnrichmentService
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.services.conversation_prompt_builder import ConversationPromptBuilder

logger = logging.getLogger(__name__)


class ConversationAdapter(ConversationServicePort):
    """Outbound adapter for AI conversation service using Vertex AI"""
    
    def __init__(self):
        self.vertex_adapter = VertexAIAdapter()
        self.prompt_builder = ConversationPromptBuilder()
        self._enrichment_service = None  # Will be initialized lazily
        logger.info("🤖 CONVERSATION [ADAPTER] Initialized with Vertex AI and unified prompt builder")
    
    def _get_generation_config(self, prompt_type: str) -> Dict[str, Any]:
        """Get optimized generation config by prompt type"""
        configs = {
            "chat": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json"
            },
            "commentary": {
                "temperature": 0.6,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1024,
                "response_mime_type": "application/json"
            },
            "quiz": {
                "temperature": 0.4,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1500,
                "response_mime_type": "application/json"
            },
            "examples": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1200,
                "response_mime_type": "application/json"
            },
            "key_points": {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 800,
                "response_mime_type": "application/json"
            }
        }
        return configs.get(prompt_type, configs["chat"])
    
    def _parse_json_response(self, response_text: str, action_type: str) -> Dict[str, Any]:
        """Parse JSON response with fallback handling"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"❌ CONVERSATION [{action_type.upper()}] Invalid JSON response: {str(e)}")
            return self._get_fallback_response(action_type)
    
    def _get_fallback_response(self, action_type: str) -> Dict[str, Any]:
        """Get fallback response by action type"""
        fallbacks = {
            "chat": {
                "response": "I understand your question. Let me help you with that.",
                "confidence_score": 0.7,
                "suggested_actions": ["Ask a more specific question"],
                "related_concepts": [],
                "learner_profile": {}
            },
            "comment": {
                "response": "Here's my analysis of this slide: The content covers important concepts that are relevant to your learning objectives.",
                "confidence_score": 0.7,
                "suggested_actions": ["Review the main points", "Ask questions if needed"],
                "related_concepts": []
            },
            "quiz": {
                "response": "Let me test your understanding: What are the main concepts covered in this slide? Can you explain them in your own words?",
                "confidence_score": 0.7,
                "suggested_actions": ["Think about the key points", "Try to explain in your own words"],
                "related_concepts": []
            },
            "examples": {
                "response": "Here are some practical examples to illustrate these concepts: Consider how these ideas apply in real-world situations relevant to your work.",
                "confidence_score": 0.7,
                "suggested_actions": ["Think of your own examples", "Apply to your work context"],
                "related_concepts": []
            },
            "key_points": {
                "response": "If you remember just one thing from this slide, focus on the main concept that connects to your learning objectives.",
                "confidence_score": 0.7,
                "suggested_actions": ["Focus on the main concept", "Connect to previous learning"],
                "related_concepts": []
            }
        }
        return fallbacks.get(action_type, fallbacks["chat"])
    
    def _build_response_metadata(self, action_type: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build response metadata"""
        return {
            "model_used": "gemini-2.0-flash-exp",
            "action_type": action_type,
            "generation_time": response_data.get("generation_time_ms", 0),
            "adapter": "vertex_ai"
        }
    
    async def _generate_ai_response(
        self, 
        prompt: str, 
        prompt_type: str, 
        action_type: str,
        learner_session_id: UUID = None
    ) -> Dict[str, Any]:
        """Unified AI response generation with error handling"""
        call_id = None
        try:
            await gemini_rate_limiter.acquire()
            
            # 🔍 NOUVEAU: Logger centralisé - INPUT
            call_id = gemini_call_logger.log_input(
                service_name=f"conversation_{action_type}",
                prompt=prompt,
                learner_session_id=str(learner_session_id) if learner_session_id else None,
                additional_context={
                    "prompt_type": prompt_type,
                    "action_type": action_type,
                    "generation_config": self._get_generation_config(prompt_type)
                }
            )
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=self._get_generation_config(prompt_type),
                learner_session_id=str(learner_session_id) if learner_session_id else None
            )
            
            # 🔍 NOUVEAU: Logger centralisé - OUTPUT
            gemini_call_logger.log_output(
                call_id=call_id,
                service_name=f"conversation_{action_type}",
                response=response_text,
                learner_session_id=str(learner_session_id) if learner_session_id else None,
                additional_metadata={
                    "parsed_successfully": True,
                    "action_type": action_type
                }
            )
            
            logger.info(f"🤖 CONVERSATION [{action_type.upper()}] Generated response - Call ID: {call_id}")
            
            response_data = self._parse_json_response(response_text, action_type)
            
            return {
                "response": response_data.get("response", f"Generated {action_type} response"),
                "confidence_score": response_data.get("confidence_score", 0.8),
                "suggested_actions": response_data.get("suggested_actions", []),
                "related_concepts": response_data.get("related_concepts", []),
                "metadata": self._build_response_metadata(action_type, response_data)
            }
            
        except Exception as e:
            # 🔍 NOUVEAU: Logger centralisé - ERROR
            if call_id:
                gemini_call_logger.log_error(
                    call_id=call_id,
                    service_name=f"conversation_{action_type}",
                    error=e,
                    learner_session_id=str(learner_session_id) if learner_session_id else None
                )
            
            logger.error(f"❌ CONVERSATION [{action_type.upper()}] Failed to generate response: {str(e)}")
            fallback = self._get_fallback_response(action_type)
            fallback["metadata"] = {"error": str(e), "fallback": True}
            return fallback
        
    async def chat_with_learner(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        training_context: str,
        learner_profile: Dict[str, Any],
        learner_session_id: UUID
    ) -> Dict[str, Any]:
        """Handle learner chat interactions using Vertex AI"""
        try:
            # Apply rate limiting before API call
            await gemini_rate_limiter.acquire()
            
            prompt = self.prompt_builder.build_message_response_prompt(
                message=message,
                conversation_history=conversation_history,
                training_context=training_context,
                learner_profile=learner_profile
            )
            
            response_result = await self._generate_ai_response(
                prompt=prompt,
                prompt_type="chat",
                action_type="chat",
                learner_session_id=learner_session_id
            )
            
            # Extract response data and handle profile enrichment
            response_data = response_result.copy()
            if "metadata" in response_data and "error" not in response_data["metadata"]:
                # Re-parse for learner_profile if no error
                try:
                    full_response = json.loads(await self.vertex_adapter.generate_content(
                        prompt=prompt,
                        generation_config=self._get_generation_config("chat"),
                        learner_session_id=str(learner_session_id) if learner_session_id else None
                    ))
                    response_data["learner_profile"] = full_response.get("learner_profile", {})
                except:
                    response_data["learner_profile"] = {}
            
            # Extract and save enriched profile data
            enriched_profile_data = response_data.get("learner_profile", {})
            if enriched_profile_data and learner_session_id:
                try:
                    await self._save_enriched_profile(learner_session_id, enriched_profile_data)
                except Exception as e:
                    logger.warning(f"⚠️ CONVERSATION [PROFILE] Failed to save enriched profile: {str(e)}")
            
            # Return enriched response
            response_data["learner_profile"] = enriched_profile_data
            return response_data
            
        except Exception as e:
            logger.error(f"❌ CONVERSATION [CHAT] Failed to generate chat response: {str(e)}")
            fallback = self._get_fallback_response("chat")
            fallback["response"] = "I'm here to help you with your training. Could you please rephrase your question?"
            fallback["suggested_actions"] = ["Ask a more specific question", "Review the current slide"]
            fallback["learner_profile"] = {}
            fallback["metadata"] = {"error": str(e), "fallback": True}
            return fallback
    
    async def generate_contextual_hint(
        self,
        current_slide: Dict[str, Any],
        learner_question: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Generate contextual hints for learner questions using unified message response"""
        try:
            # Use unified message response with slide context
            slide_context = f"Current slide: {current_slide.get('title', 'Unknown')}\n{current_slide.get('content', 'No content')}"
            
            response = await self.chat_with_learner(
                message=f"Question about current slide: {learner_question}",
                conversation_history=[],
                training_context=slide_context,
                learner_profile=learner_profile,
                learner_session_id=None  # No profile enrichment for hints
            )
            
            logger.info(f"🤖 CONVERSATION [HINT] Generated contextual hint via unified chat")
            return response.get("response", "Try reviewing the key concepts on this slide and take your time to understand each point.")
            
        except Exception as e:
            logger.error(f"❌ CONVERSATION [HINT] Failed to generate hint: {str(e)}")
            return "Try reviewing the key concepts on this slide and take your time to understand each point."
    
    async def explain_concept(
        self,
        concept: str,
        training_context: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Explain a specific concept to the learner using unified message response"""
        try:
            # Use unified message response for concept explanation
            response = await self.chat_with_learner(
                message=f"Please explain this concept: {concept}",
                conversation_history=[],
                training_context=training_context,
                learner_profile=learner_profile,
                learner_session_id=None  # No profile enrichment for explanations
            )
            
            logger.info(f"🤖 CONVERSATION [EXPLAIN] Generated explanation via unified chat for concept: {concept}")
            return response.get("response", f"I'd be happy to explain {concept}. This is an important concept in your training that builds on the fundamentals you've already learned.")
            
        except Exception as e:
            logger.error(f"❌ CONVERSATION [EXPLAIN] Failed to explain concept: {str(e)}")
            return f"I'd be happy to explain {concept}. This is an important concept in your training that builds on the fundamentals you've already learned."
    
    
    
    
    async def comment_slide(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI trainer's comment about the current slide"""
        prompt = self.prompt_builder.build_slide_commentary_prompt(
            slide_content=slide_content,
            slide_title=slide_title,
            learner_profile=learner_profile
        )
        
        return await self._generate_ai_response(
            prompt=prompt,
            prompt_type="commentary",
            action_type="comment",
            learner_session_id=None  # No learner session for slide comments
        )
    
    async def generate_quiz(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a quiz based on the current slide to evaluate comprehension"""
        call_id = None
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self.prompt_builder.build_comprehension_question_prompt(
                slide_content=slide_content,
                slide_title=slide_title,
                learner_profile=learner_profile
            )
            
            generation_config = {
                "temperature": 0.4,  # Lower temperature for more structured quiz
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1500,
                "response_mime_type": "application/json"
            }
            
            # 🔍 NOUVEAU: Logger centralisé - INPUT
            call_id = gemini_call_logger.log_input(
                service_name="conversation_quiz",
                prompt=prompt,
                additional_context={
                    "slide_title": slide_title,
                    "generation_config": generation_config,
                    "action_type": "quiz_generation"
                }
            )
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # 🔍 NOUVEAU: Logger centralisé - OUTPUT
            gemini_call_logger.log_output(
                call_id=call_id,
                service_name="conversation_quiz",
                response=response_text,
                additional_metadata={
                    "action_type": "quiz_generation",
                    "slide_title": slide_title
                }
            )
            
            logger.info(f"🤖 CONVERSATION [QUIZ] Generated quiz for slide comprehension")
            
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ CONVERSATION [QUIZ] Invalid JSON response: {str(e)}")
                response_data = {
                    "response": "Let me test your understanding: What are the main concepts covered in this slide? Can you explain them in your own words?",
                    "confidence_score": 0.7,
                    "suggested_actions": ["Think about the key points", "Try to explain in your own words"],
                    "related_concepts": []
                }
            
            return {
                "response": response_data.get("response", "Let me test your understanding of this slide."),
                "confidence_score": response_data.get("confidence_score", 0.8),
                "suggested_actions": response_data.get("suggested_actions", []),
                "related_concepts": response_data.get("related_concepts", []),
                "metadata": {
                    "model_used": "gemini-2.0-flash-exp",
                    "action_type": "quiz_generation",
                    "adapter": "vertex_ai"
                }
            }
            
        except Exception as e:
            # 🔍 NOUVEAU: Logger centralisé - ERROR
            if call_id:
                gemini_call_logger.log_error(
                    call_id=call_id,
                    service_name="conversation_quiz",
                    error=e
                )
            
            logger.error(f"❌ CONVERSATION [QUIZ] Failed to generate quiz: {str(e)}")
            return {
                "response": "Let me test your understanding: What are the most important points from this slide? Try explaining them in your own words.",
                "confidence_score": 0.5,
                "suggested_actions": ["Review the content", "Think about key concepts"],
                "related_concepts": [],
                "metadata": {"error": str(e), "fallback": True}
            }
    
    async def provide_examples(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide practical examples to illustrate the slide content"""
        call_id = None
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self.prompt_builder.build_example_generation_prompt(
                slide_content=slide_content,
                slide_title=slide_title,
                learner_profile=learner_profile
            )
            
            generation_config = {
                "temperature": 0.7,  # Higher temperature for creative examples
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1200,
                "response_mime_type": "application/json"
            }
            
            # 🔍 NOUVEAU: Logger centralisé - INPUT
            call_id = gemini_call_logger.log_input(
                service_name="conversation_examples",
                prompt=prompt,
                additional_context={
                    "slide_title": slide_title,
                    "generation_config": generation_config,
                    "action_type": "examples_generation"
                }
            )
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # 🔍 NOUVEAU: Logger centralisé - OUTPUT
            gemini_call_logger.log_output(
                call_id=call_id,
                service_name="conversation_examples",
                response=response_text,
                additional_metadata={
                    "action_type": "examples_generation",
                    "slide_title": slide_title
                }
            )
            
            logger.info(f"🤖 CONVERSATION [EXAMPLES] Generated practical examples")
            
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ CONVERSATION [EXAMPLES] Invalid JSON response: {str(e)}")
                response_data = {
                    "response": "Here are some practical examples to illustrate these concepts: Consider how these ideas apply in real-world situations relevant to your work.",
                    "confidence_score": 0.7,
                    "suggested_actions": ["Think of your own examples", "Apply to your work context"],
                    "related_concepts": []
                }
            
            return {
                "response": response_data.get("response", "Let me provide some practical examples to illustrate these concepts."),
                "confidence_score": response_data.get("confidence_score", 0.8),
                "suggested_actions": response_data.get("suggested_actions", []),
                "related_concepts": response_data.get("related_concepts", []),
                "metadata": {
                    "model_used": "gemini-2.0-flash-exp",
                    "action_type": "examples_generation",
                    "adapter": "vertex_ai"
                }
            }
            
        except Exception as e:
            # 🔍 NOUVEAU: Logger centralisé - ERROR
            if call_id:
                gemini_call_logger.log_error(
                    call_id=call_id,
                    service_name="conversation_examples",
                    error=e
                )
            
            logger.error(f"❌ CONVERSATION [EXAMPLES] Failed to provide examples: {str(e)}")
            return {
                "response": "Let me give you some examples: Think about how these concepts apply in your daily work or professional context.",
                "confidence_score": 0.5,
                "suggested_actions": ["Consider real-world applications", "Think of similar situations"],
                "related_concepts": [],
                "metadata": {"error": str(e), "fallback": True}
            }
    
    async def extract_key_points(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract the 1-3 most important points to remember from the slide"""
        call_id = None
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self.prompt_builder.build_key_points_prompt(
                slide_content=slide_content,
                slide_title=slide_title,
                learner_profile=learner_profile
            )
            
            generation_config = {
                "temperature": 0.3,  # Lower temperature for focused key points
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 800,
                "response_mime_type": "application/json"
            }
            
            # 🔍 NOUVEAU: Logger centralisé - INPUT
            call_id = gemini_call_logger.log_input(
                service_name="conversation_key_points",
                prompt=prompt,
                additional_context={
                    "slide_title": slide_title,
                    "generation_config": generation_config,
                    "action_type": "key_points_extraction"
                }
            )
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # 🔍 NOUVEAU: Logger centralisé - OUTPUT
            gemini_call_logger.log_output(
                call_id=call_id,
                service_name="conversation_key_points",
                response=response_text,
                additional_metadata={
                    "action_type": "key_points_extraction",
                    "slide_title": slide_title
                }
            )
            
            logger.info(f"🤖 CONVERSATION [KEY_POINTS] Generated key points to remember")
            
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ CONVERSATION [KEY_POINTS] Invalid JSON response: {str(e)}")
                response_data = {
                    "response": "If you remember just one thing from this slide, focus on the main concept that connects to your learning objectives.",
                    "confidence_score": 0.7,
                    "suggested_actions": ["Focus on the main concept", "Connect to previous learning"],
                    "related_concepts": []
                }
            
            return {
                "response": response_data.get("response", "Here are the most important points to remember from this slide."),
                "confidence_score": response_data.get("confidence_score", 0.8),
                "suggested_actions": response_data.get("suggested_actions", []),
                "related_concepts": response_data.get("related_concepts", []),
                "metadata": {
                    "model_used": "gemini-2.0-flash-exp",
                    "action_type": "key_points_extraction",
                    "adapter": "vertex_ai"
                }
            }
            
        except Exception as e:
            # 🔍 NOUVEAU: Logger centralisé - ERROR
            if call_id:
                gemini_call_logger.log_error(
                    call_id=call_id,
                    service_name="conversation_key_points",
                    error=e
                )
            
            logger.error(f"❌ CONVERSATION [KEY_POINTS] Failed to extract key points: {str(e)}")
            return {
                "response": "The most important takeaway from this slide is understanding the core concept and how it applies to your learning goals.",
                "confidence_score": 0.5,
                "suggested_actions": ["Focus on core concepts", "Review main ideas"],
                "related_concepts": [],
                "metadata": {"error": str(e), "fallback": True}
            }
    
    
    
    

    
    async def _save_enriched_profile(self, learner_session_id: UUID, enriched_profile_data: Dict[str, Any]) -> None:
        """Save enriched profile data to the learner session"""
        try:
            # Create a new session and service for each call
            from app.infrastructure.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db_session:
                learner_repo = LearnerSessionRepository(db_session)
                enrichment_service = LearnerProfileEnrichmentService(learner_repo)
                
                # Save the enriched profile
                await enrichment_service.enrich_learner_profile(
                    learner_session_id=learner_session_id,
                    new_profile_data=enriched_profile_data
                )
            
            logger.info(f"🧠 CONVERSATION [PROFILE] Enriched profile saved for learner {learner_session_id}")
            
        except Exception as e:
            logger.error(f"❌ CONVERSATION [PROFILE] Failed to save enriched profile: {str(e)}")
            # Don't raise to avoid breaking the conversation flow
            pass