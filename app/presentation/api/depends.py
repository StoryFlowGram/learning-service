from fastapi import Depends, Security, HTTPException 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError

from app.application.protocols.jwt_verifier_protocol import AbstractJwtVerifier
from app.infrastructure.di import token_verifier

bearer_scheme = HTTPBearer()


async def card_protocol():
    raise NotImplementedError("Должен быть переопределён в infa слое")


async def uow_dependencies():
    raise NotImplementedError("Должен быть переопределён в infa слое")


async def get_current_user(
    token: HTTPAuthorizationCredentials = Security(bearer_scheme),
    token_verifier: AbstractJwtVerifier = Depends(token_verifier)
):
    jwt_token = token.credentials
    try:
        user_id = token_verifier.get_user_id(jwt_token)
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Токен истёк",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Токен не валидный",
            headers={"WWW-Authenticate": "Bearer"}
        )