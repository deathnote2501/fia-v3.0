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
from app.domain.services.learner_profile_enrichment_service import LearnerProfileEnrichmentService
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository

logger = logging.getLogger(__name__)


class ConversationAdapter(ConversationServicePort):
    """Outbound adapter for AI conversation service using Vertex AI"""
    
    def __init__(self):
        self.vertex_adapter = VertexAIAdapter()
        self._enrichment_service = None  # Will be initialized lazily
        logger.info("🤖 CONVERSATION [ADAPTER] Initialized with Vertex AI")
        
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
            
            prompt = self._build_conversation_prompt(
                message, conversation_history, training_context, learner_profile
            )
            
            # Use Vertex AI with structured JSON output
            generation_config = {
                "temperature": 0.7,  # Higher temperature for more conversational responses
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json"
            }
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            logger.info(f"🤖 CONVERSATION [CHAT] Generated chat response for learner")
            
            # Parse JSON response
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ CONVERSATION [CHAT] Invalid JSON response: {str(e)}")
                # Return fallback structured response
                response_data = {
                    "response": "I understand your question. Let me help you with that.",
                    "confidence_score": 0.7,
                    "suggested_actions": ["Ask a more specific question"],
                    "related_concepts": [],
                    "learner_profile": {}
                }
            
            # Extract and save enriched profile data
            enriched_profile_data = response_data.get("learner_profile", {})
            if enriched_profile_data and learner_session_id:
                try:
                    await self._save_enriched_profile(learner_session_id, enriched_profile_data)
                except Exception as e:
                    logger.warning(f"⚠️ CONVERSATION [PROFILE] Failed to save enriched profile: {str(e)}")
            
            return {
                "response": response_data.get("response", "I understand your question. Let me help you with that."),
                "confidence_score": response_data.get("confidence_score", 0.8),
                "suggested_actions": response_data.get("suggested_actions", []),
                "related_concepts": response_data.get("related_concepts", []),
                "learner_profile": enriched_profile_data,
                "metadata": {
                    "model_used": "gemini-2.0-flash-exp",
                    "generation_time": response_data.get("generation_time_ms", 0),
                    "adapter": "vertex_ai"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ CONVERSATION [CHAT] Failed to generate chat response: {str(e)}")
            # Return fallback response
            return {
                "response": "I'm here to help you with your training. Could you please rephrase your question?",
                "confidence_score": 0.5,
                "suggested_actions": ["Ask a more specific question", "Review the current slide"],
                "related_concepts": [],
                "learner_profile": {},
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
            
            generation_config = {
                "temperature": 0.5,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 200  # Keep hints concise
            }
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            logger.info(f"🤖 CONVERSATION [HINT] Generated contextual hint for learner question")
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"❌ CONVERSATION [HINT] Failed to generate hint: {str(e)}")
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
            
            generation_config = {
                "temperature": 0.3,  # Lower temperature for more accurate explanations
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 300
            }
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            logger.info(f"🤖 CONVERSATION [EXPLAIN] Generated explanation for concept: {concept}")
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"❌ CONVERSATION [EXPLAIN] Failed to explain concept: {str(e)}")
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

AI PROFILE ENRICHMENT TASK:
En te basant sur LEARNER'S CURRENT MESSAGE et l'historique de conversation, enrichis le profil de l'apprenant pour personnaliser au maximum les prochaines slides. Identifie et analyse :
- Son style d'apprentissage réel observé (au-delà du profil initial)
- Ses préférences de contenu et formats d'explication
- Son niveau de compréhension réel sur les sujets abordés
- Ses objectifs personnels et professionnels spécifiques
- Ses blocages ou difficultés récurrentes
- Ses patterns d'engagement et questions fréquentes

Respond in JSON format with this exact structure:
{{
  "response": "Your helpful response to the learner",
  "confidence_score": 0.85,
  "suggested_actions": ["Action 1", "Action 2"],
  "related_concepts": ["Concept 1", "Concept 2"],
  "learner_profile": {{
    "learning_style_observed": "prefers concrete examples and visual aids",
    "comprehension_level": "good understanding but needs repetition on complex topics",
    "interests": ["practical applications", "real-world case studies"],
    "blockers": ["abstract concepts", "too much theory at once"],
    "objectives": "apply knowledge to current job challenges",
    "engagement_patterns": "asks detailed questions, prefers step-by-step approach"
  }},
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
    
    async def comment_slide(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI trainer's comment about the current slide"""
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_slide_comment_prompt(slide_content, slide_title, learner_profile)
            
            generation_config = {
                "temperature": 0.6,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1024,
                "response_mime_type": "application/json"
            }
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            logger.info(f"🤖 CONVERSATION [COMMENT] Generated slide comment")
            
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ CONVERSATION [COMMENT] Invalid JSON response: {str(e)}")
                response_data = {
                    "response": "Here's my analysis of this slide: The content covers important concepts that are relevant to your learning objectives.",
                    "confidence_score": 0.7,
                    "suggested_actions": ["Review the main points", "Ask questions if needed"],
                    "related_concepts": []
                }
            
            return {
                "response": response_data.get("response", "This slide provides valuable learning content."),
                "confidence_score": response_data.get("confidence_score", 0.8),
                "suggested_actions": response_data.get("suggested_actions", []),
                "related_concepts": response_data.get("related_concepts", []),
                "metadata": {
                    "model_used": "gemini-2.0-flash-exp",
                    "action_type": "slide_comment",
                    "adapter": "vertex_ai"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ CONVERSATION [COMMENT] Failed to generate comment: {str(e)}")
            return {
                "response": "This slide contains important information for your learning journey. Take time to understand each concept presented.",
                "confidence_score": 0.5,
                "suggested_actions": ["Review the content carefully"],
                "related_concepts": [],
                "metadata": {"error": str(e), "fallback": True}
            }
    
    async def generate_quiz(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a quiz based on the current slide to evaluate comprehension"""
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_quiz_prompt(slide_content, slide_title, learner_profile)
            
            generation_config = {
                "temperature": 0.4,  # Lower temperature for more structured quiz
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1500,
                "response_mime_type": "application/json"
            }
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
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
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_examples_prompt(slide_content, slide_title, learner_profile)
            
            generation_config = {
                "temperature": 0.7,  # Higher temperature for creative examples
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1200,
                "response_mime_type": "application/json"
            }
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
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
        try:
            await gemini_rate_limiter.acquire()
            
            prompt = self._build_key_points_prompt(slide_content, slide_title, learner_profile)
            
            generation_config = {
                "temperature": 0.3,  # Lower temperature for focused key points
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 800,
                "response_mime_type": "application/json"
            }
            
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
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
            logger.error(f"❌ CONVERSATION [KEY_POINTS] Failed to extract key points: {str(e)}")
            return {
                "response": "The most important takeaway from this slide is understanding the core concept and how it applies to your learning goals.",
                "confidence_score": 0.5,
                "suggested_actions": ["Focus on core concepts", "Review main ideas"],
                "related_concepts": [],
                "metadata": {"error": str(e), "fallback": True}
            }
    
    def _build_slide_comment_prompt(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build prompt for slide commentary"""
        return f"""You are an expert AI trainer providing commentary on a training slide.

SLIDE TITLE: {slide_title}
SLIDE CONTENT: {slide_content[:1500]}...

LEARNER PROFILE:
- Experience Level: {learner_profile.get('experience_level', 'beginner')}
- Learning Style: {learner_profile.get('learning_style', 'visual')}
- Job Position: {learner_profile.get('job_position', 'professional')}
- Activity Sector: {learner_profile.get('activity_sector', 'general')}
- Language: {learner_profile.get('language', 'en')}

INSTRUCTIONS:
- Provide insightful commentary about this slide's content
- Explain why this content is important for the learner
- Highlight connections to their professional context
- Adapt your language to their experience level
- Be encouraging and educational
- Respond in {learner_profile.get('language', 'English')}

Respond in JSON format with this exact structure:
{{
  "response": "Your insightful commentary about this slide",
  "confidence_score": 0.85,
  "suggested_actions": ["Action 1", "Action 2"],
  "related_concepts": ["Concept 1", "Concept 2"],
  "generation_time_ms": 1200
}}"""
    
    def _build_quiz_prompt(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build prompt for quiz generation"""
        return f"""You are an expert AI trainer creating a comprehension quiz for a training slide.

SLIDE TITLE: {slide_title}
SLIDE CONTENT: {slide_content[:1500]}...

LEARNER PROFILE:
- Experience Level: {learner_profile.get('experience_level', 'beginner')}
- Learning Style: {learner_profile.get('learning_style', 'visual')}
- Job Position: {learner_profile.get('job_position', 'professional')}
- Activity Sector: {learner_profile.get('activity_sector', 'general')}
- Language: {learner_profile.get('language', 'en')}

INSTRUCTIONS:
- Generate 2-3 quiz questions to evaluate understanding of this slide
- Adapt difficulty to their experience level: {learner_profile.get('experience_level', 'beginner')}
- Include both conceptual and practical application questions
- Make questions relevant to their job: {learner_profile.get('job_position', 'professional')}
- Be clear and encouraging in your approach
- Respond in {learner_profile.get('language', 'English')}

Respond in JSON format with this exact structure:
{{
  "response": "Here's a quiz to test your understanding: [Your 2-3 questions with encouraging tone]",
  "confidence_score": 0.85,
  "suggested_actions": ["Think through each question", "Apply concepts to your work"],
  "related_concepts": ["Related concept 1", "Related concept 2"],
  "generation_time_ms": 1200
}}"""
    
    def _build_examples_prompt(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build prompt for examples generation"""
        return f"""You are an expert AI trainer providing practical examples to illustrate training content.

SLIDE TITLE: {slide_title}
SLIDE CONTENT: {slide_content[:1500]}...

LEARNER PROFILE:
- Experience Level: {learner_profile.get('experience_level', 'beginner')}
- Learning Style: {learner_profile.get('learning_style', 'visual')}
- Job Position: {learner_profile.get('job_position', 'professional')}
- Activity Sector: {learner_profile.get('activity_sector', 'general')}
- Language: {learner_profile.get('language', 'en')}

INSTRUCTIONS:
- Provide 2-3 concrete, practical examples that illustrate the slide concepts
- Make examples relevant to their job: {learner_profile.get('job_position', 'professional')}
- Adapt examples to their sector: {learner_profile.get('activity_sector', 'general')}
- Consider their experience level: {learner_profile.get('experience_level', 'beginner')}
- Use their preferred learning style: {learner_profile.get('learning_style', 'visual')}
- Be specific and actionable
- Respond in {learner_profile.get('language', 'English')}

Respond in JSON format with this exact structure:
{{
  "response": "Here are practical examples to illustrate these concepts: [Your 2-3 specific examples]",
  "confidence_score": 0.85,
  "suggested_actions": ["Try applying these examples", "Think of similar situations in your work"],
  "related_concepts": ["Related concept 1", "Related concept 2"],
  "generation_time_ms": 1200
}}"""
    
    def _build_key_points_prompt(
        self,
        slide_content: str,
        slide_title: str,
        learner_profile: Dict[str, Any]
    ) -> str:
        """Build prompt for key points extraction"""
        return f"""You are an expert AI trainer identifying the most crucial points from a training slide.

SLIDE TITLE: {slide_title}
SLIDE CONTENT: {slide_content[:1500]}...

LEARNER PROFILE:
- Experience Level: {learner_profile.get('experience_level', 'beginner')}
- Learning Style: {learner_profile.get('learning_style', 'visual')}
- Job Position: {learner_profile.get('job_position', 'professional')}
- Activity Sector: {learner_profile.get('activity_sector', 'general')}
- Language: {learner_profile.get('language', 'en')}

INSTRUCTIONS:
- Identify the 1-3 MOST IMPORTANT points to remember from this slide
- Focus on what's essential for their job: {learner_profile.get('job_position', 'professional')}
- Prioritize based on their experience level: {learner_profile.get('experience_level', 'beginner')}
- Make it memorable and actionable
- Explain WHY these points are the most important
- Respond in {learner_profile.get('language', 'English')}

Respond in JSON format with this exact structure:
{{
  "response": "If you remember only 1-3 things from this slide, focus on: [Your prioritized key points with explanations]",
  "confidence_score": 0.90,
  "suggested_actions": ["Remember these key points", "Apply them in practice"],
  "related_concepts": ["Core concept 1", "Core concept 2"],
  "generation_time_ms": 1200
}}"""

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
                "learner_profile": {
                    "type": "object",
                    "description": "Enriched learner profile based on conversation analysis",
                    "properties": {
                        "learning_style_observed": {"type": "string"},
                        "comprehension_level": {"type": "string"},
                        "interests": {"type": "array", "items": {"type": "string"}},
                        "blockers": {"type": "array", "items": {"type": "string"}},
                        "objectives": {"type": "string"},
                        "engagement_patterns": {"type": "string"}
                    }
                },
                "generation_time_ms": {
                    "type": "number",
                    "description": "Time taken to generate response in milliseconds"
                }
            },
            "required": ["response", "confidence_score"]
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