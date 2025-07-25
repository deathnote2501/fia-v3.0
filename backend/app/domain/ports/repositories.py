from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities import (
    Trainer, Training, TrainingSession, LearnerSession,
    Slide, ChatMessage, ApiLog
)


class TrainerRepositoryPort(ABC):
    
    @abstractmethod
    async def create(self, trainer: Trainer) -> Trainer:
        pass
    
    @abstractmethod
    async def get_by_id(self, trainer_id: UUID) -> Optional[Trainer]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Trainer]:
        pass
    
    @abstractmethod
    async def update(self, trainer: Trainer) -> Trainer:
        pass
    
    @abstractmethod
    async def delete(self, trainer_id: UUID) -> bool:
        pass


class TrainingRepositoryPort(ABC):
    
    @abstractmethod
    async def create(self, training: Training) -> Training:
        pass
    
    @abstractmethod
    async def get_by_id(self, training_id: UUID) -> Optional[Training]:
        pass
    
    @abstractmethod
    async def get_by_trainer_id(self, trainer_id: UUID) -> List[Training]:
        pass
    
    @abstractmethod
    async def update(self, training: Training) -> Training:
        pass
    
    @abstractmethod
    async def delete(self, training_id: UUID) -> bool:
        pass


class TrainingSessionRepositoryPort(ABC):
    
    @abstractmethod
    async def create(self, training_session: TrainingSession) -> TrainingSession:
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[TrainingSession]:
        pass
    
    @abstractmethod
    async def get_by_token(self, session_token: str) -> Optional[TrainingSession]:
        pass
    
    @abstractmethod
    async def get_by_training_id(self, training_id: UUID) -> List[TrainingSession]:
        pass
    
    @abstractmethod
    async def update(self, training_session: TrainingSession) -> TrainingSession:
        pass
    
    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        pass


class LearnerSessionRepositoryPort(ABC):
    
    @abstractmethod
    async def create(self, learner_session: LearnerSession) -> LearnerSession:
        pass
    
    @abstractmethod
    async def get_by_id(self, learner_session_id: UUID) -> Optional[LearnerSession]:
        pass
    
    @abstractmethod
    async def get_by_training_session_and_email(
        self, training_session_id: UUID, email: str
    ) -> Optional[LearnerSession]:
        pass
    
    @abstractmethod
    async def get_by_training_session_id(self, training_session_id: UUID) -> List[LearnerSession]:
        pass
    
    @abstractmethod
    async def update(self, learner_session: LearnerSession) -> LearnerSession:
        pass
    
    @abstractmethod
    async def delete(self, learner_session_id: UUID) -> bool:
        pass


class SlideRepositoryPort(ABC):
    
    @abstractmethod
    async def create(self, slide: Slide) -> Slide:
        pass
    
    @abstractmethod
    async def get_by_id(self, slide_id: UUID) -> Optional[Slide]:
        pass
    
    @abstractmethod
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[Slide]:
        pass
    
    @abstractmethod
    async def get_by_learner_session_and_slide_number(
        self, learner_session_id: UUID, slide_number: int
    ) -> Optional[Slide]:
        pass
    
    @abstractmethod
    async def update(self, slide: Slide) -> Slide:
        pass
    
    @abstractmethod
    async def delete(self, slide_id: UUID) -> bool:
        pass


class ChatMessageRepositoryPort(ABC):
    
    @abstractmethod
    async def create(self, chat_message: ChatMessage) -> ChatMessage:
        pass
    
    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Optional[ChatMessage]:
        pass
    
    @abstractmethod
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[ChatMessage]:
        pass
    
    @abstractmethod
    async def get_by_learner_session_and_slide(
        self, learner_session_id: UUID, slide_number: Optional[int] = None
    ) -> List[ChatMessage]:
        pass
    
    @abstractmethod
    async def delete(self, message_id: UUID) -> bool:
        pass


class ApiLogRepositoryPort(ABC):
    
    @abstractmethod
    async def create(self, api_log: ApiLog) -> ApiLog:
        pass
    
    @abstractmethod
    async def get_by_id(self, log_id: UUID) -> Optional[ApiLog]:
        pass
    
    @abstractmethod
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[ApiLog]:
        pass
    
    @abstractmethod
    async def get_by_operation_type(self, operation_type: str) -> List[ApiLog]:
        pass
    
    @abstractmethod
    async def delete(self, log_id: UUID) -> bool:
        pass