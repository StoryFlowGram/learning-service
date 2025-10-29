from app.application.protocols.uow import IUnitOfWork
from app.domain.entity.card import Card
from app.domain.exception.card_exceptions import CardNotFoundException


class DeleteCardForUserUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, card_id: int, user_id: int) -> None:
        async with self.uow:
            check_existence: Card = await self.uow.cards.get_by_id(card_id, user_id)
            if not check_existence:
                raise CardNotFoundException(card_id=card_id, user_id=user_id)
            await self.uow.cards.delete(card_id, user_id)