import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
os.environ.setdefault("RABBITMQ_REMINDER_QUEUE", "notifications.reminder")
os.environ.setdefault("LEARN_DB_USER", "test")
os.environ.setdefault("LEARN_DB_PASSWORD", "test")
os.environ.setdefault("LEARN_DB_NAME", "test")

from app.application.dto.card_dto import CardDTO
from app.infrastructure.notifications.rabbitmq_reminder_producer import (
    RabbitMQReminderProducer,
    ReminderMessage,
)
from app.presentation.api.v1 import card_controller
from app.presentation.schemas.card_schema import CardAddRequestSchema, CardReviewRequestSchema


class _FakeExchange:
    def __init__(self):
        self.published: list[tuple] = []

    async def publish(self, message, routing_key: str):
        self.published.append((message, routing_key))


class _FakeChannel:
    def __init__(self):
        self.default_exchange = _FakeExchange()
        self.declared_queues: list[tuple] = []

    async def declare_queue(self, name: str, durable: bool, arguments=None):
        self.declared_queues.append((name, durable, arguments))


class _FakeConnection:
    def __init__(self, channel: _FakeChannel):
        self._channel = channel

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def channel(self):
        return self._channel


class RabbitMQReminderProducerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_delayed_message_uses_integer_expiration(self):
        producer = RabbitMQReminderProducer()
        channel = _FakeChannel()
        connection = _FakeConnection(channel)

        async def _fake_connect(url: str):
            self.assertEqual(url, producer.url)
            return connection

        payload = ReminderMessage(
            user_id=1,
            card_id=2,
            word="word",
            translation="translation",
            remind_at=datetime.now(timezone.utc) + timedelta(seconds=2),
        )

        with patch(
            "app.infrastructure.notifications.rabbitmq_reminder_producer.aio_pika.connect_robust",
            new=_fake_connect,
        ):
            await producer.publish(payload)

        self.assertEqual(len(channel.default_exchange.published), 1)
        message, routing_key = channel.default_exchange.published[0]
        self.assertEqual(routing_key, producer.delay_queue_name)
        self.assertIsInstance(message.expiration, int)
        self.assertGreater(message.expiration, 0)


class ReviewCardNotificationsTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_review_card_returns_503_when_enqueue_fails(self):
        result = CardDTO(
            id=3,
            user_id=11,
            word="test",
            translation="тест",
            context=None,
            next_review_at=datetime.now(timezone.utc) + timedelta(days=1),
            previous_interval=1,
            ease_factor=2.5,
            repetitions=1,
            created_at=None,
        )
        received_args: list[tuple[int, int, int]] = []

        class _FakeReviewUseCase:
            def __init__(self, _uow):
                pass

            async def __call__(self, user_id: int, card_id: int, quality_value: int):
                received_args.append((user_id, card_id, quality_value))
                return result

        class _FailingProducer:
            queue_name = "notifications.reminder"

            async def publish(self, payload):
                raise RuntimeError("RabbitMQ unavailable")

        schema = CardReviewRequestSchema(card_id=3, quality=4)

        with patch.object(card_controller, "ReviewCardUseCase", _FakeReviewUseCase), patch.object(
            card_controller,
            "reminder_producer",
            _FailingProducer(),
        ), patch.object(card_controller, "logger", MagicMock()):
            with self.assertRaises(HTTPException) as ctx:
                await card_controller.review_card(schema=schema, user_id=11, uow=object())

        self.assertEqual(received_args, [(11, 3, 4)])
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertIn("reminder enqueue failed", ctx.exception.detail)


class AddCardNotificationsTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_add_card_enqueues_initial_reminder(self):
        created_card = CardDTO(
            id=77,
            user_id=29,
            word="new",
            translation="новий",
            context="ctx",
            next_review_at=datetime.now(timezone.utc) + timedelta(hours=1),
            previous_interval=0,
            ease_factor=2.5,
            repetitions=0,
            created_at=None,
        )
        published_payloads = []

        class _FakeAddCardUseCase:
            def __init__(self, _uow):
                pass

            async def __call__(self, _card_domain):
                return created_card

        class _Producer:
            queue_name = "notifications.reminder"

            async def publish(self, payload):
                published_payloads.append(payload)

        schema = CardAddRequestSchema(word="new", translation="новий", context="ctx")

        with patch.object(card_controller, "AddCardUseCase", _FakeAddCardUseCase), patch.object(
            card_controller,
            "reminder_producer",
            _Producer(),
        ):
            result = await card_controller.add_card(schema=schema, user_id=29, uow=object())

        self.assertEqual(result.id, created_card.id)
        self.assertEqual(len(published_payloads), 1)
        payload = published_payloads[0]
        self.assertEqual(payload.user_id, created_card.user_id)
        self.assertEqual(payload.card_id, created_card.id)
        self.assertEqual(payload.word, created_card.word)
        self.assertEqual(payload.translation, created_card.translation)
        self.assertEqual(payload.remind_at, created_card.next_review_at)

    async def test_add_card_returns_card_when_enqueue_fails(self):
        created_card = CardDTO(
            id=78,
            user_id=30,
            word="newer",
            translation="новіший",
            context=None,
            next_review_at=datetime.now(timezone.utc) + timedelta(hours=2),
            previous_interval=0,
            ease_factor=2.5,
            repetitions=0,
            created_at=None,
        )

        class _FakeAddCardUseCase:
            def __init__(self, _uow):
                pass

            async def __call__(self, _card_domain):
                return created_card

        class _FailingProducer:
            queue_name = "notifications.reminder"

            async def publish(self, payload):
                raise RuntimeError("queue is down")

        schema = CardAddRequestSchema(word="newer", translation="новіший", context=None)

        with patch.object(card_controller, "AddCardUseCase", _FakeAddCardUseCase), patch.object(
            card_controller,
            "reminder_producer",
            _FailingProducer(),
        ), patch.object(card_controller, "logger", MagicMock()):
            result = await card_controller.add_card(schema=schema, user_id=30, uow=object())

        self.assertEqual(result.id, created_card.id)
        self.assertEqual(result.user_id, created_card.user_id)
