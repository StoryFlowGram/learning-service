from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from loguru import logger

from app.application.usecase.add_card_usecase import AddCardUseCase
from app.application.usecase.delete_card import DeleteCardForUserUseCase
from app.application.usecase.get_card_by_id_usecase import GetCardByIdUseCase
from app.application.usecase.get_all_cards_usecase import GetAllCardsForUserUseCase
from app.application.usecase.get_due_usecase import GetDueForReviewUseCase
from app.application.protocols.uow import IUnitOfWork 

from app.presentation.api.depends import uow_dependencies
from app.presentation.schemas.card_schema import CardAddRequestSchema, CardResponseSchema
from app.presentation.mappers.card_schema_mapper import schema_to_domain

from app.presentation.api.depends import get_current_user



card_router = APIRouter(
    prefix="/api/v1/learn/cards",
    tags=["cards"]

)


@card_router.post("/add", response_model=CardResponseSchema)
async def add_card(
    schema: CardAddRequestSchema,
    uow: IUnitOfWork = Depends(uow_dependencies),
    get_current_user_jwt = Depends(get_current_user),
):
    usecase = AddCardUseCase(uow)
    try:
        logger.info(f"Схема равна: {schema}")
        card_domain = schema_to_domain(schema)
        return await usecase(card_domain)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@card_router.get("/getCard/{card_id}/{user_id}", response_model=CardResponseSchema)
async def get_card(
    card_id: int,
    user_id: int,
    uow: IUnitOfWork = Depends(uow_dependencies),
    get_current_user_jwt = Depends(get_current_user),
):

    usecase = GetCardByIdUseCase(uow)
    try:
        return await usecase(card_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@card_router.get("/getAllCard/{user_id}", response_model=list[CardResponseSchema])
async def get_all_card_by_user(
    user_id: int, 
    uow: IUnitOfWork = Depends(uow_dependencies),
    get_current_user_jwt = Depends(get_current_user),
):
    usecase  = GetAllCardsForUserUseCase(uow)
    try:
        return await usecase(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@card_router.get("/getDue/{user_id}/{limit}/{now}", response_model=list[CardResponseSchema])
async def get_due_for_review(
    user_id: int,
    limit: int,
    now: datetime,
    uow: IUnitOfWork = Depends(uow_dependencies),
    get_current_user_jwt = Depends(get_current_user),
):
    usecase = GetDueForReviewUseCase(uow)
    try: 
        return await usecase(user_id, limit, now)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@card_router.delete("/delete/{card_id}/{user_id}")
async def delete_card(
    card_id: int,
    user_id: int,
    uow: IUnitOfWork = Depends(uow_dependencies),
    get_current_user_jwt = Depends(get_current_user),):
    usecase = DeleteCardForUserUseCase(uow)
    try:
        return await usecase(card_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
