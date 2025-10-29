from app.domain.entity.card import Card
from app.application.protocols.uow import IUnitOfWork
from app.application.dto.card_dto import CardDTO
from app.domain.exception.card_exceptions import CardAlreadyExistsException


class AddCardUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, card: Card):
        async with self.uow:
            check_existing = await self.uow.cards.get_by_id(card.id, card.user_id)
            if check_existing:
                raise CardAlreadyExistsException(f"Карта с  {card.id} уже существует в пользователя {card.user_id}")
            await self.uow.cards.add(card)

        
        return CardDTO(
            id=card.id,
            user_id=card.user_id,
            question=card.question,
            answer=card.answer,
            created_at=str(card.created_at),
            updated_at=str(card)
        )