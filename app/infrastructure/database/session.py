from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.infrastructure.database.engine import engine

session_factory = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() :
    async with session_factory() as session:
        return session
    