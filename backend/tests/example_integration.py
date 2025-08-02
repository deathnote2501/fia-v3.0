"""
FIA v3.0 - Exemple d'intégration du GeminiCallLogger
Montre comment intégrer le logger dans les services existants SANS impacter la logique métier
"""

import time
from typing import Dict, Any, Optional
from uuid import UUID
from app.infrastructure.gemini_call_logger import gemini_call_logger

# ===========================================================================================
# EXEMPLE 1: Integration dans un service de conversation
# ===========================================================================================

class ExampleConversationService:
    """Exemple d'intégration dans un service de conversation"""
    
    async def generate_response(
        self, 
        message: str, 
        learner_session_id: UUID,
        learner_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Méthode existante - AUCUNE modification de la logique métier
        On ajoute SEULEMENT les appels de logging
        """
        start_time = time.time()
        call_id = None
        
        try:
            # 1. Construire le prompt (logique métier existante)
            prompt = self._build_prompt(message, learner_profile)
            
            # 2. 🔍 NOUVEAU: Logger l'input (N'IMPACTE PAS la logique)
            call_id = gemini_call_logger.log_input(
                service_name="conversation",
                prompt=prompt,
                learner_session_id=learner_session_id,
                additional_context={
                    "message_length": len(message),
                    "profile_level": learner_profile.get("experience_level")
                }
            )
            
            # 3. Appel API existant (AUCUNE modification)
            response = await self._call_vertex_ai(prompt)
            
            # 4. Traitement de la réponse (logique métier existante)
            processed_response = self._process_response(response)
            
            # 5. 🔍 NOUVEAU: Logger l'output (N'IMPACTE PAS la logique)
            processing_time = time.time() - start_time
            gemini_call_logger.log_output(
                call_id=call_id,
                service_name="conversation",
                response=response,  # Réponse brute de l'API
                learner_session_id=learner_session_id,
                processing_time=processing_time,
                additional_metadata={
                    "processed_response_length": len(str(processed_response)),
                    "success": True
                }
            )
            
            # 6. Retour normal (AUCUNE modification)
            return processed_response
            
        except Exception as e:
            # 7. 🔍 NOUVEAU: Logger l'erreur (N'IMPACTE PAS la gestion d'erreur)
            if call_id:
                processing_time = time.time() - start_time
                gemini_call_logger.log_error(
                    call_id=call_id,
                    service_name="conversation",
                    error=e,
                    learner_session_id=learner_session_id,
                    processing_time=processing_time
                )
            
            # 8. Re-raise l'exception (logique métier INCHANGÉE)
            raise
    
    def _build_prompt(self, message: str, profile: Dict[str, Any]) -> str:
        """Méthode existante - AUCUNE modification"""
        return f"User message: {message}\nProfile: {profile}"
    
    async def _call_vertex_ai(self, prompt: str) -> str:
        """Simulation d'appel VertexAI - AUCUNE modification"""
        # Logique métier existante inchangée
        return "Réponse simulée de VertexAI"
    
    def _process_response(self, response: str) -> Dict[str, Any]:
        """Traitement de réponse - AUCUNE modification"""
        return {"response": response, "processed": True}

# ===========================================================================================
# EXEMPLE 2: Integration dans un service de génération de plan
# ===========================================================================================

class ExamplePlanGenerationService:
    """Exemple d'intégration dans un service de génération de plan"""
    
    async def generate_training_plan(
        self, 
        document_content: str,
        learner_profile: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Service existant - Ajout du logging SANS modification de la logique
        """
        start_time = time.time()
        call_id = None
        
        try:
            # Logique métier existante
            prompt = self._build_plan_prompt(document_content, learner_profile)
            
            # 🔍 Logging ajouté (non-intrusif)
            call_id = gemini_call_logger.log_input(
                service_name="plan_generation",
                prompt=prompt,
                session_id=session_id,
                additional_context={
                    "document_length": len(document_content),
                    "learner_level": learner_profile.get("experience_level"),
                    "training_duration": learner_profile.get("training_duration")
                }
            )
            
            # Appel API existant (inchangé)
            raw_response = await self._call_gemini_with_structured_output(prompt)
            
            # Traitement existant (inchangé)
            validated_plan = self._validate_and_process_plan(raw_response)
            
            # 🔍 Logging de la réponse (non-intrusif)
            processing_time = time.time() - start_time
            gemini_call_logger.log_output(
                call_id=call_id,
                service_name="plan_generation",
                response=raw_response,  # Réponse brute importante pour debug
                session_id=session_id,
                processing_time=processing_time,
                additional_metadata={
                    "plan_stages": len(validated_plan.get("stages", [])),
                    "validation_success": True
                }
            )
            
            return validated_plan
            
        except Exception as e:
            # Logging d'erreur sans impact sur la gestion existante
            if call_id:
                gemini_call_logger.log_error(
                    call_id=call_id,
                    service_name="plan_generation", 
                    error=e,
                    session_id=session_id,
                    processing_time=time.time() - start_time
                )
            raise  # Re-raise inchangé
    
    def _build_plan_prompt(self, content: str, profile: Dict[str, Any]) -> str:
        """Méthode existante inchangée"""
        return f"Generate plan for: {content[:100]}... Profile: {profile}"
    
    async def _call_gemini_with_structured_output(self, prompt: str) -> Dict[str, Any]:
        """Appel API existant inchangé"""
        return {"training_plan": {"stages": [{"title": "Test"}]}}
    
    def _validate_and_process_plan(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validation existante inchangée"""
        return response

# ===========================================================================================
# DÉMONSTRATION - Comment utiliser dans les services réels
# ===========================================================================================

def integration_guidelines():
    """
    GUIDELINES pour intégrer le logger dans les services existants:
    
    ✅ CE QU'IL FAUT FAIRE:
    1. Ajouter 3 lignes de code SEULEMENT:
       - gemini_call_logger.log_input() AVANT l'appel API
       - gemini_call_logger.log_output() APRÈS l'appel API réussi  
       - gemini_call_logger.log_error() dans le bloc except
    
    2. Passer les données EXISTANTES (ne pas créer de nouvelles variables)
    
    3. Utiliser try/except autour des appels de logging si nécessaire
    
    ❌ CE QU'IL NE FAUT PAS FAIRE:
    1. Modifier la signature des méthodes existantes
    2. Changer la logique de traitement des réponses
    3. Modifier la gestion d'erreurs existante
    4. Ajouter de nouvelles dépendances aux services métier
    
    📋 PATTERN D'INTÉGRATION:
    ```python
    async def existing_method(self, ...):
        start_time = time.time()
        call_id = None
        
        try:
            # Logique existante inchangée
            prompt = self._build_prompt(...)
            
            # 🔍 AJOUT: Logging input
            call_id = gemini_call_logger.log_input(...)
            
            # Logique existante inchangée  
            response = await self._call_api(prompt)
            result = self._process_response(response)
            
            # 🔍 AJOUT: Logging output
            gemini_call_logger.log_output(...)
            
            # Retour inchangé
            return result
            
        except Exception as e:
            # 🔍 AJOUT: Logging error
            if call_id:
                gemini_call_logger.log_error(...)
            raise  # Gestion d'erreur inchangée
    ```
    """
    pass

if __name__ == "__main__":
    print("📋 Exemples d'intégration du GeminiCallLogger")
    print("Voir le code source pour les patterns d'intégration recommandés")