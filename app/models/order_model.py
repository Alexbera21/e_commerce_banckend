from pydantic import BaseModel
from typing import List
from datetime import datetime


class OrderItem(BaseModel):
    product_id: str
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItem]


class OrderInDB(BaseModel):
    user_id: str
    items: list
    total: float
    status: str = "pending"
    created_at: datetime = datetime.utcnow()

class OrderStatusUpdate(BaseModel):
    status: str  # pending, confirmed, shipped, delivered, cancelled    