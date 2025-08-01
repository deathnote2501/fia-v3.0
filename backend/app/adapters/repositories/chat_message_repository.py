from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.chat_message import ChatMessage
from app.domain.ports.repositories import ChatMessageRepositoryPort
from app.infrastructure.models.chat_message_model import ChatMessageModel


class ChatMessageRepository(ChatMessageRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, chat_message: ChatMessage) -> ChatMessage:
        message_model = self._entity_to_model(chat_message)
        self.session.add(message_model)
        await self.session.commit()
        await self.session.refresh(message_model)
        return self._model_to_entity(message_model)
    
    async def get_by_id(self, message_id: UUID) -> Optional[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessageModel).where(ChatMessageModel.id == message_id)
        )
        message_model = result.scalar_one_or_none()
        if message_model:
            return self._model_to_entity(message_model)
        return None
    
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessageModel).where(ChatMessageModel.learner_session_id == learner_session_id)
            .order_by(ChatMessageModel.created_at)
        )
        message_models = result.scalars().all()
        return [self._model_to_entity(model) for model in message_models]
    
    async def get_by_learner_session_and_slide(
        self, learner_session_id: UUID, slide_number: Optional[int] = None
    ) -> List[ChatMessage]:
        query = select(ChatMessageModel).where(
            ChatMessageModel.learner_session_id == learner_session_id
        )
        
        # Note: slide_number doesn't exist in DB, ignore filter for now
        # if slide_number is not None:
        #     query = query.where(ChatMessageModel.slide_number == slide_number)
        
        query = query.order_by(ChatMessageModel.created_at)
        
        result = await self.session.execute(query)
        message_models = result.scalars().all()
        return [self._model_to_entity(model) for model in message_models]
    
    async def delete(self, message_id: UUID) -> bool:
        result = await self.session.execute(
            select(ChatMessageModel).where(ChatMessageModel.id == message_id)
        )
        message_model = result.scalar_one_or_none()
        if message_model:
            await self.session.delete(message_model)
            await self.session.commit()
            return True
        return False

    def _entity_to_model(self, chat_message: ChatMessage) -> ChatMessageModel:
        """Convert domain entity to SQLAlchemy model"""
        return ChatMessageModel(
            id=chat_message.id,
            learner_session_id=chat_message.learner_session_id,
            message=chat_message.content,  # Map content to message
            message_type=chat_message.message_type,  # Fixed: use message_type from entity
            created_at=chat_message.created_at
        )
    
    def _model_to_entity(self, model: ChatMessageModel) -> ChatMessage:
        """Convert SQLAlchemy model to domain entity"""
        return ChatMessage(
            chat_message_id=model.id,
            learner_session_id=model.learner_session_id,
            message_type=model.message_type,  # Fixed: correct mapping
            content=model.message or model.response or "",  # Use message or response
            slide_number=None,  # Will be added later if needed
            created_at=model.created_at
        )