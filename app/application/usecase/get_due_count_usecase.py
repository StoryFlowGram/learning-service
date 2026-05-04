from datetime import datetime

from app.application.protocols.uow import IUnitOfWork


class GetDueCountUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, user_id: int, now: datetime) -> int:
        async with self.uow:
            return await self.uow.cards.get_due_count(user_id, now)

