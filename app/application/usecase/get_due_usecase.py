from datetime import datetime

from app.application.dto.card_dto import CardDTO
from app.application.protocols.uow import IUnitOfWork


class GetDueForReviewUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, user_id: int, limit: int, now: datetime) -> list[CardDTO]:
        async with self.uow:
            cards = await self.uow.cards.get_due_for_review(user_id, limit, now)
            return [CardDTO.from_entity(card) for card in cards]