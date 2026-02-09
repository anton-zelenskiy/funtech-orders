import json
from datetime import datetime, timezone
from uuid import UUID

from aiokafka import AIOKafkaProducer

from app.core.config import settings

_producer: AIOKafkaProducer | None = None


async def get_kafka_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
        )
        await _producer.start()
    return _producer


async def close_kafka_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None


async def send_new_order_event(order_id: UUID, user_id: int) -> None:
    producer = await get_kafka_producer()
    payload = {
        "order_id": str(order_id),
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await producer.send_and_wait(
        settings.kafka_new_order_topic,
        value=json.dumps(payload).encode("utf-8"),
    )
