import uuid

from app.db.models import Order, OrderStatus
from app.db.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate


async def create_order(
    repository: OrderRepository,
    user_id: int,
    order_data: OrderCreate,
) -> Order:
    order_dict = order_data.to_dict()
    return await repository.create(
        user_id=user_id,
        items=order_dict["items"],
        total_price=order_dict["total_price"],
        status=OrderStatus.PENDING,
    )


async def get_order(repository: OrderRepository, order_id: uuid.UUID) -> Order | None:
    return await repository.get_by_id(order_id)


async def update_order_status(
    repository: OrderRepository,
    order_id: uuid.UUID,
    status: OrderStatus,
) -> Order | None:
    return await repository.update_status(order_id, status)


async def get_orders_by_user_id(
    repository: OrderRepository,
    user_id: int,
) -> list[Order]:
    return await repository.get_by_user_id(user_id)
