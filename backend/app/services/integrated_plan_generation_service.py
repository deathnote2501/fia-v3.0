"""
FIA v3.0 - Integrated Plan Generation Service
Service de génération de plans avec intégration base de données complète
"""

import logging
import time
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.services.simple_plan_generation_service import SimplePlanGenerationService
from app.domain.entities.learner_training_plan import LearnerTrainingPlan
from app.domain.entities.api_log import ApiLog
from app.domain.ports.repositories import LearnerTrainingPlanRepositoryPort, ApiLogRepositoryPort

logger = logging.getLogger(__name__)


class IntegratedPlanGenerationService:
    """Service de génération de plans avec persistance en base de données"""
    
    def __init__(
        self,
        plan_repository: LearnerTrainingPlanRepositoryPort,
        api_log_repository: ApiLogRepositoryPort
    ):
        """
        Initialiser le service intégré
        
        Args:
            plan_repository: Repository pour les plans de formation
            api_log_repository: Repository pour les logs API
        """
        self.plan_repository = plan_repository
        self.api_log_repository = api_log_repository
        self.plan_generation_service = SimplePlanGenerationService()
        
        # Décorer le service simple pour capturer les logs
        self._decorate_plan_service()
        
        logger.info("IntegratedPlanGenerationService initialized")
        logger.info(f"Database integration: plan_repository={type(plan_repository).__name__}")
        logger.info(f"Database integration: api_log_repository={type(api_log_repository).__name__}")
    
    def _decorate_plan_service(self):
        """Décorer le service simple pour capturer les appels API"""
        original_log_method = self.plan_generation_service._log_gemini_api_call
        
        def enhanced_log_method(*args, **kwargs):
            """Méthode de log enrichie qui sauve aussi en DB"""
            # Appeler la méthode originale (logging structuré)
            original_log_method(*args, **kwargs)
            
            # Stocker pour persistance ultérieure (async sera géré dans le service)
            if hasattr(self, '_current_learner_session_id'):
                kwargs['learner_session_id'] = self._current_learner_session_id
                self._pending_api_logs.append((args, kwargs))
        
        # Remplacer la méthode de log
        self.plan_generation_service._log_gemini_api_call = enhanced_log_method
        
        # Liste pour stocker les logs en attente
        self._pending_api_logs = []
        self._current_learner_session_id = None
    
    async def _persist_api_log(
        self,
        operation_type: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any] = None,
        error_data: Dict[str, Any] = None,
        start_time: float = None,
        end_time: float = None,
        attempt_number: int = 1,
        success: bool = True,
        learner_session_id: Optional[UUID] = None
    ) -> None:
        """
        Persister les logs d'API en base de données
        
        Args:
            operation_type: Type d'opération Gemini
            request_data: Métadonnées de la requête
            response_data: Métadonnées de la réponse
            error_data: Données d'erreur si applicable
            start_time: Timestamp de début
            end_time: Timestamp de fin
            attempt_number: Numéro de tentative
            success: Si l'appel a réussi
            learner_session_id: ID de session apprenant (optionnel)
        """
        try:
            # Calculer durée
            duration_ms = None
            if start_time and end_time:
                duration_ms = int((end_time - start_time) * 1000)
            
            # Créer l'entité ApiLog
            api_log = ApiLog(
                service_name="gemini_flash_2.0",
                endpoint=f"/v1/{operation_type}",
                method="POST",
                request_data=request_data,
                response_data=response_data or {},
                status_code=200 if success else 500,
                response_time_ms=duration_ms,
                tokens_used=response_data.get("usage_metadata", {}).get("total_token_count") if response_data else None,
                cost_estimate=None,  # À calculer si nécessaire
                learner_session_id=learner_session_id
            )
            
            # Persister en base
            await self.api_log_repository.create(api_log)
            
            logger.debug(f"🗄️ API log persisted: {operation_type} (duration: {duration_ms}ms)")
            
        except Exception as e:
            logger.error(f"❌ Failed to persist API log: {e}")
            # Ne pas faire échouer la génération pour un problème de log
    
    async def generate_and_persist_plan(
        self,
        learner_session_id: UUID,
        learner_profile: Dict[str, Any],
        file_path: str,
        force_regenerate: bool = False
    ) -> LearnerTrainingPlan:
        """
        Générer un plan de formation et le persister en base de données
        
        Args:
            learner_session_id: ID de la session apprenant
            learner_profile: Profil de l'apprenant
            file_path: Chemin du fichier de formation
            force_regenerate: Forcer la régénération
            
        Returns:
            Plan de formation persisté
        """
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Starting integrated plan generation for session {learner_session_id}")
            
            # Vérifier si un plan existe déjà
            if not force_regenerate:
                existing_plan = await self.plan_repository.get_latest_by_learner_session_id(learner_session_id)
                if existing_plan:
                    logger.info(f"✅ Using existing plan for session {learner_session_id}")
                    return existing_plan
            
            # Configurer le contexte pour les logs API
            self._current_learner_session_id = learner_session_id
            
            # Générer le plan avec le service simple (qui va maintenant logger en DB)
            plan_data = await self.plan_generation_service.generate_plan(
                learner_profile=learner_profile,
                file_path=file_path
            )
            
            end_time = time.time()
            generation_time_seconds = int(end_time - start_time)
            
            # Déterminer la méthode de génération
            generation_method = "vertex_ai" if self.plan_generation_service.client else "fallback"
            
            # Créer l'entité domaine
            learner_training_plan = LearnerTrainingPlan(
                learner_session_id=learner_session_id,
                plan_data=plan_data,
                generation_method=generation_method,
                tokens_used=None,  # Sera mis à jour par les logs API
                generation_time_seconds=generation_time_seconds
            )
            
            # Valider l'entité
            learner_training_plan.validate()
            
            # Persister en base de données
            persisted_plan = await self.plan_repository.create(learner_training_plan)
            
            # Persister tous les logs API en attente
            await self._persist_pending_api_logs()
            
            # Calculer statistiques
            total_slides = persisted_plan.get_total_slides()
            stage_count = persisted_plan.get_stage_count()
            
            logger.info(
                f"✅ Plan generated and persisted successfully: "
                f"ID={persisted_plan.id}, stages={stage_count}, slides={total_slides}, "
                f"method={generation_method}, time={generation_time_seconds}s"
            )
            
            return persisted_plan
            
        except Exception as e:
            end_time = time.time()
            generation_time_seconds = int(end_time - start_time)
            
            logger.error(
                f"❌ Failed to generate and persist plan for session {learner_session_id}: "
                f"{type(e).__name__}: {e} (after {generation_time_seconds}s)"
            )
            raise
        
        finally:
            # Nettoyer le contexte
            self._current_learner_session_id = None
            self._pending_api_logs.clear()
    
    async def _persist_pending_api_logs(self):
        """Persister tous les logs API en attente"""
        for args, kwargs in self._pending_api_logs:
            try:
                await self._persist_api_log(*args, **kwargs)
            except Exception as e:
                logger.error(f"❌ Failed to persist pending API log: {e}")
        
        self._pending_api_logs.clear()
    
    async def get_plan_for_session(self, learner_session_id: UUID) -> Optional[LearnerTrainingPlan]:
        """
        Récupérer le plan le plus récent pour une session apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            
        Returns:
            Plan de formation ou None si aucun trouvé
        """
        return await self.plan_repository.get_latest_by_learner_session_id(learner_session_id)
    
    async def get_all_plans_for_session(self, learner_session_id: UUID) -> list[LearnerTrainingPlan]:
        """
        Récupérer tous les plans pour une session apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            
        Returns:
            Liste des plans de formation
        """
        return await self.plan_repository.get_by_learner_session_id(learner_session_id)
    
    async def update_plan(
        self,
        plan_id: UUID,
        new_plan_data: Dict[str, Any]
    ) -> LearnerTrainingPlan:
        """
        Mettre à jour un plan existant
        
        Args:
            plan_id: ID du plan à mettre à jour
            new_plan_data: Nouvelles données du plan
            
        Returns:
            Plan mis à jour
        """
        # Récupérer le plan existant
        existing_plan = await self.plan_repository.get_by_id(plan_id)
        if not existing_plan:
            raise ValueError(f"Plan with ID {plan_id} not found")
        
        # Mettre à jour les données
        existing_plan.update_plan_data(new_plan_data)
        existing_plan.validate()
        
        # Persister la mise à jour
        updated_plan = await self.plan_repository.update(existing_plan)
        
        logger.info(f"✅ Plan updated successfully: ID={plan_id}")
        return updated_plan
    
    async def delete_plan(self, plan_id: UUID) -> bool:
        """
        Supprimer un plan de formation
        
        Args:
            plan_id: ID du plan à supprimer
            
        Returns:
            True si supprimé avec succès
        """
        result = await self.plan_repository.delete(plan_id)
        if result:
            logger.info(f"✅ Plan deleted successfully: ID={plan_id}")
        else:
            logger.warning(f"⚠️ Plan not found for deletion: ID={plan_id}")
        return result
    
    async def get_api_logs_for_session(self, learner_session_id: UUID) -> list:
        """
        Récupérer les logs API pour une session apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            
        Returns:
            Liste des logs API
        """
        return await self.api_log_repository.get_by_learner_session_id(learner_session_id)
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Obtenir des statistiques sur la génération de plans
        
        Returns:
            Dictionnaire avec les statistiques
        """
        try:
            # Plans par méthode de génération
            vertex_plans = await self.plan_repository.get_plans_by_generation_method("vertex_ai", limit=1000)
            fallback_plans = await self.plan_repository.get_plans_by_generation_method("fallback", limit=1000)
            
            # Plans avec de bonnes performances (< 30s de génération)
            fast_plans = await self.plan_repository.get_plans_with_performance_metrics(
                max_generation_time=30
            )
            
            # Statistiques générales
            stats = {
                "total_plans_generated": len(vertex_plans) + len(fallback_plans),
                "vertex_ai_plans": len(vertex_plans),
                "fallback_plans": len(fallback_plans),
                "fast_generation_plans": len(fast_plans),
                "vertex_ai_success_rate": len(vertex_plans) / max(len(vertex_plans) + len(fallback_plans), 1) * 100,
                "average_slides_per_plan": sum(plan.get_total_slides() for plan in vertex_plans + fallback_plans) / max(len(vertex_plans) + len(fallback_plans), 1)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get generation statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérification de santé du service intégré
        
        Returns:
            Statut de santé
        """
        try:
            # Test du service de génération simple
            simple_service_healthy = self.plan_generation_service.client is not None
            
            # Test des repositories (tentative de connexion DB)
            db_healthy = True
            try:
                # Test simple : essayer de récupérer des plans (limite 1)
                await self.plan_repository.get_plans_by_generation_method("vertex_ai", limit=1)
            except Exception:
                db_healthy = False
            
            return {
                "status": "healthy" if simple_service_healthy and db_healthy else "unhealthy",
                "service": "integrated_plan_generation",
                "components": {
                    "plan_generation_service": "healthy" if simple_service_healthy else "unhealthy",
                    "database_repositories": "healthy" if db_healthy else "unhealthy"
                },
                "vertex_ai_configured": simple_service_healthy,
                "model": self.plan_generation_service.model_name
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "integrated_plan_generation",
                "error": str(e)
            }