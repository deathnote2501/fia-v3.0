"""
FIA v3.0 - Text-to-Speech Controller
FastAPI routes for TTS service using Vertex AI Gemini 2.5 TTS
"""

import base64
import logging
import time
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.domain.services.text_to_speech_service import TextToSpeechService
from app.adapters.outbound.tts_adapter import TTSAdapter

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["tts"])


# ============================================================================
# PYDANTIC MODELS FOR TTS REQUESTS/RESPONSES
# ============================================================================

class TTSGenerateRequest(BaseModel):
    """Request model for TTS generation"""
    message: str = Field(..., min_length=1, max_length=500, description="Text to convert to speech")
    voice: str = Field(default="Kore", description="Voice name to use (e.g., 'Kore', 'Puck', 'Aoede')")
    language: str = Field(default="fr", description="Language code (e.g., 'fr', 'en', 'es', 'de')")
    voice_style: str = Field(default="default", description="Voice style (default, friendly, formal)")


class TTSGenerateResponse(BaseModel):
    """Response model for TTS generation"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    mime_type: str = Field(..., description="MIME type of audio (e.g., 'audio/wav')")
    duration: float = Field(..., description="Duration of audio in seconds")
    voice_used: str = Field(..., description="Voice that was actually used")
    language: str = Field(..., description="Language code used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TTSVoiceInfo(BaseModel):
    """Voice information model"""
    name: str = Field(..., description="Voice name")
    style: str = Field(..., description="Voice style description")
    supported_languages: List[str] = Field(..., description="List of supported language codes")
    recommended_for: str = Field(..., description="Recommended usage context")
    available: bool = Field(default=True, description="Whether voice is currently available")


class TTSHealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status (healthy, degraded, unhealthy)")
    vertex_ai_available: bool = Field(..., description="Whether Vertex AI TTS is available")
    service: str = Field(default="tts", description="Service name")
    version: str = Field(default="3.0", description="Service version")
    available_voices_count: int = Field(..., description="Number of available voices")
    supported_languages: List[str] = Field(..., description="List of supported languages")


# ============================================================================
# TTS ROUTES (public - no auth required for learner experience)
# ============================================================================

@router.post("/api/tts/generate", response_model=TTSGenerateResponse, status_code=status.HTTP_200_OK)
async def generate_speech(request: TTSGenerateRequest):
    """
    Generate speech audio from text using Vertex AI Gemini 2.5 TTS
    
    This endpoint converts text to speech using AI-powered voice synthesis.
    Perfect for creating voice responses from AI trainer messages.
    """
    try:
        logger.info(f"🔊 TTS [API] Generating speech - Voice: {request.voice}, Lang: {request.language}, Text: {len(request.message)} chars")
        
        # Initialize TTS service
        tts_adapter = TTSAdapter()
        tts_service = TextToSpeechService(tts_adapter)
        
        # Generate speech - use the specific voice requested, not voice_style selection
        speech_result = await tts_service.generate_speech_for_message(
            text=request.message,
            language_code=request.language,
            voice_style=request.voice_style,
            learner_profile={
                "language": request.language,
                "voice_preference": request.voice,
                "requested_voice": request.voice  # Ensure specific voice is used
            }
        )
        
        # Audio data from Gemini is already base64 encoded
        audio_data = speech_result["audio_data"]
        if isinstance(audio_data, bytes):
            # If it's bytes, encode it
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            logger.info("🔊 TTS [API] Encoded bytes to base64")
        else:
            # If it's already a string (base64), use it as-is
            audio_b64 = audio_data
            logger.info("🔊 TTS [API] Using existing base64 string")
        
        # Use detected format from TTS service
        metadata = speech_result.get("metadata", {})
        actual_format = metadata.get("format", "wav")
        mime_type_from_response = metadata.get("mime_type_from_response", f"audio/{actual_format}")
        
        # Try different MIME types for better browser compatibility
        if actual_format == "unknown":
            # Default to WAV for unknown formats
            mime_type = "audio/wav"
            actual_format = "wav"
        else:
            mime_type = f"audio/{actual_format}"
        
        logger.info(f"🔊 TTS [API] Audio format: {actual_format}, MIME type: {mime_type}, Response MIME: {mime_type_from_response}")
        
        response = TTSGenerateResponse(
            audio_data=audio_b64,
            mime_type=mime_type,
            duration=speech_result.get("duration_seconds", 0.0),
            voice_used=speech_result["metadata"].get("voice_selected", request.voice),
            language=request.language,
            metadata=speech_result.get("metadata", {})
        )
        
        logger.info(f"✅ TTS [API] Speech generated successfully - {len(audio_b64)} base64 chars, {response.duration:.2f}s")
        return response
        
    except ValueError as e:
        logger.warning(f"⚠️ TTS [API] Invalid request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ TTS [API] Speech generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Text-to-speech service temporarily unavailable"
        )


@router.get("/api/tts/voices", response_model=List[TTSVoiceInfo], status_code=status.HTTP_200_OK)
async def get_available_voices(language: Optional[str] = None):
    """
    Get list of available voices, optionally filtered by language
    
    This endpoint returns all available voices for text-to-speech generation,
    with information about their styles and supported languages.
    """
    try:
        logger.info(f"🔊 TTS [API] Getting available voices for language: {language or 'all'}")
        
        # Initialize TTS service
        tts_adapter = TTSAdapter()
        tts_service = TextToSpeechService(tts_adapter)
        
        # Get available voices
        voices = await tts_service.get_available_voices_for_language(language or "fr")
        
        # Convert to response format
        voice_responses = []
        for voice in voices:
            voice_info = TTSVoiceInfo(
                name=voice["name"],
                style=voice["style"],
                supported_languages=voice["supported_languages"],
                recommended_for=voice["recommended_for"],
                available=voice.get("available", True)
            )
            voice_responses.append(voice_info)
        
        logger.info(f"✅ TTS [API] Returned {len(voice_responses)} available voices")
        return voice_responses
        
    except Exception as e:
        logger.error(f"❌ TTS [API] Failed to get available voices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve available voices"
        )


@router.get("/api/tts/health", response_model=TTSHealthResponse, status_code=status.HTTP_200_OK)
async def tts_health_check():
    """
    Health check for TTS service
    
    This endpoint provides status information about the text-to-speech service,
    including Vertex AI availability and supported features.
    """
    try:
        logger.info("🔊 TTS [API] Performing health check")
        
        # Initialize TTS service
        tts_adapter = TTSAdapter()
        tts_service = TextToSpeechService(tts_adapter)
        
        # Check service availability
        try:
            # Test by getting available voices
            voices = await tts_service.get_available_voices_for_language("fr")
            vertex_ai_available = True
            service_status = "healthy"
            available_voices_count = len(voices)
        except Exception as e:
            logger.warning(f"⚠️ TTS [API] Health check warning: {str(e)}")
            vertex_ai_available = False
            service_status = "degraded"
            available_voices_count = 0
        
        # Get supported languages
        supported_languages = ["fr", "en", "es", "de"]  # Based on our voice mapping
        
        response = TTSHealthResponse(
            status=service_status,
            vertex_ai_available=vertex_ai_available,
            service="tts",
            version="3.0",
            available_voices_count=available_voices_count,
            supported_languages=supported_languages
        )
        
        logger.info(f"✅ TTS [API] Health check completed - Status: {service_status}")
        return response
        
    except Exception as e:
        logger.error(f"❌ TTS [API] Health check failed: {str(e)}")
        return TTSHealthResponse(
            status="unhealthy",
            vertex_ai_available=False,
            service="tts",
            version="3.0",
            available_voices_count=0,
            supported_languages=[]
        )


# ============================================================================
# UTILITY ROUTES
# ============================================================================

@router.post("/api/tts/debug/save-audio", status_code=status.HTTP_200_OK)
async def save_audio_debug(request: TTSGenerateRequest):
    """
    Debug endpoint to save generated audio to file for testing
    """
    try:
        logger.info(f"🔍 TTS [DEBUG] Saving audio for debugging")
        
        # Initialize TTS service
        tts_adapter = TTSAdapter()
        tts_service = TextToSpeechService(tts_adapter)
        
        # Generate speech
        speech_result = await tts_service.generate_speech_for_message(
            text=request.message,
            language_code=request.language,
            voice_style=request.voice_style,
            learner_profile={
                "language": request.language,
                "voice_preference": request.voice,
                "requested_voice": request.voice
            }
        )
        
        # Save to file for debugging
        import base64
        import os
        
        audio_data = speech_result["audio_data"]
        if isinstance(audio_data, str):
            # Decode base64
            audio_bytes = base64.b64decode(audio_data)
        else:
            audio_bytes = audio_data
            
        # Determine format
        metadata = speech_result.get("metadata", {})
        actual_format = metadata.get("format", "wav")
        
        # Save to temp file
        temp_dir = "/tmp"
        filename = f"tts_debug_{int(time.time())}.{actual_format}"
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(audio_bytes)
            
        logger.info(f"🔍 TTS [DEBUG] Audio saved to: {filepath} ({len(audio_bytes)} bytes)")
        
        return {
            "status": "saved",
            "filepath": filepath,
            "size_bytes": len(audio_bytes),
            "format": actual_format,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"❌ TTS [DEBUG] Failed to save audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug save failed: {str(e)}"
        )


@router.get("/api/tts/voices/recommendations", status_code=status.HTTP_200_OK)
async def get_voice_recommendations(
    language: str = "fr",
    context: str = "default"
):
    """
    Get voice recommendations for specific language and context
    
    This endpoint provides intelligent voice recommendations based on
    the target language and usage context (default, friendly, formal).
    """
    try:
        logger.info(f"🔊 TTS [API] Getting voice recommendations - Lang: {language}, Context: {context}")
        
        # Initialize TTS adapter
        tts_adapter = TTSAdapter()
        
        # Get recommendations
        recommendations = tts_adapter.get_voice_recommendations(language, context)
        
        response = {
            "language": language,
            "context": context,
            "recommended_voices": recommendations,
            "primary_recommendation": recommendations[0] if recommendations else None
        }
        
        logger.info(f"✅ TTS [API] Voice recommendations: {recommendations}")
        return response
        
    except Exception as e:
        logger.error(f"❌ TTS [API] Failed to get voice recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to get voice recommendations"
        )