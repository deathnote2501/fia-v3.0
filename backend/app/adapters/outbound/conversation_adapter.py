"""
FIA v3.0 - Conversation Outbound Adapter
Implementation of AI conversation service using Gemini 2.0 Flash
"""

import json
import logging
from typing import Dict, Any, List

import google.generativeai as genai
from google.generativeai.types import GenerateContentConfig

from app.domain.ports.outbound_ports import ConversationServicePort
from app.infrastructure.settings import settings
from app.infrastructure.rate_limiter import gemini_rate_limiter

logger = logging.getLogger(__name__)


class ConversationAdapter(ConversationServicePort):
    """Outbound adapter for AI conversation service using Gemini"""
    
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_region
        )
        self.model_name = settings.gemini_model_name
        
    async def chat_with_learner(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        training_context: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle learner chat interactions using Gemini AI"""
        try:
            # Apply rate limiting before API call
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_conversation_prompt(
                message, conversation_history, training_context, learner_profile
            )
            
            config = GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self._get_chat_response_schema(),
                temperature=0.7  # Higher temperature for more conversational responses
            )
            
            response = await self.client.models.generate_content_async(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            logger.info(f"Generated chat response for learner conversation")
            
            # Parse JSON response
            response_data = json.loads(response.text)
            
            return {
                "response": response_data.get("response", "I understand your question. Let me help you with that."),
                "confidence_score": response_data.get("confidence_score", 0.8),
                "suggested_actions": response_data.get("suggested_actions", []),
                "related_concepts": response_data.get("related_concepts", []),
                "metadata": {
                    "model_used": self.model_name,
                    "tokens_used": getattr(response.usage_metadata, 'total_token_count', 0),
                    "generation_time": response_data.get("generation_time_ms", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate chat response: {str(e)}")
            # Return fallback response
            return {
                "response": "I'm here to help you with your training. Could you please rephrase your question?",
                "confidence_score": 0.5,
                "suggested_actions": ["Ask a more specific question", "Review the current slide"],
                "related_concepts": [],
                "metadata": {"error": str(e), "fallback": True}
            }
    
    async def generate_contextual_hint(
        self,
        current_slide: Dict[str, Any],
        learner_question: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Generate contextual hints for learner questions"""
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_hint_prompt(current_slide, learner_question, learner_profile)
            
            config = GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=200  # Keep hints concise
            )
            
            response = await self.client.models.generate_content_async(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            logger.info(f"Generated contextual hint for learner question")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate hint: {str(e)}")
            return "Try reviewing the key concepts on this slide and take your time to understand each point."
    
    async def explain_concept(
        self,
        concept: str,
        training_context: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Explain a specific concept to the learner"""
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_explanation_prompt(concept, training_context, learner_profile)
            
            config = GenerateContentConfig(
                temperature=0.3,  # Lower temperature for more accurate explanations
                max_output_tokens=300
            )
            
            response = await self.client.models.generate_content_async(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            logger.info(f"Generated explanation for concept: {concept}")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Failed to explain concept: {str(e)}")
            return f"I'd be happy to explain {concept}. This is an important concept in your training that builds on the fundamentals you've already learned."
    
    def _build_conversation_prompt(
        self, 
        message: str, 
        conversation_history: List[Dict[str, Any]], 
        training_context: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build conversation prompt for Gemini"""
        
        # Build conversation history
        history_text = ""
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            role = "Learner" if msg["role"] == "user" else "AI Trainer"
            history_text += f"{role}: {msg['content']}\n"
        
        return f"""You are an expert AI trainer helping a learner in an interactive training session.

LEARNER PROFILE:
- Experience Level: {learner_profile.get('experience_level', 'beginner')}
- Learning Style: {learner_profile.get('learning_style', 'visual')}
- Job Position: {learner_profile.get('job_position', 'professional')}
- Activity Sector: {learner_profile.get('activity_sector', 'general')}
- Language: {learner_profile.get('language', 'en')}

TRAINING CONTEXT:
{training_context[:1000]}...

RECENT CONVERSATION:
{history_text}

LEARNER'S CURRENT MESSAGE:
{message}

INSTRUCTIONS:
- Respond helpfully and supportively in {learner_profile.get('language', 'English')}
- Adapt your explanation style to their learning preference: {learner_profile.get('learning_style', 'visual')}
- Consider their experience level: {learner_profile.get('experience_level', 'beginner')}
- Provide practical examples relevant to their job: {learner_profile.get('job_position', 'professional')}
- Be encouraging and pedagogical
- Suggest specific actions they can take
- Identify related concepts they should explore

Respond in JSON format with this exact structure:
{{
  "response": "Your helpful response to the learner",
  "confidence_score": 0.85,
  "suggested_actions": ["Action 1", "Action 2"],
  "related_concepts": ["Concept 1", "Concept 2"],
  "generation_time_ms": 1500
}}"""
    
    def _build_hint_prompt(
        self, 
        current_slide: Dict[str, Any], 
        learner_question: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build hint generation prompt"""
        
        slide_content = current_slide.get('content', 'Current slide content')
        slide_title = current_slide.get('title', 'Current slide')
        
        return f"""You are an AI trainer providing a helpful hint to a learner.

CURRENT SLIDE: {slide_title}
SLIDE CONTENT: {slide_content[:500]}...

LEARNER PROFILE:
- Experience Level: {learner_profile.get('experience_level', 'beginner')}
- Learning Style: {learner_profile.get('learning_style', 'visual')}

LEARNER'S QUESTION: {learner_question}

INSTRUCTIONS:
- Provide a brief, encouraging hint (1-2 sentences)
- Don't give away the complete answer
- Guide them toward discovering the solution
- Adapt to their experience level: {learner_profile.get('experience_level', 'beginner')}
- Use language appropriate for their learning style: {learner_profile.get('learning_style', 'visual')}

Generate a helpful hint:"""
    
    def _build_explanation_prompt(
        self, 
        concept: str, 
        training_context: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build concept explanation prompt"""
        
        return f"""You are an AI trainer explaining a concept to a learner.

CONCEPT TO EXPLAIN: {concept}

TRAINING CONTEXT: {training_context[:800]}...

LEARNER PROFILE:
- Experience Level: {learner_profile.get('experience_level', 'beginner')}
- Learning Style: {learner_profile.get('learning_style', 'visual')}
- Job Position: {learner_profile.get('job_position', 'professional')}
- Activity Sector: {learner_profile.get('activity_sector', 'general')}

INSTRUCTIONS:
- Explain the concept clearly and concisely
- Adapt to their experience level: {learner_profile.get('experience_level', 'beginner')}
- Use examples relevant to their job: {learner_profile.get('job_position', 'professional')}
- Structure for their learning style: {learner_profile.get('learning_style', 'visual')}
- Keep it practical and actionable
- Limit to 2-3 paragraphs

Provide a clear explanation:"""
    
    def _get_chat_response_schema(self) -> Dict[str, Any]:
        """Get JSON schema for chat response"""
        return {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "The AI trainer's response to the learner"
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Confidence score for the response quality"
                },
                "suggested_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Suggested actions for the learner"
                },
                "related_concepts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Related concepts the learner should explore"
                },
                "generation_time_ms": {
                    "type": "number",
                    "description": "Time taken to generate response in milliseconds"
                }
            },
            "required": ["response", "confidence_score"]
        }