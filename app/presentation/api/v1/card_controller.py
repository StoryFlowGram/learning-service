from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.application.protocols.uow import IUnitOfWork
from app.application.usecase.add_card_usecase import AddCardUseCase
from app.application.usecase.delete_card import DeleteCardForUserUseCase
from app.application.usecase.get_all_cards_usecase import GetAllCardsForUserUseCase
from app.application.usecase.get_card_by_id_usecase import GetCardByIdUseCase
from app.application.usecase.get_due_count_usecase import GetDueCountUseCase
from app.application.usecase.get_due_usecase import GetDueForReviewUseCase
from app.application.usecase.update_card_usecase import ReviewCardUseCase
from app.infrastructure.notifications.rabbitmq_reminder_producer import (
    ReminderMessage,
    RabbitMQReminderProducer,
)
from app.presentation.api.depends import ensure_gateway_request, get_current_user, uow_dependencies
from app.presentation.mappers.card_schema_mapper import schema_to_domain
from app.presentation.schemas.card_schema import (
    CardAddRequestSchema,
    CardResponseSchema,
    CardReviewRequestSchema,
    DueCountResponseSchema,
    ForceNotificationRequestSchema,
    ForceNotificationResponseSchema,
)

card_router = APIRouter(tags=["cards"], dependencies=[Depends(ensure_gateway_request)])
reminder_producer = RabbitMQReminderProducer()


@card_router.get(
    "/get",
    response_model=list[CardResponseSchema],
    description="Отримання карток, строк повторення яких настав",
)
async def get_due_for_review(
    limit: int = 10,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    now = datetime.now(timezone.utc)
    usecase = GetDueForReviewUseCase(uow)
    try:
        return await usecase(user_id, limit, now)
    except Exception:
        logger.exception("Failed to get due cards for user %s", user_id)
        raise HTTPException(status_code=400, detail="Не вдалося отримати картки для повторення")


@card_router.get(
    "/due/count",
    response_model=DueCountResponseSchema,
    description="Отримання кількості слів, які вже час повторити",
)
async def get_due_count(
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    now = datetime.now(timezone.utc)
    usecase = GetDueCountUseCase(uow)
    try:
        due_count = await usecase(user_id, now)
        return {"due_count": due_count, "as_of": now}
    except Exception:
        logger.exception("Failed to get due cards count for user %s", user_id)
        raise HTTPException(status_code=400, detail="Не вдалося отримати кількість карток для повторення")


@card_router.post("/", response_model=CardResponseSchema, status_code=201, description="Додавання картки")
async def add_card(
    schema: CardAddRequestSchema,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    usecase = AddCardUseCase(uow)
    try:
        card_domain = schema_to_domain(schema, user_id)
        result = await usecase(card_domain)
    except Exception:
        logger.exception("Failed to add card for user %s", user_id)
        raise HTTPException(status_code=400, detail="Не вдалося додати картку")

    try:
        await reminder_producer.publish(
            ReminderMessage(
                user_id=result.user_id,
                card_id=result.id,
                word=result.word,
                translation=result.translation,
                remind_at=result.next_review_at,
            )
        )
        logger.info(
            "Reminder enqueued after card creation. user_id=%s card_id=%s remind_at=%s queue=%s",
            result.user_id,
            result.id,
            result.next_review_at,
            reminder_producer.queue_name,
        )
    except Exception:
        logger.exception(
            "Card created but reminder enqueue failed. user_id=%s card_id=%s",
            result.user_id,
            result.id,
        )

    return result


@card_router.get("/{card_id}", response_model=CardResponseSchema, description="Отримання картки за ID")
async def get_card(
    card_id: int,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    usecase = GetCardByIdUseCase(uow)
    try:
        return await usecase(card_id, user_id)
    except Exception:
        logger.exception("Failed to get card %s for user %s", card_id, user_id)
        raise HTTPException(status_code=400, detail="Не вдалося отримати картку")


@card_router.get(
    "/",
    response_model=list[CardResponseSchema],
    description="Отримання всіх карток користувача",
)
async def get_all_card_by_user(
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    usecase = GetAllCardsForUserUseCase(uow)
    try:
        return await usecase(user_id)
    except Exception:
        logger.exception("Failed to get all cards for user %s", user_id)
        raise HTTPException(status_code=400, detail="Не вдалося отримати картки користувача")


@card_router.patch(
    "/review",
    response_model=CardResponseSchema,
    description="Відправка результату повторення (SRS)",
)
async def review_card(
    schema: CardReviewRequestSchema,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    usecase = ReviewCardUseCase(uow)
    try:
        result = await usecase(
            user_id=user_id,
            card_id=schema.card_id,
            quality_value=schema.quality,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Некоректні дані повторення")
    except Exception:
        logger.exception("Failed to review card %s for user %s", schema.card_id, user_id)
        raise HTTPException(status_code=400, detail="Не вдалося оновити повторення картки")

    try:
        await reminder_producer.publish(
            ReminderMessage(
                user_id=result.user_id,
                card_id=result.id,
                word=result.word,
                translation=result.translation,
                remind_at=result.next_review_at,
            )
        )
        logger.info(
            "Reminder enqueued after review. user_id=%s card_id=%s remind_at=%s queue=%s",
            result.user_id,
            result.id,
            result.next_review_at,
            reminder_producer.queue_name,
        )
    except Exception:
        logger.exception(
            "Failed to enqueue reminder for user %s and card %s",
            user_id,
            schema.card_id,
        )
        raise HTTPException(
            status_code=503,
            detail="Card was reviewed, but reminder enqueue failed. Retry reminder trigger later.",
        )

    return result


@card_router.post(
    "/notifications/force-trigger",
    response_model=ForceNotificationResponseSchema,
    description="Тестовий примусовий тригер надсилання сповіщення через RabbitMQ",
)
async def force_trigger_notification(
    schema: ForceNotificationRequestSchema,
    user_id: int = Depends(get_current_user),
):
    remind_at = datetime.now(timezone.utc)
    payload = ReminderMessage(
        user_id=user_id,
        card_id=schema.card_id,
        word=schema.word,
        translation=schema.translation,
        remind_at=remind_at,
    )

    logger.info(
        "Force-trigger requested. user_id=%s card_id=%s queue=%s",
        user_id,
        schema.card_id,
        reminder_producer.queue_name,
    )

    try:
        await reminder_producer.publish(payload)
    except Exception:
        logger.exception(
            "Force-trigger publish failed. user_id=%s card_id=%s queue=%s",
            user_id,
            schema.card_id,
            reminder_producer.queue_name,
        )
        raise HTTPException(status_code=503, detail="Не вдалося надіслати тестове повідомлення у чергу")

    logger.info(
        "Force-trigger published. user_id=%s card_id=%s queue=%s",
        user_id,
        schema.card_id,
        reminder_producer.queue_name,
    )

    return {
        "status": "queued",
        "queue": reminder_producer.queue_name,
        "user_id": user_id,
        "card_id": schema.card_id,
        "remind_at": remind_at,
    }


@card_router.delete("/{card_id}", status_code=204, description="Видалення картки за ID")
async def delete_card(
    card_id: int,
    user_id: int = Depends(get_current_user),
    uow: IUnitOfWork = Depends(uow_dependencies),
):
    usecase = DeleteCardForUserUseCase(uow)
    try:
        return await usecase(card_id, user_id)
    except Exception:
        logger.exception("Failed to delete card %s for user %s", card_id, user_id)
        raise HTTPException(status_code=400, detail="Не вдалося видалити картку")
