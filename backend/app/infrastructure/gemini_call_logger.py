"""
FIA v3.0 - Gemini Call Logger
Service centralisé pour logger tous les appels et réponses Gemini/VertexAI avec comptage de tokens
ATTENTION: Ce service ne doit PAS impacter la logique métier existante
"""

import logging
import json
import time
from typing import Optional, Dict, Any, Union
from datetime import datetime, timezone
from uuid import UUID
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types de services pour catégoriser les appels AI"""
    PLAN = "plan_generation"
    SLIDES = "slide_generation"  
    CONVERSATION = "conversation"
    TTS = "tts_generation"
    LIVE = "live_conversation"
    IMAGE = "image_generation"
    CONTEXT_CACHE = "context_cache"
    DOCUMENT_PROCESSING = "document_processing"
    
    @classmethod
    def from_service_name(cls, service_name: str) -> 'ServiceType':
        """Détecter le type de service depuis le nom du service"""
        service_name_lower = service_name.lower()
        
        if "plan" in service_name_lower:
            return cls.PLAN
        elif "slide" in service_name_lower:
            return cls.SLIDES
        elif "conversation" in service_name_lower or "chat" in service_name_lower:
            return cls.CONVERSATION
        elif "tts" in service_name_lower or "speech" in service_name_lower:
            return cls.TTS
        elif "live" in service_name_lower:
            return cls.LIVE
        elif "image" in service_name_lower or "dalle" in service_name_lower:
            return cls.IMAGE
        elif "cache" in service_name_lower:
            return cls.CONTEXT_CACHE
        elif "document" in service_name_lower:
            return cls.DOCUMENT_PROCESSING
        else:
            return cls.CONVERSATION  # Default fallback


class GeminiCallLogger:
    """
    Service centralisé pour logger tous les appels Gemini/VertexAI de façon standardisée
    
    Objectifs:
    - Traçabilité complète des appels AI
    - Format uniforme pour debug facile
    - ID de session pour suivre les conversations
    - Aucun impact sur la logique métier
    """
    
    def __init__(self):
        """Initialize Gemini call logger"""
        self.call_counter = 0
        # 🔍 Simple déduplication pour éviter les logs identiques en succession rapide
        self.last_prompt_hash = None
        self.last_prompt_time = 0
        self.dedup_window_seconds = 2  # Éviter les doublons dans une fenêtre de 2 secondes
        logger.info("🔍 GEMINI_CALL_LOGGER [INIT] Service initialized")
    
    def log_input(
        self,
        service_name: str,
        prompt: str,
        session_id: Optional[Union[str, UUID]] = None,
        learner_session_id: Optional[Union[str, UUID]] = None,
        additional_context: Optional[Dict[str, Any]] = None,
        service_type: Optional[ServiceType] = None
    ) -> str:
        """
        Logger un prompt/input envoyé à Gemini
        
        Args:
            service_name: Nom du service appelant (ex: "conversation", "plan_generation")
            prompt: Le prompt complet envoyé
            session_id: ID de session technique
            learner_session_id: ID de session apprenant
            additional_context: Contexte additionnel (config, metadata)
            service_type: Type de service pour catégorisation (auto-détecté si None)
            
        Returns:
            call_id: Identifiant unique pour tracer l'appel
        """
        try:
            # 🔍 Simple déduplication - éviter les prompts identiques en succession rapide  
            import hashlib
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
            current_time = time.time()
            
            if (prompt_hash == self.last_prompt_hash and 
                current_time - self.last_prompt_time < self.dedup_window_seconds):
                logger.info(f"🔍 GEMINI_CALL_LOGGER [DEDUP] Skipping duplicate prompt (within {self.dedup_window_seconds}s)")
                return f"dedup_skip_{int(current_time)}"
            
            self.last_prompt_hash = prompt_hash
            self.last_prompt_time = current_time
            
            self.call_counter += 1
            call_id = f"call_{self.call_counter}_{int(time.time())}"
            
            # Détecter le type de service si non fourni
            detected_service_type = service_type or ServiceType.from_service_name(service_name)
            
            # Préparer le contexte de session
            session_info = self._format_session_info(session_id, learner_session_id)
            
            # Logger le prompt complet avec formatage lisible
            logger.info("=" * 100)
            logger.info(f"🎯 [GEMINI_CALL] [INPUT] [{service_name.upper()}] {session_info}")
            logger.info(f"📋 Call ID: {call_id}")
            logger.info(f"🏷️ Service Type: {detected_service_type.value}")
            logger.info(f"⏰ Timestamp: {datetime.now(timezone.utc).isoformat()}")
            logger.info(f"📏 Prompt Length: {len(prompt)} characters")
            
            if additional_context:
                logger.info(f"🔧 Context: {json.dumps(additional_context, indent=2, default=str)}")
            
            logger.info("-" * 50 + " PROMPT START " + "-" * 50)
            logger.info(prompt)
            logger.info("-" * 50 + " PROMPT END " + "-" * 52)
            logger.info("=" * 100)
            
            return call_id
            
        except Exception as e:
            # Le logging ne doit JAMAIS faire planter la logique métier
            logger.error(f"❌ GEMINI_CALL_LOGGER [INPUT_ERROR] Failed to log input: {e}")
            return f"error_call_{int(time.time())}"
    
    def log_output(
        self,
        call_id: str,
        service_name: str,
        response: Union[str, Dict[str, Any]],
        session_id: Optional[Union[str, UUID]] = None,
        learner_session_id: Optional[Union[str, UUID]] = None,
        processing_time: Optional[float] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        usage_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Logger la réponse reçue de Gemini avec comptage de tokens
        
        Args:
            call_id: ID de l'appel correspondant (retourné par log_input)
            service_name: Nom du service appelant
            response: Réponse brute de Gemini (string ou JSON)
            session_id: ID de session technique
            learner_session_id: ID de session apprenant
            processing_time: Temps de traitement en secondes
            additional_metadata: Métadonnées additionnelles
            input_tokens: Nombre de tokens d'entrée (prompt)
            output_tokens: Nombre de tokens de sortie (réponse)
            usage_metadata: Métadonnées d'usage complètes de l'API
        """
        try:
            # Skip si c'était un appel dédupliqué
            if call_id.startswith("dedup_skip_"):
                return
                
            # Préparer le contexte de session
            session_info = self._format_session_info(session_id, learner_session_id)
            
            # Extraire les tokens depuis usage_metadata si disponibles
            extracted_input_tokens, extracted_output_tokens = self._extract_tokens_from_metadata(
                usage_metadata, input_tokens, output_tokens
            )
            
            # Formater la réponse pour affichage
            formatted_response = self._format_response(response)
            
            # Logger la réponse complète avec formatage lisible
            logger.info("=" * 100)
            logger.info(f"📥 [GEMINI_CALL] [OUTPUT] [{service_name.upper()}] {session_info}")
            logger.info(f"📋 Call ID: {call_id}")
            logger.info(f"⏰ Timestamp: {datetime.now(timezone.utc).isoformat()}")
            logger.info(f"📏 Response Length: {len(str(response))} characters")
            
            # Afficher les tokens si disponibles
            if extracted_input_tokens is not None or extracted_output_tokens is not None:
                logger.info(f"🪙 TOKENS - Input: {extracted_input_tokens or 'N/A'} | Output: {extracted_output_tokens or 'N/A'} | Total: {(extracted_input_tokens or 0) + (extracted_output_tokens or 0) if extracted_input_tokens and extracted_output_tokens else 'N/A'}")
            
            if processing_time:
                logger.info(f"⚡ Processing Time: {processing_time:.3f}s")
                
            if additional_metadata:
                logger.info(f"🔧 Metadata: {json.dumps(additional_metadata, indent=2, default=str)}")
            
            logger.info("-" * 50 + " RESPONSE START " + "-" * 48)
            logger.info(formatted_response)
            logger.info("-" * 50 + " RESPONSE END " + "-" * 50)
            logger.info("=" * 100)
            
        except Exception as e:
            # Le logging ne doit JAMAIS faire planter la logique métier
            logger.error(f"❌ GEMINI_CALL_LOGGER [OUTPUT_ERROR] Failed to log output for call {call_id}: {e}")
    
    def log_error(
        self,
        call_id: str,
        service_name: str,
        error: Exception,
        session_id: Optional[Union[str, UUID]] = None,
        learner_session_id: Optional[Union[str, UUID]] = None,
        processing_time: Optional[float] = None
    ) -> None:
        """
        Logger une erreur lors d'un appel Gemini
        
        Args:
            call_id: ID de l'appel correspondant
            service_name: Nom du service appelant
            error: Exception capturée
            session_id: ID de session technique
            learner_session_id: ID de session apprenant
            processing_time: Temps avant erreur en secondes
        """
        try:
            session_info = self._format_session_info(session_id, learner_session_id)
            
            logger.error("=" * 100)
            logger.error(f"❌ [GEMINI_CALL] [ERROR] [{service_name.upper()}] {session_info}")
            logger.error(f"📋 Call ID: {call_id}")
            logger.error(f"⏰ Timestamp: {datetime.now(timezone.utc).isoformat()}")
            logger.error(f"🚨 Error Type: {type(error).__name__}")
            logger.error(f"💬 Error Message: {str(error)}")
            
            if processing_time:
                logger.error(f"⚡ Time Before Error: {processing_time:.3f}s")
            
            logger.error("=" * 100)
            
        except Exception as e:
            # Même les logs d'erreur ne doivent pas planter
            logger.error(f"❌ GEMINI_CALL_LOGGER [ERROR_LOG_ERROR] Failed to log error: {e}")
    
    def _format_session_info(
        self, 
        session_id: Optional[Union[str, UUID]], 
        learner_session_id: Optional[Union[str, UUID]]
    ) -> str:
        """Formater les informations de session pour affichage"""
        info_parts = []
        
        if session_id:
            info_parts.append(f"Session: {str(session_id)[:8]}...")
            
        if learner_session_id:
            info_parts.append(f"Learner: {str(learner_session_id)[:8]}...")
            
        if not info_parts:
            info_parts.append("No Session")
            
        return f"[{' | '.join(info_parts)}]"
    
    def _extract_tokens_from_metadata(
        self, 
        usage_metadata: Optional[Dict[str, Any]], 
        input_tokens: Optional[int], 
        output_tokens: Optional[int]
    ) -> tuple[Optional[int], Optional[int]]:
        """
        Extraire les tokens depuis les métadonnées d'usage ou utiliser les valeurs fournies
        
        Args:
            usage_metadata: Métadonnées d'usage de l'API Vertex AI
            input_tokens: Tokens d'entrée fournis manuellement
            output_tokens: Tokens de sortie fournis manuellement
            
        Returns:
            tuple: (input_tokens, output_tokens) ou (None, None) si non disponibles
        """
        try:
            # Priorité aux valeurs fournies explicitement
            final_input_tokens = input_tokens
            final_output_tokens = output_tokens
            
            # Si les valeurs ne sont pas fournies, essayer d'extraire depuis usage_metadata
            if usage_metadata and isinstance(usage_metadata, dict):
                if final_input_tokens is None:
                    final_input_tokens = usage_metadata.get('prompt_token_count')
                if final_output_tokens is None:
                    final_output_tokens = usage_metadata.get('candidates_token_count')
                    
            return final_input_tokens, final_output_tokens
            
        except Exception as e:
            logger.warning(f"⚠️ GEMINI_CALL_LOGGER [TOKEN_EXTRACTION] Failed to extract tokens: {e}")
            return input_tokens, output_tokens
    
    def _format_response(self, response: Union[str, Dict[str, Any]]) -> str:
        """Formater la réponse pour un affichage lisible"""
        try:
            if isinstance(response, str):
                # Essayer de parser comme JSON pour un affichage plus propre
                try:
                    parsed = json.loads(response)
                    return json.dumps(parsed, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    # Si ce n'est pas du JSON, retourner tel quel
                    return response
            elif isinstance(response, dict):
                return json.dumps(response, indent=2, ensure_ascii=False, default=str)
            else:
                return str(response)
        except Exception:
            # En cas de problème de formatage, retourner la représentation string
            return str(response)
    
    def log_tokens(
        self,
        call_id: str,
        service_name: str, 
        service_type: ServiceType,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        learner_session_id: Optional[Union[str, UUID]] = None
    ) -> None:
        """
        Méthode spécialisée pour logger uniquement les tokens (utilisée pour les services sans prompt/response)
        
        Args:
            call_id: ID de l'appel
            service_name: Nom du service
            service_type: Type de service (enum)
            input_tokens: Nombre de tokens d'entrée
            output_tokens: Nombre de tokens de sortie
            learner_session_id: ID de session apprenant
        """
        try:
            session_info = self._format_session_info(None, learner_session_id)
            total_tokens = (input_tokens or 0) + (output_tokens or 0)
            
            logger.info("=" * 50)
            logger.info(f"🪙 [TOKENS_ONLY] [{service_name.upper()}] {session_info}")
            logger.info(f"📋 Call ID: {call_id}")
            logger.info(f"🏷️ Service Type: {service_type.value}")
            logger.info(f"🪙 TOKENS - Input: {input_tokens or 'N/A'} | Output: {output_tokens or 'N/A'} | Total: {total_tokens or 'N/A'}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ GEMINI_CALL_LOGGER [TOKENS_ERROR] Failed to log tokens for call {call_id}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du logger avec support tokens"""
        return {
            "service_name": "GeminiCallLogger",
            "total_calls_logged": self.call_counter,
            "status": "active",
            "features": [
                "input_output_logging",
                "token_counting", 
                "service_type_detection",
                "usage_metadata_extraction"
            ],
            "supported_service_types": [service_type.value for service_type in ServiceType],
            "last_check": datetime.now(timezone.utc).isoformat()
        }


# Instance globale pour utilisation dans toute l'application
gemini_call_logger = GeminiCallLogger()