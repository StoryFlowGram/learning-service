from app.application.protocols.uow import IUnitOfWork
from app.domain.entity.card import Card

class GetAllCardsForUserUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, user_id: int) -> list[Card]:
        async with self.uow:
            cards = await self.uow.cards.get_all_by_user(user_id)
            return cards