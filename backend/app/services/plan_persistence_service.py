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
from app.domain.entities.training_slide import SlideType

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
            
            # 1. Créer la slide de plan global (première slide)
            await self._create_plan_slide(plan_id, training_plan)
            
            # 2. Persister chaque étape et ses modules
            for stage_index, stage in enumerate(stages):
                await self._persist_stage_modules(
                    plan_id, 
                    stage, 
                    training_plan.get("plan_slide", {}),
                    is_first_stage=(stage_index == 0),
                    is_last_stage=(stage_index == len(stages) - 1)
                )
            
            # IMPORTANT: Committer la transaction
            await self.session.commit()
            
            logger.info(f"✅ Plan structure persisted successfully for plan {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error persisting plan structure for plan {plan_id}: {e}")
            await self.session.rollback()
            return False
    
    async def _persist_stage_modules(
        self, 
        plan_id: UUID, 
        stage: Dict[str, Any], 
        plan_slide_data: Dict[str, Any], 
        is_first_stage: bool = False, 
        is_last_stage: bool = False
    ) -> None:
        """Persiste les modules d'une étape"""
        stage_number = stage.get("stage_number")
        stage_name = stage.get("title", stage.get("stage_name"))
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
            
            # Persister les sous-modules avec les informations de stage et module
            await self._persist_module_submodules(
                module_model.id, 
                module, 
                stage, 
                plan_slide_data,
                is_first_module=(module_index == 0),
                is_last_module=(module_index == len(modules) - 1),
                is_first_stage=is_first_stage,
                is_last_stage=is_last_stage
            )
    
    async def _persist_module_submodules(
        self, 
        module_id: UUID, 
        module: Dict[str, Any], 
        stage: Dict[str, Any], 
        plan_slide_data: Dict[str, Any],
        is_first_module: bool = False,
        is_last_module: bool = False,
        is_first_stage: bool = False,
        is_last_stage: bool = False
    ) -> None:
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
            
            # Persister les slides avec les nouvelles typologies
            await self._persist_submodule_slides_with_types(
                submodule_model.id, 
                submodule, 
                stage, 
                module, 
                plan_slide_data,
                is_first_submodule=(submodule_index == 0),
                is_first_module=is_first_module,
                is_last_submodule=(submodule_index == len(submodules) - 1),
                is_last_module=is_last_module,
                is_first_stage=is_first_stage,
                is_last_stage=is_last_stage
            )
    
    async def _persist_submodule_slides(self, submodule_id: UUID, submodule: Dict[str, Any]) -> None:
        """Persiste les slides d'un sous-module"""
        slide_count = submodule.get("slide_count", 0)
        submodule_name = submodule.get("submodule_name", "")
        slide_titles = submodule.get("slide_titles", [])
        
        logger.debug(f"📝 Creating {slide_count} slides for submodule {submodule_id}")
        
        # Créer les slides avec les titres générés par l'IA ou des titres génériques
        for slide_index in range(slide_count):
            # Utiliser le titre généré par l'IA si disponible, sinon titre générique
            if slide_index < len(slide_titles):
                slide_title = slide_titles[slide_index]
            else:
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
    
    async def _create_plan_slide(self, plan_id: UUID, training_plan: Dict[str, Any]) -> None:
        """Créer la slide de plan global (première slide de la formation)"""
        # Pour la slide de plan, nous devons l'associer au premier submodule
        # Nous allons la créer lors du traitement du premier submodule
        logger.debug(f"📝 Plan slide will be created with first submodule")
        pass
    
    async def _create_stage_slide(self, submodule_id: UUID, stage: Dict[str, Any], order: int) -> None:
        """Créer la slide d'introduction d'étape"""
        stage_slide_data = stage.get("stage_slide", {})
        if stage_slide_data:
            slide_title = stage_slide_data.get("title", f"Étape {stage.get('stage_number')}: {stage.get('title')}")
            
            slide_model = TrainingSlideModel(
                submodule_id=submodule_id,
                order_in_submodule=order,
                title=slide_title,
                slide_type=SlideType.STAGE.value,
                content=None,
                generated_at=None
            )
            
            self.session.add(slide_model)
            logger.debug(f"📝 Created stage slide: {slide_title}")
    
    async def _create_module_slide(self, submodule_id: UUID, module: Dict[str, Any], order: int) -> None:
        """Créer la slide d'introduction de module"""
        module_slide_data = module.get("module_slide", {})
        if module_slide_data:
            slide_title = module_slide_data.get("title", f"Module: {module.get('module_name')}")
            
            slide_model = TrainingSlideModel(
                submodule_id=submodule_id,
                order_in_submodule=order,
                title=slide_title,
                slide_type=SlideType.MODULE.value,
                content=None,
                generated_at=None
            )
            
            self.session.add(slide_model)
            logger.debug(f"📝 Created module slide: {slide_title}")
    
    async def _create_quiz_slide(self, submodule_id: UUID, quiz_data: Dict[str, Any], order: int) -> None:
        """Créer une slide de quiz"""
        if quiz_data:
            slide_title = quiz_data.get("title", "Quiz")
            
            slide_model = TrainingSlideModel(
                submodule_id=submodule_id,
                order_in_submodule=order,
                title=slide_title,
                slide_type=SlideType.QUIZ.value,
                content=None,
                generated_at=None
            )
            
            self.session.add(slide_model)
            logger.debug(f"📝 Created quiz slide: {slide_title}")
    
    async def _persist_submodule_slides_with_types(
        self, 
        submodule_id: UUID, 
        submodule: Dict[str, Any], 
        stage: Dict[str, Any], 
        module: Dict[str, Any], 
        plan_slide_data: Dict[str, Any],
        is_first_submodule: bool = False,
        is_first_module: bool = False,
        is_last_submodule: bool = False,
        is_last_module: bool = False,
        is_first_stage: bool = False,
        is_last_stage: bool = False
    ) -> None:
        """Persiste les slides d'un sous-module avec les nouvelles typologies"""
        
        slide_order = 1
        
        # 1. Si c'est le tout premier sous-module, créer la slide de plan
        if is_first_submodule and is_first_module and is_first_stage:
            if not plan_slide_data:
                # Fallback si pas de plan_slide dans le JSON
                plan_slide_data = {"title": "Plan de Formation", "slide_type": "plan"}
            
            await self._create_slide_with_type(submodule_id, plan_slide_data, slide_order, SlideType.PLAN)
            slide_order += 1
        
        # 2. Si c'est le premier sous-module du premier module, créer la slide d'étape
        if is_first_submodule and is_first_module:
            stage_slide_data = stage.get("stage_slide", {})
            if stage_slide_data:
                await self._create_slide_with_type(submodule_id, stage_slide_data, slide_order, SlideType.STAGE)
                slide_order += 1
        
        # # 3. Si c'est le premier sous-module du module, créer la slide de module > commenté volontairement ne pas décommenter !!!
        # if is_first_submodule:
        #     module_slide_data = module.get("module_slide", {})
        #     if module_slide_data:
        #         await self._create_slide_with_type(submodule_id, module_slide_data, slide_order, SlideType.MODULE)
        #         slide_order += 1
        
        # 4. Créer les slides de contenu du sous-module
        slide_count = submodule.get("slide_count", 0)
        slide_titles = submodule.get("slide_titles", [])
        slide_types = submodule.get("slide_types", ["content"] * slide_count)
        
        logger.debug(f"📝 Creating {slide_count} content slides for submodule {submodule_id}")
        
        for slide_index in range(slide_count):
            # Utiliser le titre généré par l'IA si disponible
            if slide_index < len(slide_titles):
                slide_title = slide_titles[slide_index]
            else:
                slide_title = f"{submodule.get('submodule_name', '')} - Slide {slide_index + 1}"
            
            # Utiliser le type spécifié ou 'content' par défaut
            slide_type_str = slide_types[slide_index] if slide_index < len(slide_types) else "content"
            slide_type = SlideType.CONTENT  # Toujours content pour les slides normales
            
            await self._create_slide_with_type(
                submodule_id, 
                {"title": slide_title, "slide_type": slide_type_str}, 
                slide_order, 
                slide_type
            )
            slide_order += 1
        
        # 5. Créer la slide de quiz du sous-module
        quiz_slide_data = submodule.get("quiz_slide", {})
        if quiz_slide_data:
            await self._create_slide_with_type(submodule_id, quiz_slide_data, slide_order, SlideType.QUIZ)
            slide_order += 1
        
        # 6. Si c'est le dernier sous-module du module, créer le quiz du module
        if is_last_submodule:
            module_quiz_data = module.get("module_quiz_slide", {})
            if module_quiz_data:
                await self._create_slide_with_type(submodule_id, module_quiz_data, slide_order, SlideType.QUIZ)
                slide_order += 1
        
        # 7. Si c'est le dernier sous-module du dernier module de l'étape, créer le quiz de l'étape
        if is_last_submodule and is_last_module:
            stage_quiz_data = stage.get("stage_quiz_slide", {})
            if stage_quiz_data:
                await self._create_slide_with_type(submodule_id, stage_quiz_data, slide_order, SlideType.QUIZ)
                slide_order += 1
    
    async def _create_slide_with_type(
        self, 
        submodule_id: UUID, 
        slide_data: Dict[str, Any], 
        order: int, 
        slide_type: SlideType
    ) -> None:
        """Créer une slide avec un type spécifique"""
        slide_title = slide_data.get("title", "Slide sans titre")
        
        slide_model = TrainingSlideModel(
            submodule_id=submodule_id,
            order_in_submodule=order,
            title=slide_title,
            slide_type=slide_type.value,
            content=None,
            generated_at=None
        )
        
        self.session.add(slide_model)
        logger.debug(f"📝 Created {slide_type.value} slide: {slide_title} (order: {order})")