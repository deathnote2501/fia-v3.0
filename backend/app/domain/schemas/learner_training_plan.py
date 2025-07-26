"""
FIA v3.0 - Learner Training Plan Schemas
Pydantic schemas for learner training plan data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class TrainingSlideCreate(BaseModel):
    """Schema for creating a training slide"""
    title: str = Field(..., min_length=1, max_length=200)
    order_in_submodule: int = Field(..., ge=1)


class TrainingSlideResponse(BaseModel):
    """Schema for training slide response"""
    id: UUID
    title: str
    content: Optional[str]
    order_in_submodule: int
    generated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingSubmoduleCreate(BaseModel):
    """Schema for creating a training submodule"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    order_in_module: int = Field(..., ge=1)
    slides: List[TrainingSlideCreate] = Field(..., min_items=1)


class TrainingSubmoduleResponse(BaseModel):
    """Schema for training submodule response"""
    id: UUID
    title: str
    description: Optional[str]
    order_in_module: int
    created_at: datetime
    slides: List[TrainingSlideResponse] = []

    class Config:
        from_attributes = True


class TrainingModuleCreate(BaseModel):
    """Schema for creating a training module"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    stage_number: int = Field(..., ge=1, le=5)
    order_in_stage: int = Field(..., ge=1)
    submodules: List[TrainingSubmoduleCreate] = Field(..., min_items=1)


class TrainingModuleResponse(BaseModel):
    """Schema for training module response"""
    id: UUID
    title: str
    description: Optional[str]
    stage_number: int
    order_in_stage: int
    created_at: datetime
    submodules: List[TrainingSubmoduleResponse] = []

    class Config:
        from_attributes = True


class LearnerTrainingPlanCreate(BaseModel):
    """Schema for creating a learner training plan"""
    learner_session_id: UUID
    modules: List[TrainingModuleCreate] = Field(..., min_items=1)


class LearnerTrainingPlanResponse(BaseModel):
    """Schema for learner training plan response"""
    id: UUID
    learner_session_id: UUID
    current_slide_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    modules: List[TrainingModuleResponse] = []

    class Config:
        from_attributes = True


class CurrentSlideUpdate(BaseModel):
    """Schema for updating current slide position"""
    current_slide_id: UUID


# Gemini Structured Output Schemas
class GeminiSlideStructure(BaseModel):
    """Schema for slide structure from Gemini"""
    title: str = Field(..., min_length=1, max_length=200)


class GeminiSubmoduleStructure(BaseModel):
    """Schema for submodule structure from Gemini"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    slides: List[GeminiSlideStructure] = Field(..., min_items=1)


class GeminiModuleStructure(BaseModel):
    """Schema for module structure from Gemini"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    submodules: List[GeminiSubmoduleStructure] = Field(..., min_items=1)


class GeminiStageStructure(BaseModel):
    """Schema for stage structure from Gemini"""
    stage_number: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    modules: List[GeminiModuleStructure] = Field(..., min_items=1)


class GeminiTrainingPlanStructure(BaseModel):
    """Schema for complete training plan structure from Gemini"""
    stages: List[GeminiStageStructure] = Field(..., min_items=5, max_items=5)