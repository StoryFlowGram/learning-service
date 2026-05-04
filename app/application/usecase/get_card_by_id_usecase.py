from app.application.dto.card_dto import CardDTO
from app.application.protocols.uow import IUnitOfWork
from app.domain.exception.card_exceptions import CardNotFoundException


class GetCardByIdUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, card_id: int, user_id: int) -> CardDTO:
        async with self.uow:
            result = await self.uow.cards.get_by_id(card_id, user_id)
            if not result:
                raise CardNotFoundException(card_id=card_id, user_id=user_id)
            return CardDTO.from_entity(result)