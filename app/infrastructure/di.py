from app.infrastructure.repositories.card_repositories import CardRepository
from app.infrastructure.database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.infrastructure.database.uow import UnitOfWork
from app.infrastructure.security.jwt_verifier import JWTTokenVerifier


async def card_protocol(session:AsyncSession = Depends(get_session)) -> CardRepository:
    return CardRepository(session)


async def uow_dependencies():
    session: AsyncSession = await get_session()
    uow =UnitOfWork(session)
    
    try:
        return uow
    finally:
        await session.close()


def token_verifier():
    return JWTTokenVerifier()