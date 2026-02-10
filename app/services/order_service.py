import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.decorators import cached_entity
from app.db.models import Order, OrderStatus
from app.db.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse


ORDER_DETAIL_CACHE_TTL = 300


@cached_entity(
    key_prefix="order:",
    key_param_name="order_id",
    response_model=OrderResponse,
    ttl=ORDER_DETAIL_CACHE_TTL,
)
async def get_order(
    order_id: UUID,
    session: AsyncSession,
) -> OrderResponse | None:
    repository = OrderRepository(session)
    order = await repository.get_by_id(order_id)
    if order is None:
        return None
    return OrderResponse.model_validate(order)


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
