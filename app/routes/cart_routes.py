from fastapi import APIRouter, HTTPException, Depends
from app.models.cart_model import CartItemAdd, CartItemUpdate
from app.services.cart_service import (
    get_cart_service,
    add_to_cart_service,
    update_cart_item_service,
    remove_from_cart_service,
    clear_cart_service,
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


def _check(result: dict):
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get(
    "/",
    summary="Ver mi carrito",
    description="Obtiene el carrito actual del usuario con todos los productos y el total."
)
async def view_cart(current_user: dict = Depends(get_current_user)):
    return await get_cart_service(str(current_user["_id"]))


@router.post(
    "/add",
    summary="Agregar producto al carrito",
    description="Agrega un producto al carrito. Si ya existe, suma la cantidad."
)
async def add_item(item: CartItemAdd, current_user: dict = Depends(get_current_user)):
    result = await add_to_cart_service(str(current_user["_id"]), item.product_id, item.quantity)
    return _check(result)


@router.put(
    "/update",
    summary="Actualizar cantidad de un producto",
    description="Cambia la cantidad de un producto en el carrito. Si pones cantidad 0, lo elimina."
)
async def update_item(item: CartItemUpdate, current_user: dict = Depends(get_current_user)):
    result = await update_cart_item_service(str(current_user["_id"]), item.product_id, item.quantity)
    return _check(result)


@router.delete(
    "/remove/{product_id}",
    summary="Eliminar producto del carrito",
    description="Elimina un producto específico del carrito."
)
async def remove_item(product_id: str, current_user: dict = Depends(get_current_user)):
    result = await remove_from_cart_service(str(current_user["_id"]), product_id)
    return _check(result)


@router.delete(
    "/clear",
    summary="Vaciar carrito",
    description="Elimina todos los productos del carrito."
)
async def clear(current_user: dict = Depends(get_current_user)):
    return await clear_cart_service(str(current_user["_id"]))