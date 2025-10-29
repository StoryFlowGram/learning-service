from app.domain.entity.card import Card
from app.application.dto.card_dto import CardDTO
from app.application.protocols.uow import IUnitOfWork
from app.domain.exception.card_exceptions import CardNotFoundException




class GetCardByIdUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, card_id: int, user_id: int):
        async with self.uow:
            result = await self.uow.cards.get_by_id(card_id, user_id)
            if not result:
                raise CardNotFoundException(f"Карта с id {card_id} не найдена у пользователя {user_id}")
            
        return CardDTO(
            id=result.id,
            user_id=result.user_id,
            question=result.question,
            answer=result.answer,
            created_at=str(result.created_at),
            updated_at=str(result.updated_at)
        )