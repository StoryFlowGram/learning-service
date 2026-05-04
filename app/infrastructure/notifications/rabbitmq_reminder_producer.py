import json
import logging
from datetime import datetime, timezone

import aio_pika
from aio_pika import DeliveryMode, Message
from pydantic import BaseModel

from app.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


class ReminderMessage(BaseModel):
    user_id: int
    card_id: int
    word: str
    translation: str
    remind_at: datetime


class RabbitMQReminderProducer:
    def __init__(self):
        settings = Settings()
        self.url = settings.rabbitmq.url
        self.queue_name = settings.rabbitmq.reminder_queue
        self.delay_queue_name = f"{self.queue_name}.delay"
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def _ensure_connected(self) -> aio_pika.abc.AbstractChannel:
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(self.url)
            self._channel = None

        if self._channel is None or self._channel.is_closed:
            self._channel = await self._connection.channel()
            await self._channel.declare_queue(self.queue_name, durable=True)
            await self._channel.declare_queue(
                self.delay_queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": "",
                    "x-dead-letter-routing-key": self.queue_name,
                },
            )

        return self._channel

    async def publish(self, payload: ReminderMessage) -> None:
        remind_at = (
            payload.remind_at.astimezone(timezone.utc)
            if payload.remind_at.tzinfo
            else payload.remind_at.replace(tzinfo=timezone.utc)
        )
        delay_seconds = (remind_at - datetime.now(timezone.utc)).total_seconds()
        delay_ms = max(0, int(delay_seconds * 1000))
        routing_key = self.delay_queue_name if delay_ms > 0 else self.queue_name

        logger.info(
            "Publishing reminder to RabbitMQ. user_id=%s card_id=%s queue=%s delay_ms=%s",
            payload.user_id,
            payload.card_id,
            routing_key,
            delay_ms,
        )

        channel = await self._ensure_connected()
        body = json.dumps(payload.model_dump(mode="json"), ensure_ascii=False).encode("utf-8")
        message = Message(
            body=body,
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
            expiration=delay_ms if delay_ms > 0 else None,
        )
        await channel.default_exchange.publish(message, routing_key=routing_key)

        logger.info(
            "Reminder published successfully. user_id=%s card_id=%s queue=%s",
            payload.user_id,
            payload.card_id,
            routing_key,
        )

    async def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
