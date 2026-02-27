from fastapi import APIRouter, Depends
from app.models.order_model import OrderCreate, OrderStatusUpdate
from app.services.order_services import (
    create_order_service,
    create_order_from_cart_service,
    get_user_orders_service,
    get_all_orders_service,
    update_order_status_service,
)
from app.utils.dependencies import get_current_user, get_current_admin
from app.database import user_collection, order_collection
from app.services.email_service import (
    send_order_confirmation,
    send_admin_new_order,
    send_order_status_update,
)
from bson import ObjectId

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/from-cart", summary="Confirmar compra desde el carrito")
async def create_from_cart(current_user: dict = Depends(get_current_user)):
    order = await create_order_from_cart_service(str(current_user["_id"]))

    # Emails de confirmación
    try:
        send_order_confirmation(order, current_user["email"], current_user.get("name", "Cliente"))
        send_admin_new_order(order,    current_user["email"], current_user.get("name", "Cliente"))
    except Exception as e:
        print(f"[EMAIL WARN] from_cart: {e}")

    return order


@router.post("/", summary="Crear orden manual")
async def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    created = await create_order_service(str(current_user["_id"]), order)

    try:
        send_order_confirmation(created, current_user["email"], current_user.get("name", "Cliente"))
        send_admin_new_order(created,    current_user["email"], current_user.get("name", "Cliente"))
    except Exception as e:
        print(f"[EMAIL WARN] create_order: {e}")

    return created


@router.get("/my-orders", summary="Mis órdenes")
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    return await get_user_orders_service(str(current_user["_id"]))


@router.get("/all", summary="Todas las órdenes (Admin)")
async def get_all_orders(admin_user: dict = Depends(get_current_admin)):
    return await get_all_orders_service()


@router.put("/{order_id}/status", summary="Actualizar estado de orden (Admin)")
async def update_status(
    order_id: str,
    body: OrderStatusUpdate,
    admin_user: dict = Depends(get_current_admin)
):
    updated = await update_order_status_service(order_id, body.status)

    # Notificar al cliente del cambio de estado
    try:
        order = await order_collection.find_one({"_id": ObjectId(order_id)})
        if order and order.get("user_id"):
            user = await user_collection.find_one({"_id": ObjectId(order["user_id"])})
            if user:
                send_order_status_update(
                    order=order,
                    user_email=user["email"],
                    user_name=user.get("name", "Cliente"),
                    new_status=body.status,
                )
    except Exception as e:
        print(f"[EMAIL WARN] status_update: {e}")

    return updated