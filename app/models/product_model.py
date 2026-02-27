from pydantic import BaseModel
from typing import List, Optional

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    original_price: Optional[float] = None
    category: str
    stock: int
    images: List[str] = []
    rating: Optional[float] = 0