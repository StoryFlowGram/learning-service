from app.application.protocols.uow import IUnitOfWork
from app.domain.entity.card import Card
from app.application.dto.card_dto import CardDTO


class GetAllCardsForUserUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, user_id: int) -> list[Card]:
        async with self.uow:
            cards = await self.uow.cards.get_all_by_user(user_id)
            
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
