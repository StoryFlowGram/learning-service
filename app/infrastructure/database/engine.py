from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from app.infrastructure.config.settings import Settings
from app.infrastructure.database.base import Base


settings = Settings(env_file=".env")

engine: AsyncEngine  = create_async_engine(
    settings.database.get_database_url(DB_API="asyncpg"),
    echo=True,
)


async def flush_database(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)