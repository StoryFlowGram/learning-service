from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.card_repositories import CardRepository




class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.cards = CardRepository(session)


    async def __aenter__(self):
        return self
    

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()


    async def commit(self):
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
        
    async def rollback(self):
        await self.session.rollback()