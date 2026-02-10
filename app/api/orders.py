from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.decorators import invalidate_cache
from app.core.limiter import limiter
from app.kafka.producer import send_new_order_event
from app.core.dependencies import get_current_user
from app.db.base import get_db_session
from app.db.models import User
from app.db.repositories.order_repository import OrderRepository
from app.core.config import settings
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services import order_service

router = APIRouter()


@router.post("/", response_model=OrderResponse)
@limiter.limit(settings.rate_limit_default)
async def create_order(
    request: Request,
    body: OrderCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    repository = OrderRepository(session)
    order = await order_service.create_order(
        repository,
        user_id=current_user.id,
        order_data=body,
    )
    await send_new_order_event(order.id, current_user.id)
    return OrderResponse.model_validate(order)


@router.get("/{order_id}/", response_model=OrderResponse)
@limiter.limit(settings.rate_limit_default)
async def get_order(
    request: Request,
    order_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    response = await order_service.get_order(order_id, session)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if response.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access this order")
    return response


@router.patch("/{order_id}/", response_model=OrderResponse)
@limiter.limit(settings.rate_limit_default)
async def update_order(
    request: Request,
    order_id: UUID,
    body: OrderUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    order = await order_service.get_order(order_id, session)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access this order")
    
    repository = OrderRepository(session)
    updated = await order_service.update_order_status(repository, order_id, body.status)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    await invalidate_cache(f"order:{order_id}")
    return OrderResponse.model_validate(updated)


@router.get("/user/{user_id}/", response_model=list[OrderResponse])
@limiter.limit(settings.rate_limit_default)
async def get_orders_by_user(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[OrderResponse]:
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your orders")
    repository = OrderRepository(session)
    orders = await order_service.get_orders_by_user_id(repository, user_id)
    return [OrderResponse.model_validate(o) for o in orders]
