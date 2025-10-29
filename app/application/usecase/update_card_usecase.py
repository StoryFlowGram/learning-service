from app.application.protocols.uow import IUnitOfWork
from app.domain.entity.card import Card
from app.application.dto.card_dto import CardDTO
from app.domain.exception.card_exceptions import CardNotFoundException


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
            question=update_card.question,
            answer=update_card.answer,
            created_at=str(update_card.created_at),
            updated_at=str(update_card.updated_at)
        )
