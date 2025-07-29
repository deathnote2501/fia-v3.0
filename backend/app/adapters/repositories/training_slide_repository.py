"""
FIA v3.0 - Training Slide Repository
Repository for slides table operations (using existing slides table)
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from app.infrastructure.models.training_slide_model import TrainingSlideModel
from app.domain.entities.training_slide import TrainingSlide, SlideType


class TrainingSlideRepository:
    """Repository for training slide operations"""
    
    def __init__(self, session: AsyncSession = None):
        self.session = session
    
    def set_session(self, session: AsyncSession):
        """Set database session"""
        self.session = session
    
    async def get_by_id(self, slide_id: UUID) -> Optional[TrainingSlideModel]:
        """Get training slide by ID"""
        if not self.session:
            raise ValueError("Database session not set")
        
        result = await self.session.execute(
            select(TrainingSlideModel)
            .where(TrainingSlideModel.id == slide_id)
            .options(selectinload(TrainingSlideModel.training_submodule))
        )
        return result.scalar_one_or_none()
    
    async def get_first_slide(self, training_plan_id: UUID) -> Optional[TrainingSlideModel]:
        """Get the first slide of a training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Import needed models for joins
        from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
        from app.infrastructure.models.training_module_model import TrainingModuleModel
        
        # Query to get the first slide of the first submodule of the first module
        result = await self.session.execute(
            select(TrainingSlideModel)
            .join(TrainingSubmoduleModel, TrainingSlideModel.submodule_id == TrainingSubmoduleModel.id)
            .join(TrainingModuleModel, TrainingSubmoduleModel.module_id == TrainingModuleModel.id)
            .where(TrainingModuleModel.plan_id == training_plan_id)
            .order_by(
                TrainingModuleModel.stage_number,
                TrainingModuleModel.order_in_stage,
                TrainingSubmoduleModel.order_in_module,
                TrainingSlideModel.order_in_submodule
            )
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_slides_by_submodule(self, submodule_id: UUID) -> List[TrainingSlideModel]:
        """Get all slides for a submodule, ordered by order_in_submodule"""
        if not self.session:
            raise ValueError("Database session not set")
        
        result = await self.session.execute(
            select(TrainingSlideModel)
            .where(TrainingSlideModel.submodule_id == submodule_id)
            .order_by(TrainingSlideModel.order_in_submodule)
        )
        return list(result.scalars().all())
    
    async def update_content(self, slide_id: UUID, content: str) -> bool:
        """Update slide content and mark as generated"""
        if not self.session:
            raise ValueError("Database session not set")
        
        try:
            await self.session.execute(
                update(TrainingSlideModel)
                .where(TrainingSlideModel.id == slide_id)
                .values(
                    content=content,
                    generated_at=datetime.now(timezone.utc)
                )
            )
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False
    
    async def get_slides_by_training_plan(self, training_plan_id: UUID) -> List[TrainingSlideModel]:
        """Get all slides for a training plan, ordered by module/submodule/slide order"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Import needed models for joins
        from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
        from app.infrastructure.models.training_module_model import TrainingModuleModel
        
        result = await self.session.execute(
            select(TrainingSlideModel)
            .join(TrainingSubmoduleModel, TrainingSlideModel.submodule_id == TrainingSubmoduleModel.id)
            .join(TrainingModuleModel, TrainingSubmoduleModel.module_id == TrainingModuleModel.id)
            .where(TrainingModuleModel.plan_id == training_plan_id)
            .order_by(
                TrainingModuleModel.stage_number,
                TrainingModuleModel.order_in_stage,
                TrainingSubmoduleModel.order_in_module,
                TrainingSlideModel.order_in_submodule
            )
            .options(
                selectinload(TrainingSlideModel.training_submodule)
            )
        )
        return list(result.scalars().all())
    
    async def get_next_slide(self, current_slide_id: UUID, training_plan_id: UUID) -> Optional[TrainingSlideModel]:
        """Get the next slide after the current one in the training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Get all slides ordered
        all_slides = await self.get_slides_by_training_plan(training_plan_id)
        
        # Find current slide index
        current_index = None
        for i, slide in enumerate(all_slides):
            if slide.id == current_slide_id:
                current_index = i
                break
        
        # Return next slide if exists
        if current_index is not None and current_index + 1 < len(all_slides):
            return all_slides[current_index + 1]
        
        return None
    
    async def get_previous_slide(self, current_slide_id: UUID, training_plan_id: UUID) -> Optional[TrainingSlideModel]:
        """Get the previous slide before the current one in the training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Get all slides ordered
        all_slides = await self.get_slides_by_training_plan(training_plan_id)
        
        # Find current slide index
        current_index = None
        for i, slide in enumerate(all_slides):
            if slide.id == current_slide_id:
                current_index = i
                break
        
        # Return previous slide if exists
        if current_index is not None and current_index > 0:
            return all_slides[current_index - 1]
        
        return None
    
    async def get_slide_position(self, slide_id: UUID, training_plan_id: UUID) -> dict:
        """Get position information for a slide within the training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Get all slides ordered
        all_slides = await self.get_slides_by_training_plan(training_plan_id)
        
        # Find current slide index
        current_index = None
        for i, slide in enumerate(all_slides):
            if slide.id == slide_id:
                current_index = i
                break
        
        if current_index is not None:
            return {
                "current_position": current_index + 1,
                "total_slides": len(all_slides),
                "has_previous": current_index > 0,
                "has_next": current_index + 1 < len(all_slides)
            }
        
        return {
            "current_position": 0,
            "total_slides": len(all_slides),
            "has_previous": False,
            "has_next": False
        }
    
    async def create_slide(self, training_slide: TrainingSlide) -> TrainingSlideModel:
        """Create a new training slide"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Validate domain entity
        training_slide.validate()
        
        # Create SQLAlchemy model
        slide_model = TrainingSlideModel(
            id=training_slide.id,
            submodule_id=training_slide.submodule_id,
            order_in_submodule=training_slide.order_in_submodule,
            title=training_slide.title,
            slide_type=training_slide.slide_type.value,
            content=training_slide.content,
            generated_at=training_slide.generated_at,
            created_at=training_slide.created_at
        )
        
        self.session.add(slide_model)
        await self.session.commit()
        await self.session.refresh(slide_model)
        
        return slide_model
    
    async def get_slides_by_type(self, training_plan_id: UUID, slide_type: SlideType) -> List[TrainingSlideModel]:
        """Get all slides of a specific type for a training plan"""
        if not self.session:
            raise ValueError("Database session not set")
        
        # Import needed models for joins
        from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
        from app.infrastructure.models.training_module_model import TrainingModuleModel
        
        result = await self.session.execute(
            select(TrainingSlideModel)
            .join(TrainingSubmoduleModel, TrainingSlideModel.submodule_id == TrainingSubmoduleModel.id)
            .join(TrainingModuleModel, TrainingSubmoduleModel.module_id == TrainingModuleModel.id)
            .where(TrainingModuleModel.plan_id == training_plan_id)
            .where(TrainingSlideModel.slide_type == slide_type.value)
            .order_by(
                TrainingModuleModel.stage_number,
                TrainingModuleModel.order_in_stage,
                TrainingSubmoduleModel.order_in_module,
                TrainingSlideModel.order_in_submodule
            )
        )
        return list(result.scalars().all())
    
    def model_to_entity(self, model: TrainingSlideModel) -> TrainingSlide:
        """Convert SQLAlchemy model to domain entity"""
        return TrainingSlide(
            id=model.id,
            submodule_id=model.submodule_id,
            order_in_submodule=model.order_in_submodule,
            title=model.title,
            slide_type=SlideType(model.slide_type),
            content=model.content,
            generated_at=model.generated_at,
            created_at=model.created_at
        )
    
    def entity_to_model(self, entity: TrainingSlide) -> TrainingSlideModel:
        """Convert domain entity to SQLAlchemy model"""
        return TrainingSlideModel(
            id=entity.id,
            submodule_id=entity.submodule_id,
            order_in_submodule=entity.order_in_submodule,
            title=entity.title,
            slide_type=entity.slide_type.value,
            content=entity.content,
            generated_at=entity.generated_at,
            created_at=entity.created_at
        )
    
    async def get_previous_content_slides(self, current_slide_id: UUID, training_plan_id: UUID, scope: str = "submodule") -> List[TrainingSlideModel]:
        """
        Récupérer les slides de contenu précédentes pour générer un quiz
        
        Args:
            current_slide_id: ID de la slide de quiz actuelle
            training_plan_id: ID du plan de formation
            scope: Portée du quiz ("submodule", "module", "stage")
            
        Returns:
            Liste des slides de contenu précédentes selon la portée
        """
        if not self.session:
            raise ValueError("Database session not set")
        
        from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
        from app.infrastructure.models.training_module_model import TrainingModuleModel
        
        try:
            # D'abord, obtenir la slide actuelle pour connaître sa position
            current_slide = await self.get_by_id(current_slide_id)
            if not current_slide:
                return []
            
            # Obtenir toutes les slides du plan dans l'ordre
            all_slides = await self.get_slides_by_training_plan(training_plan_id)
            
            # Trouver l'index de la slide actuelle
            current_index = None
            for i, slide in enumerate(all_slides):
                if slide.id == current_slide_id:
                    current_index = i
                    break
            
            if current_index is None:
                return []
            
            # Sélectionner les slides précédentes selon la portée
            if scope == "submodule":
                # Quiz de sous-module : récupérer les slides content du même sous-module
                content_slides = []
                for i in range(current_index - 1, -1, -1):
                    slide = all_slides[i]
                    if slide.submodule_id == current_slide.submodule_id and slide.slide_type == "content":
                        content_slides.insert(0, slide)  # Insérer au début pour garder l'ordre
                    elif slide.submodule_id != current_slide.submodule_id:
                        break  # On est sorti du sous-module
                return content_slides
                
            elif scope == "module":
                # Quiz de module : récupérer toutes les slides content du module
                current_module_id = await self._get_module_id_from_slide(current_slide)
                if not current_module_id:
                    return []
                
                content_slides = []
                for i in range(current_index - 1, -1, -1):
                    slide = all_slides[i]
                    slide_module_id = await self._get_module_id_from_slide(slide)
                    if slide_module_id == current_module_id and slide.slide_type == "content":
                        content_slides.insert(0, slide)
                    elif slide_module_id != current_module_id:
                        break  # On est sorti du module
                return content_slides
                
            elif scope == "stage":
                # Quiz d'étape : récupérer toutes les slides content de l'étape
                current_stage_number = await self._get_stage_number_from_slide(current_slide)
                if not current_stage_number:
                    return []
                
                content_slides = []
                for i in range(current_index - 1, -1, -1):
                    slide = all_slides[i]
                    slide_stage_number = await self._get_stage_number_from_slide(slide)
                    if slide_stage_number == current_stage_number and slide.slide_type == "content":
                        content_slides.insert(0, slide)
                    elif slide_stage_number != current_stage_number:
                        break  # On est sorti de l'étape
                return content_slides
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting previous content slides: {e}")
            return []
    
    async def _get_module_id_from_slide(self, slide: TrainingSlideModel) -> Optional[UUID]:
        """Obtenir l'ID du module d'une slide via son sous-module"""
        try:
            result = await self.session.execute(
                select(TrainingSubmoduleModel.module_id)
                .where(TrainingSubmoduleModel.id == slide.submodule_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def _get_stage_number_from_slide(self, slide: TrainingSlideModel) -> Optional[int]:
        """Obtenir le numéro d'étape d'une slide via son sous-module et module"""
        try:
            from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
            from app.infrastructure.models.training_module_model import TrainingModuleModel
            
            result = await self.session.execute(
                select(TrainingModuleModel.stage_number)
                .join(TrainingSubmoduleModel, TrainingModuleModel.id == TrainingSubmoduleModel.module_id)
                .where(TrainingSubmoduleModel.id == slide.submodule_id)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def get_slide_breadcrumb(self, slide_id: UUID) -> dict:
        """
        Récupérer les informations de fil d'Ariane pour une slide donnée
        
        Returns:
            Dict avec stage_name, module_name, submodule_name
        """
        if not self.session:
            raise ValueError("Database session not set")
        
        try:
            from app.infrastructure.models.training_submodule_model import TrainingSubmoduleModel
            from app.infrastructure.models.training_module_model import TrainingModuleModel
            
            # Requête pour récupérer toutes les informations en une seule fois
            result = await self.session.execute(
                select(
                    TrainingModuleModel.stage_number,
                    TrainingModuleModel.title.label('module_title'),
                    TrainingSubmoduleModel.title.label('submodule_title')
                )
                .join(TrainingSubmoduleModel, TrainingModuleModel.id == TrainingSubmoduleModel.module_id)
                .join(TrainingSlideModel, TrainingSubmoduleModel.id == TrainingSlideModel.submodule_id)
                .where(TrainingSlideModel.id == slide_id)
            )
            
            row = result.first()
            if not row:
                return {
                    "stage_name": "Formation",
                    "module_name": "Module",
                    "submodule_name": "Contenu"
                }
            
            # Mapping des numéros d'étapes vers leurs noms
            stage_names = {
                1: "Mise en contexte",
                2: "Acquisition des fondamentaux", 
                3: "Construction progressive",
                4: "Maîtrise",
                5: "Validation"
            }
            
            return {
                "stage_name": stage_names.get(row.stage_number, f"Étape {row.stage_number}"),
                "module_name": row.module_title or "Module",
                "submodule_name": row.submodule_title or "Contenu"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting slide breadcrumb: {e}")
            return {
                "stage_name": "Formation",
                "module_name": "Module", 
                "submodule_name": "Contenu"
            }