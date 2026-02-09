import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.db.models import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderItem
from app.services import order_service


@pytest.mark.asyncio
async def test_create_order():
    repo = AsyncMock()
    order_data = OrderCreate(items=[OrderItem(name="item1", quantity=2, price=5.0)])
    order = Order(
        id=uuid.uuid4(),
        user_id=1,
        items=[{"name": "item1", "quantity": 2, "price": 5.0}],
        total_price=10.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
    repo.create = AsyncMock(return_value=order)
    result = await order_service.create_order(repo, user_id=1, order_data=order_data)
    assert result.status == OrderStatus.PENDING
    assert result.total_price == 10.0
    repo.create.assert_called_once_with(
        user_id=1,
        items=[{"name": "item1", "quantity": 2, "price": 5.0}],
        total_price=10.0,
        status=OrderStatus.PENDING,
    )


@pytest.mark.asyncio
async def test_get_order():
    repo = AsyncMock()
    order_id = uuid.uuid4()
    order = Order(
        id=order_id,
        user_id=1,
        items=[],
        total_price=0.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
    repo.get_by_id = AsyncMock(return_value=order)
    result = await order_service.get_order(repo, order_id)
    assert result is not None
    assert result.id == order_id


@pytest.mark.asyncio
async def test_get_order_not_found():
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    result = await order_service.get_order(repo, uuid.uuid4())
    assert result is None
