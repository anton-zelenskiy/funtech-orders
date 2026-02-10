import asyncio

import structlog
from app.tasks.broker import broker

logger = structlog.get_logger(__name__)


@broker.task
async def process_order_task(order_id: str) -> None:
    await asyncio.sleep(2)
    logger.info("order_processed", order_id=order_id)
