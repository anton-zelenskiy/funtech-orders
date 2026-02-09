from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, computed_field, field_validator

from app.db.models import OrderStatus


class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    items: list[OrderItem]

    @computed_field
    @property
    def total_price(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

    def to_dict(self) -> dict:
        return {
            "items": [item.model_dump() for item in self.items],
            "total_price": self.total_price,
        }


class OrderUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: UUID
    user_id: int
    items: list[OrderItem]
    total_price: float
    status: OrderStatus
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("items", mode="before")
    @classmethod
    def validate_items(cls, v):
        if isinstance(v, list):
            return [OrderItem.model_validate(item) if isinstance(item, dict) else item for item in v]
        return v
