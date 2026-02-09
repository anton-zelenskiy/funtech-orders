import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, OrderStatus


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, order_id: uuid.UUID) -> Order | None:
        result = await self._session.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[Order]:
        result = await self._session.execute(
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: int,
        items: list,
        total_price: float,
        status: OrderStatus = OrderStatus.PENDING,
    ) -> Order:
        order = Order(
            user_id=user_id,
            items=items,
            total_price=total_price,
            status=status,
        )
        self._session.add(order)
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def update_status(self, order_id: uuid.UUID, status: OrderStatus) -> Order | None:
        order = await self.get_by_id(order_id)
        if order is None:
            return None
        order.status = status
        await self._session.flush()
        await self._session.refresh(order)
        return order
