from app.domain.entity.card import Card
from app.application.protocols.uow import IUnitOfWork
from app.application.dto.card_dto import CardDTO
from datetime import datetime


class GetDueForReviewUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, user_id: int, limit: int, now: datetime) -> list[Card]:
        async with self.uow:
            cards = await self.uow.cards.get_due_for_review(user_id, limit, now)
        
        return [
            CardDTO(
                id=cards.id,
                user_id=cards.user_id,
                word=cards.word,
                translation=cards.translation,
                context=cards.context,
                next_review_at=cards.next_review_at,
                previous_interval=cards.previous_interval.days,
                ease_factor=cards.ease_factor,
                repetitions=cards.repetitions,
                created_at=cards.created_at

            ) for cards in cards
        ]