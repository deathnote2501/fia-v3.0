"""
FIA v3.0 - Gemini Call Logger
Service centralisé pour logger tous les appels et réponses Gemini/VertexAI
ATTENTION: Ce service ne doit PAS impacter la logique métier existante
"""

import logging
import json
import time
from typing import Optional, Dict, Any, Union
from datetime import datetime, timezone
from uuid import UUID

logger = logging.getLogger(__name__)


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
        logger.info("🔍 GEMINI_CALL_LOGGER [INIT] Service initialized")
    
    def log_input(
        self,
        service_name: str,
        prompt: str,
        session_id: Optional[Union[str, UUID]] = None,
        learner_session_id: Optional[Union[str, UUID]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Logger un prompt/input envoyé à Gemini
        
        Args:
            service_name: Nom du service appelant (ex: "conversation", "plan_generation")
            prompt: Le prompt complet envoyé
            session_id: ID de session technique
            learner_session_id: ID de session apprenant
            additional_context: Contexte additionnel (config, metadata)
            
        Returns:
            call_id: Identifiant unique pour tracer l'appel
        """
        try:
            self.call_counter += 1
            call_id = f"call_{self.call_counter}_{int(time.time())}"
            
            # Préparer le contexte de session
            session_info = self._format_session_info(session_id, learner_session_id)
            
            # Logger le prompt complet avec formatage lisible
            logger.info("=" * 100)
            logger.info(f"🎯 [GEMINI_CALL] [INPUT] [{service_name.upper()}] {session_info}")
            logger.info(f"📋 Call ID: {call_id}")
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
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Logger la réponse reçue de Gemini
        
        Args:
            call_id: ID de l'appel correspondant (retourné par log_input)
            service_name: Nom du service appelant
            response: Réponse brute de Gemini (string ou JSON)
            session_id: ID de session technique
            learner_session_id: ID de session apprenant
            processing_time: Temps de traitement en secondes
            additional_metadata: Métadonnées additionnelles
        """
        try:
            # Préparer le contexte de session
            session_info = self._format_session_info(session_id, learner_session_id)
            
            # Formater la réponse pour affichage
            formatted_response = self._format_response(response)
            
            # Logger la réponse complète avec formatage lisible
            logger.info("=" * 100)
            logger.info(f"📥 [GEMINI_CALL] [OUTPUT] [{service_name.upper()}] {session_info}")
            logger.info(f"📋 Call ID: {call_id}")
            logger.info(f"⏰ Timestamp: {datetime.now(timezone.utc).isoformat()}")
            logger.info(f"📏 Response Length: {len(str(response))} characters")
            
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du logger"""
        return {
            "service_name": "GeminiCallLogger",
            "total_calls_logged": self.call_counter,
            "status": "active",
            "last_check": datetime.now(timezone.utc).isoformat()
        }


# Instance globale pour utilisation dans toute l'application
gemini_call_logger = GeminiCallLogger()