from app.application.protocols.uow import IUnitOfWork
from app.domain.entity.card import Card
from app.application.dto.card_dto import CardDTO
from app.domain.exception.card_exceptions import CardNotFoundException


# Оставить про запас Любой код с Update

class UpdateCardUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, card: Card):
        async with self.uow:
            check_existing = await self.uow.cards.get_by_id(card.id, card.user_id)
            if not check_existing:
                raise CardNotFoundException(card_id=card.id, user_id=card.user_id)

            update_card = await self.uow.cards.update(card)
            if not update_card:
                raise Exception(f"Не удалось обновить карту с id {card.id}")
            
        return CardDTO(
            id=update_card.id,
            user_id=update_card.user_id,
            word=update_card.word,
            translation=update_card.translation,
            context=update_card.context,
            next_review_at=update_card.next_review_at,
            previous_interval=update_card.previous_interval.days,
            ease_factor=update_card.ease_factor,
            repetitions=update_card.repetitions,
            created_at=update_card.created_at
        )
