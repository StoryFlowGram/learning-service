from app.application.dto.card_dto import CardDTO
from app.application.protocols.uow import IUnitOfWork


class GetAllCardsForUserUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, user_id: int) -> list[CardDTO]:
        async with self.uow:
            cards = await self.uow.cards.get_all_by_user(user_id)
            return [CardDTO.from_entity(card) for card in cards]
