import argparse
import asyncio
import logging
import pathlib
import sys
from datetime import datetime, timezone

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.infrastructure.notifications.rabbitmq_reminder_producer import (  # noqa: E402
    ReminderMessage,
    RabbitMQReminderProducer,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Force-trigger reminder notification via RabbitMQ.",
    )
    parser.add_argument("--user-id", type=int, required=True, help="Target app user ID")
    parser.add_argument("--card-id", type=int, default=0, help="Card ID for test payload")
    parser.add_argument("--word", default="test-word", help="Word for reminder message")
    parser.add_argument(
        "--translation",
        default="тестовий переклад",
        help="Translation for reminder message",
    )
    return parser.parse_args()


async def run() -> None:
    args = parse_args()
    producer = RabbitMQReminderProducer()
    payload = ReminderMessage(
        user_id=args.user_id,
        card_id=args.card_id,
        word=args.word,
        translation=args.translation,
        remind_at=datetime.now(timezone.utc),
    )

    logging.info(
        "Publishing force-trigger reminder. user_id=%s card_id=%s queue=%s",
        args.user_id,
        args.card_id,
        producer.queue_name,
    )
    await producer.publish(payload)
    logging.info(
        "Force-trigger reminder published. user_id=%s card_id=%s queue=%s",
        args.user_id,
        args.card_id,
        producer.queue_name,
    )
    print(
        f"Queued reminder to '{producer.queue_name}' for user_id={args.user_id}, card_id={args.card_id}",
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    asyncio.run(run())
