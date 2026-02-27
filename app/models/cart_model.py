from pydantic import BaseModel

class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = 1

class CartItemUpdate(BaseModel):
    product_id: str
    quantity: int  # si mandas 0 elimina el ítem