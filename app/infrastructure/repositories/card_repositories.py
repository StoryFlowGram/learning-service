from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.application.protocols.card_protocol import CardProtocol
from app.infrastructure.mapper.card_mapper import orm_to_domain, domain_to_orm
from app.infrastructure.models.card_model import CardModel
from app.domain.entity.card import Card


class CardRepository(CardProtocol):
    def __init__(self, session: AsyncSession):
        self.session = session



    async def add(self, card: Card):
        orm_card = domain_to_orm(card)
        self.session.add(orm_card)
        await self.session.flush([orm_card])
        return orm_to_domain(orm_card) 


    async def get_by_id(self, card_id, user_id):
        stmt = select(CardModel).where(
            CardModel.id == card_id,
            CardModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return orm_to_domain(orm)

    async def get_due_for_review(self, user_id, limit, now):
        stmt = select(CardModel).where(
            CardModel.user_id == user_id,
            CardModel.next_review_at <= now
        ).limit(limit)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        if orms is None:
            return []
        return [orm_to_domain(orm) for orm in orms]
    
    async def get_all_by_user(self, user_id):
        stmt =  select(CardModel).where(
            CardModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        if orms is None:
            return []
        return [orm_to_domain(orm) for orm in orms]
    

    async def delete(self, card_id, user_id):
        stmt = delete(CardModel).where(
            CardModel.id == card_id,
            CardModel.user_id == user_id
        )
        await self.session.execute(stmt)


    async def update(self, card):
        stmt = update(CardModel).where(
            CardModel.id == card.id,
            CardModel.user_id == card.user_id
        ).values(
            word=card.word,
            translation=card.translation,
            context=card.context,
            next_review_at=card.next_review_at,
            previous_interval=card.previous_interval.days,
            ease_factor=card.ease_factor,
            repetitions=card.repetitions
        ).returning(CardModel)
        result = await self.session.execute(stmt)
        orm = result.scalar_one()
        return orm_to_domain(orm)
    
    async def get_by_word_and_user(self, word, user_id):
        stmt = select(CardModel).where(
            CardModel.word == word,
            CardModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return orm_to_domain(orm)