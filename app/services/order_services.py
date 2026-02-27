from app.database import order_collection, product_collection, cart_collection
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime


VALID_STATUSES = ["pending", "confirmed", "shipped", "delivered", "cancelled"]


def _serialize_order(order: dict) -> dict:
    order["_id"] = str(order["_id"])
    return order


async def _descontar_stock(product_id: str, quantity: int):
    """Descuenta stock del producto, lanza error si no hay suficiente."""
    product = await product_collection.find_one({"_id": ObjectId(product_id)})

    if not product:
        raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")

    if product["stock"] < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente para '{product['name']}'. Disponible: {product['stock']}"
        )

    await product_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$inc": {"stock": -quantity}}
    )


# ─────────────────────────────────────────────
# CREAR ORDEN DESDE EL CARRITO ← NUEVO
# ─────────────────────────────────────────────

async def create_order_from_cart_service(user_id: str):
    # 1. Obtener carrito
    cart = await cart_collection.find_one({"user_id": user_id})

    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    items_snapshot = []
    total = 0

    # 2. Validar stock y construir snapshot
    for item in cart["items"]:
        product = await product_collection.find_one(
            {"_id": ObjectId(item["product_id"])}
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Producto '{item['name']}' ya no existe"
            )

        if product["stock"] < item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{product['name']}'. Disponible: {product['stock']}"
            )

        item_total = product["price"] * item["quantity"]
        total += item_total

        items_snapshot.append({
            "product_id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"],
            "quantity": item["quantity"],
            "image": item.get("image")
        })

    # 3. Descontar stock de cada producto
    for item in items_snapshot:
        await product_collection.update_one(
            {"_id": ObjectId(item["product_id"])},
            {"$inc": {"stock": -item["quantity"]}}
        )

    # 4. Crear la orden
    order = {
        "user_id": user_id,
        "items": items_snapshot,
        "total": round(total, 2),
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = await order_collection.insert_one(order)
    order["_id"] = str(result.inserted_id)

    # 5. Vaciar el carrito
    await cart_collection.update_one(
        {"user_id": user_id},
        {"$set": {"items": [], "updated_at": datetime.utcnow()}}
    )

    return order


# ─────────────────────────────────────────────
# CREAR ORDEN MANUAL (se mantiene)
# ─────────────────────────────────────────────

async def create_order_service(user_id: str, order_data):
    items_snapshot = []
    total = 0

    for item in order_data.items:
        product = await product_collection.find_one(
            {"_id": ObjectId(item.product_id)}
        )

        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{product['name']}'"
            )

        item_total = product["price"] * item.quantity
        total += item_total

        items_snapshot.append({
            "product_id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"],
            "quantity": item.quantity,
            "image": product["images"][0] if product.get("images") else None
        })

    # Descontar stock
    for item in items_snapshot:
        await product_collection.update_one(
            {"_id": ObjectId(item["product_id"])},
            {"$inc": {"stock": -item["quantity"]}}
        )

    order = {
        "user_id": user_id,
        "items": items_snapshot,
        "total": round(total, 2),
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = await order_collection.insert_one(order)
    order["_id"] = str(result.inserted_id)
    return order


# ─────────────────────────────────────────────
# CONSULTAS
# ─────────────────────────────────────────────

async def get_user_orders_service(user_id: str):
    orders = []
    async for order in order_collection.find({"user_id": user_id}).sort("created_at", -1):
        orders.append(_serialize_order(order))
    return orders


async def get_all_orders_service():
    orders = []
    async for order in order_collection.find().sort("created_at", -1):
        orders.append(_serialize_order(order))
    return orders


# ─────────────────────────────────────────────
# ACTUALIZAR ESTADO (ADMIN) ← NUEVO
# ─────────────────────────────────────────────

async def update_order_status_service(order_id: str, new_status: str):
    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Opciones: {VALID_STATUSES}"
        )

    result = await order_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    order = await order_collection.find_one({"_id": ObjectId(order_id)})
    return _serialize_order(order)