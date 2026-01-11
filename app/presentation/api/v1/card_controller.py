from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from loguru import logger

from app.application.usecase.add_card_usecase import AddCardUseCase
from app.application.usecase.delete_card import DeleteCardForUserUseCase
from app.application.usecase.get_card_by_id_usecase import GetCardByIdUseCase
from app.application.usecase.get_all_cards_usecase import GetAllCardsForUserUseCase
from app.application.usecase.get_due_usecase import GetDueForReviewUseCase
from app.application.usecase.update_card_usecase import ReviewCardUseCase
from app.application.protocols.uow import IUnitOfWork 

from app.presentation.api.depends import uow_dependencies, get_current_user
from app.presentation.schemas.card_schema import CardAddRequestSchema, CardResponseSchema, CardReviewRequestSchema
from app.presentation.mappers.card_schema_mapper import schema_to_domain



card_router = APIRouter(tags=["cards"])


@card_router.get("/get", response_model=list[CardResponseSchema], description="Получение карточек, срок повторения которых наступил")
async def get_due_for_review(
    limit: int = 10,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    now = datetime.now(timezone.utc)
    usecase = GetDueForReviewUseCase(uow)
    try: 
        return await usecase(user_id, limit, now)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@card_router.post("/", response_model=CardResponseSchema, status_code=201, description="Добавление карточки")
async def add_card(
    schema: CardAddRequestSchema,
    user_id: int = Depends(get_current_user), 
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    usecase = AddCardUseCase(uow)
    try:
        logger.info(f"Добавлена карта для {user_id}: {schema}")
        card_domain = schema_to_domain(schema, user_id)
        
        return await usecase(card_domain)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@card_router.get("/{card_id}", response_model=CardResponseSchema, description="Получение карточки по ID")
async def get_card(
    card_id: int,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):

    usecase = GetCardByIdUseCase(uow)
    try:
        return await usecase(card_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@card_router.get("/", response_model=list[CardResponseSchema], description="Получение всех карточек пользователя")
async def get_all_card_by_user(
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    usecase  = GetAllCardsForUserUseCase(uow)
    try:
        return await usecase(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@card_router.patch("/review", response_model=CardResponseSchema, description="Отправка результата повторения (SRS)")
async def review_card(
    schema: CardReviewRequestSchema,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    usecase = ReviewCardUseCase(uow)
    try:
        return await usecase(
            user_id=user_id,
            card_id=schema.card_id,
            quality_value=schema.quality
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@card_router.delete("/{card_id}", status_code=204, description="Удаление карточки по ID")
async def delete_card(
    card_id: int,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies)):
    usecase = DeleteCardForUserUseCase(uow)
    try:
        return await usecase(card_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
