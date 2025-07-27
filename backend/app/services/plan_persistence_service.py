"""
FIA v3.0 - Plan Persistence Service
Service pour persister les plans JSON dans les tables relationnelles
"""

import logging
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.training_module_model import TrainingModuleModel
from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
from app.infrastructure.models.training_slide_model import TrainingSlideModel

logger = logging.getLogger(__name__)


class PlanPersistenceService:
    """Service pour persister les plans de formation dans les tables relationnelles"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def persist_plan_structure(self, plan_id: UUID, plan_data: Dict[str, Any]) -> bool:
        """
        Persiste la structure du plan dans les tables relationnelles
        
        Args:
            plan_id: ID du plan de formation
            plan_data: Données JSON du plan généré
            
        Returns:
            True si la persistance a réussi
        """
        try:
            logger.info(f"🗄️ Starting plan structure persistence for plan {plan_id}")
            
            # Extraire la structure du plan
            training_plan = plan_data.get("training_plan", {})
            stages = training_plan.get("stages", [])
            
            if not stages:
                logger.warning(f"⚠️ No stages found in plan data for plan {plan_id}")
                return False
            
            # Persister chaque étape et ses modules
            for stage in stages:
                await self._persist_stage_modules(plan_id, stage)
            
            logger.info(f"✅ Plan structure persisted successfully for plan {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error persisting plan structure for plan {plan_id}: {e}")
            await self.session.rollback()
            return False
    
    async def _persist_stage_modules(self, plan_id: UUID, stage: Dict[str, Any]) -> None:
        """Persiste les modules d'une étape"""
        stage_number = stage.get("stage_number")
        stage_name = stage.get("stage_name")
        modules = stage.get("modules", [])
        
        logger.debug(f"📝 Persisting stage {stage_number}: {stage_name} ({len(modules)} modules)")
        
        for module_index, module in enumerate(modules):
            module_model = TrainingModuleModel(
                plan_id=plan_id,
                stage_number=stage_number,
                order_in_stage=module_index + 1,
                title=module.get("module_name", ""),
                description=None  # Peut être ajouté plus tard si nécessaire
            )
            
            self.session.add(module_model)
            await self.session.flush()  # Pour obtenir l'ID du module
            
            # Persister les sous-modules
            await self._persist_module_submodules(module_model.id, module)
    
    async def _persist_module_submodules(self, module_id: UUID, module: Dict[str, Any]) -> None:
        """Persiste les sous-modules d'un module"""
        submodules = module.get("submodules", [])
        
        logger.debug(f"📝 Persisting {len(submodules)} submodules for module {module_id}")
        
        for submodule_index, submodule in enumerate(submodules):
            submodule_model = TrainingSubmoduleModel(
                module_id=module_id,
                order_in_module=submodule_index + 1,
                title=submodule.get("submodule_name", ""),
                description=None
            )
            
            self.session.add(submodule_model)
            await self.session.flush()  # Pour obtenir l'ID du sous-module
            
            # Persister les slides
            await self._persist_submodule_slides(submodule_model.id, submodule)
    
    async def _persist_submodule_slides(self, submodule_id: UUID, submodule: Dict[str, Any]) -> None:
        """Persiste les slides d'un sous-module"""
        slide_count = submodule.get("slide_count", 0)
        submodule_name = submodule.get("submodule_name", "")
        
        logger.debug(f"📝 Creating {slide_count} slides for submodule {submodule_id}")
        
        # Créer les slides avec des titres génériques (le contenu sera généré à la demande)
        for slide_index in range(slide_count):
            slide_title = f"{submodule_name} - Slide {slide_index + 1}"
            
            slide_model = TrainingSlideModel(
                submodule_id=submodule_id,
                order_in_submodule=slide_index + 1,
                title=slide_title,
                content=None,  # Contenu généré à la demande
                generated_at=None
            )
            
            self.session.add(slide_model)
    
    async def get_plan_statistics(self, plan_id: UUID) -> Dict[str, int]:
        """Obtient les statistiques d'un plan persisté"""
        try:
            from sqlalchemy import text
            
            # Compter les modules
            modules_result = await self.session.execute(
                text("SELECT COUNT(*) FROM training_modules WHERE plan_id = :plan_id"),
                {"plan_id": plan_id}
            )
            modules_count = modules_result.scalar()
            
            # Compter les sous-modules
            submodules_result = await self.session.execute(
                text("""SELECT COUNT(*) FROM training_submodules ts 
                        JOIN training_modules tm ON ts.module_id = tm.id 
                        WHERE tm.plan_id = :plan_id"""),
                {"plan_id": plan_id}
            )
            submodules_count = submodules_result.scalar()
            
            # Compter les slides
            slides_result = await self.session.execute(
                text("""SELECT COUNT(*) FROM training_slides tsl
                        JOIN training_submodules ts ON tsl.submodule_id = ts.id
                        JOIN training_modules tm ON ts.module_id = tm.id 
                        WHERE tm.plan_id = :plan_id"""),
                {"plan_id": plan_id}
            )
            slides_count = slides_result.scalar()
            
            return {
                "modules_count": modules_count or 0,
                "submodules_count": submodules_count or 0,
                "slides_count": slides_count or 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting plan statistics for plan {plan_id}: {e}")
            return {
                "modules_count": 0,
                "submodules_count": 0,
                "slides_count": 0
            }