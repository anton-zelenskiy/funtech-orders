import asyncio

from app.tasks.broker import broker


@broker.task
async def process_order_task(order_id: str) -> None:
    await asyncio.sleep(2)
    print(f"Order {order_id} processed")
