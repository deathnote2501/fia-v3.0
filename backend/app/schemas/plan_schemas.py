"""
FIA v3.0 - Plan Generation Schemas (Minimal)
Schemas Pydantic minimaux pour génération de plans
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List
from uuid import UUID


class LearnerProfileRequest(BaseModel):
    """Schema minimal pour profil apprenant"""
    experience_level: str = Field(..., description="Niveau: beginner, intermediate, advanced")
    learning_style: str = Field(..., description="Style: visual, auditory, kinesthetic, reading")
    job_position: str = Field(..., description="Poste occupé")
    activity_sector: str = Field(..., description="Secteur d'activité") 
    country: str = Field(default="France", description="Pays de résidence")
    language: str = Field(default="fr", description="Langue préférée")


class PlanGenerationRequest(BaseModel):
    """Schema pour requête de génération de plan"""
    training_id: UUID = Field(..., description="ID de la formation")
    learner_profile: LearnerProfileRequest = Field(..., description="Profil de l'apprenant")
    force_regenerate: bool = Field(default=False, description="Forcer la régénération")


class SubmoduleSchema(BaseModel):
    """Schema pour sous-module"""
    submodule_name: str = Field(..., description="Nom du sous-module")
    slide_count: int = Field(..., ge=1, le=10, description="Nombre de slides")


class ModuleSchema(BaseModel):
    """Schema pour module"""
    module_name: str = Field(..., description="Nom du module")
    submodules: List[SubmoduleSchema] = Field(..., description="Liste des sous-modules")


class StageSchema(BaseModel):
    """Schema pour étape de formation"""
    stage_number: int = Field(..., ge=1, le=5, description="Numéro d'étape (1-5)")
    stage_name: str = Field(..., description="Nom de l'étape")
    modules: List[ModuleSchema] = Field(..., description="Liste des modules")


class TrainingPlanSchema(BaseModel):
    """Schema pour plan de formation"""
    stages: List[StageSchema] = Field(..., min_items=5, max_items=5, description="Exactement 5 étapes")


class PlanGenerationResponse(BaseModel):
    """Schema pour réponse de génération de plan"""
    success: bool = Field(..., description="Succès de la génération")
    training_plan: TrainingPlanSchema = Field(..., description="Plan de formation généré")
    generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées de génération")
    message: str = Field(default="Plan generated successfully", description="Message de statut")


class ErrorResponse(BaseModel):
    """Schema pour réponse d'erreur"""
    success: bool = Field(default=False, description="Échec de l'opération")
    error_type: str = Field(..., description="Type d'erreur")
    error_message: str = Field(..., description="Message d'erreur")
    details: Dict[str, Any] = Field(default_factory=dict, description="Détails supplémentaires")