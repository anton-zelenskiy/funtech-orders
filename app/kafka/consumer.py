import asyncio
import json
import structlog
from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.core.logging import setup_logging
from app.tasks.broker import broker
from app.tasks.order_tasks import process_order_task

logger = structlog.get_logger(__name__)


async def run_consumer() -> None:
    consumer = AIOKafkaConsumer(
        settings.kafka_new_order_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
        group_id="order-processor",
        auto_offset_reset="earliest",
    )
    await broker.startup()
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                payload = json.loads(msg.value.decode("utf-8"))
                order_id = payload.get("order_id")
                if order_id:
                    await process_order_task.kiq(order_id=order_id)
                    logger.info("enqueued_process_order_task", order_id=order_id)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("invalid_message", error=str(e))
    finally:
        await consumer.stop()
        await broker.shutdown()


def main() -> None:
    setup_logging(log_level=settings.log_level)
    asyncio.run(run_consumer())


if __name__ == "__main__":
    main()
