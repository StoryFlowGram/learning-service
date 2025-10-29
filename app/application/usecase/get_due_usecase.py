from app.domain.entity.card import Card
from app.application.protocols.uow import IUnitOfWork


class GetDueForReviewUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, user_id: int, limit: int, now) -> list[Card]:
        async with self.uow:
            cards = await self.uow.cards.get_due_for_review(user_id, limit, now)
            return cards