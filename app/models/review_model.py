from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1, le=5, description="Calificación del 1 al 5")
    comment: str = Field(..., min_length=5, description="Comentario de la review")


class ReviewInDB(BaseModel):
    user_id: str
    user_name: str
    product_id: str
    rating: float
    comment: str
    created_at: datetime