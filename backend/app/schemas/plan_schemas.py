"""
FIA v3.0 - Plan Generation Schemas (Minimal)
Schemas Pydantic minimaux pour génération de plans
"""

from pydantic import BaseModel, Field, validator, ValidationError
from typing import Dict, Any, List, Literal
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
    learner_session_id: UUID = Field(..., description="ID de la session apprenant")
    learner_profile: LearnerProfileRequest = Field(..., description="Profil de l'apprenant")
    force_regenerate: bool = Field(default=False, description="Forcer la régénération")


class SubmoduleSchema(BaseModel):
    """Schema pour sous-module avec validation stricte"""
    submodule_name: str = Field(..., min_length=5, max_length=150, description="Nom du sous-module (5-150 chars)")
    slide_count: int = Field(..., ge=2, le=8, description="Nombre de slides (2-8)")
    
    @validator('submodule_name')
    def validate_submodule_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Submodule name must be a non-empty string')
        if len(v.strip()) < 5:
            raise ValueError('Submodule name must be at least 5 characters')
        return v.strip()


class ModuleSchema(BaseModel):
    """Schema pour module avec validation stricte"""
    module_name: str = Field(..., min_length=5, max_length=100, description="Nom du module (5-100 chars)")
    submodules: List[SubmoduleSchema] = Field(..., min_items=1, max_items=4, description="1-4 sous-modules")
    
    @validator('module_name')
    def validate_module_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Module name must be a non-empty string')
        if len(v.strip()) < 5:
            raise ValueError('Module name must be at least 5 characters')
        return v.strip()
    
    @validator('submodules')
    def validate_submodules_count(cls, v):
        if not isinstance(v, list) or len(v) < 1:
            raise ValueError('Each module must have at least 1 submodule')
        if len(v) > 4:
            raise ValueError('Each module cannot have more than 4 submodules')
        return v


class StageSchema(BaseModel):
    """Schema pour étape de formation avec validation stricte"""
    stage_number: int = Field(..., ge=1, le=5, description="Numéro d'étape (1-5)")
    stage_name: Literal[
        "Mise en contexte",
        "Acquisition des fondamentaux", 
        "Construction progressive",
        "Maîtrise",
        "Validation"
    ] = Field(..., description="Nom exact de l'étape selon SPEC.md")
    modules: List[ModuleSchema] = Field(..., min_items=1, max_items=3, description="1-3 modules par étape")
    
    @validator('stage_name')
    def validate_stage_name_matches_number(cls, v, values):
        """Valider que le nom d'étape correspond au numéro"""
        if 'stage_number' not in values:
            return v
            
        stage_number = values['stage_number']
        expected_names = {
            1: "Mise en contexte",
            2: "Acquisition des fondamentaux", 
            3: "Construction progressive",
            4: "Maîtrise",
            5: "Validation"
        }
        
        expected_name = expected_names.get(stage_number)
        if v != expected_name:
            raise ValueError(f'Stage {stage_number} must be named "{expected_name}", got "{v}"')
        
        return v
    
    @validator('modules')
    def validate_modules_count(cls, v):
        if not isinstance(v, list) or len(v) < 1:
            raise ValueError('Each stage must have at least 1 module')
        if len(v) > 3:
            raise ValueError('Each stage cannot have more than 3 modules')
        return v


class TrainingPlanSchema(BaseModel):
    """Schema pour plan de formation avec validation stricte"""
    stages: List[StageSchema] = Field(..., min_items=5, max_items=5, description="Exactement 5 étapes")
    
    @validator('stages')
    def validate_stages_structure(cls, v):
        """Validation complète de la structure des étapes"""
        if not isinstance(v, list):
            raise ValueError('Stages must be a list')
        
        if len(v) != 5:
            raise ValueError(f'Must have exactly 5 stages, got {len(v)}')
        
        # Vérifier que tous les numéros d'étapes sont présents et uniques
        stage_numbers = [stage.stage_number for stage in v]
        expected_numbers = {1, 2, 3, 4, 5}
        found_numbers = set(stage_numbers)
        
        if found_numbers != expected_numbers:
            missing = expected_numbers - found_numbers
            duplicates = [num for num in stage_numbers if stage_numbers.count(num) > 1]
            
            if missing:
                raise ValueError(f'Missing stage numbers: {sorted(missing)}')
            if duplicates:
                raise ValueError(f'Duplicate stage numbers: {sorted(set(duplicates))}')
        
        # Vérifier l'ordre des étapes
        if stage_numbers != [1, 2, 3, 4, 5]:
            raise ValueError(f'Stages must be in order 1-5, got: {stage_numbers}')
        
        return v
    
    @validator('stages')
    def validate_total_slides(cls, v):
        """Validation du nombre total de slides"""
        total_slides = sum(
            submodule.slide_count
            for stage in v
            for module in stage.modules
            for submodule in module.submodules
        )
        
        # Contraintes métier: entre 15 et 50 slides total
        if total_slides < 15:
            raise ValueError(f'Training plan too short: {total_slides} slides (minimum 15)')
        if total_slides > 50:
            raise ValueError(f'Training plan too long: {total_slides} slides (maximum 50)')
        
        return v


class PlanGenerationResponse(BaseModel):
    """Schema pour réponse de génération de plan"""
    success: bool = Field(..., description="Succès de la génération")
    training_plan: TrainingPlanSchema = Field(..., description="Plan de formation généré")
    generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées de génération")
    message: str = Field(default="Plan generated successfully", description="Message de statut")


class ValidationErrorDetail(BaseModel):
    """Détail d'une erreur de validation"""
    field: str = Field(..., description="Champ en erreur")
    message: str = Field(..., description="Message d'erreur")
    invalid_value: Any = Field(None, description="Valeur invalide")


class ErrorResponse(BaseModel):
    """Schema pour réponse d'erreur"""
    success: bool = Field(default=False, description="Échec de l'opération")
    error_type: str = Field(..., description="Type d'erreur")
    error_message: str = Field(..., description="Message d'erreur")
    validation_errors: List[ValidationErrorDetail] = Field(default_factory=list, description="Erreurs de validation")
    details: Dict[str, Any] = Field(default_factory=dict, description="Détails supplémentaires")


class PlanValidationResult(BaseModel):
    """Résultat de validation d'un plan"""
    is_valid: bool = Field(..., description="Plan valide ou non")
    validation_errors: List[ValidationErrorDetail] = Field(default_factory=list, description="Liste des erreurs")
    warnings: List[str] = Field(default_factory=list, description="Avertissements non bloquants")
    statistics: Dict[str, int] = Field(default_factory=dict, description="Statistiques du plan")
    
    @property
    def error_count(self) -> int:
        """Nombre d'erreurs de validation"""
        return len(self.validation_errors)
    
    @property 
    def warning_count(self) -> int:
        """Nombre d'avertissements"""
        return len(self.warnings)