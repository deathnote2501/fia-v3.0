from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities import ChatMessage
from app.domain.ports.repositories import ChatMessageRepositoryPort


class ChatMessageRepository(ChatMessageRepositoryPort):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, chat_message: ChatMessage) -> ChatMessage:
        self.session.add(chat_message)
        await self.session.commit()
        await self.session.refresh(chat_message)
        return chat_message
    
    async def get_by_id(self, message_id: UUID) -> Optional[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage).where(ChatMessage.id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_learner_session_id(self, learner_session_id: UUID) -> List[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage).where(ChatMessage.learner_session_id == learner_session_id)
            .order_by(ChatMessage.created_at)
        )
        return list(result.scalars().all())
    
    async def get_by_learner_session_and_slide(
        self, learner_session_id: UUID, slide_number: Optional[int] = None
    ) -> List[ChatMessage]:
        query = select(ChatMessage).where(
            ChatMessage.learner_session_id == learner_session_id
        )
        
        if slide_number is not None:
            query = query.where(ChatMessage.slide_number == slide_number)
        
        query = query.order_by(ChatMessage.created_at)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def delete(self, message_id: UUID) -> bool:
        result = await self.session.execute(
            select(ChatMessage).where(ChatMessage.id == message_id)
        )
        chat_message = result.scalar_one_or_none()
        if chat_message:
            await self.session.delete(chat_message)
            await self.session.commit()
            return True
        return False