from app.application.dto.card_dto import CardDTO
from app.application.protocols.uow import IUnitOfWork
from app.domain.entity.card import Card
from app.domain.exception.card_exceptions import CardAlreadyExistsException


class AddCardUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, card: Card) -> CardDTO:
        async with self.uow:
            check_existing = await self.uow.cards.get_by_word_and_user(
                card.word,
                card.user_id,
            )
            if check_existing:
                raise CardAlreadyExistsException(card.user_id, card.word)
            card_with_id = await self.uow.cards.add(card)
            await self.uow.commit()
            return CardDTO.from_entity(card_with_id)