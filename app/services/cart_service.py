from app.database import cart_collection, product_collection
from bson import ObjectId
from datetime import datetime


def _serialize_cart(cart: dict) -> dict:
    cart.pop("_id", None)
    cart["total"] = round(
        sum(i["price"] * i["quantity"] for i in cart.get("items", [])), 2
    )
    cart["total_items"] = sum(i["quantity"] for i in cart.get("items", []))
    return cart


async def _get_product(product_id: str):
    try:
        return await product_collection.find_one({"_id": ObjectId(product_id)})
    except Exception:
        return None


async def get_cart_service(user_id: str):
    cart = await cart_collection.find_one({"user_id": user_id})
    if not cart:
        return {"user_id": user_id, "items": [], "total": 0.0, "total_items": 0}
    return _serialize_cart(cart)


async def add_to_cart_service(user_id: str, product_id: str, quantity: int):
    product = await _get_product(product_id)
    if not product:
        return {"error": "Producto no encontrado"}

    if product["stock"] < quantity:
        return {"error": f"Stock insuficiente. Disponible: {product['stock']}"}

    nuevo_item = {
        "product_id": product_id,
        "name": product["name"],
        "price": product["price"],
        "original_price": product.get("original_price"),
        "quantity": quantity,
        "image": product["images"][0] if product.get("images") else None,
        "stock": product["stock"],
    }

    cart = await cart_collection.find_one({"user_id": user_id})

    if not cart:
        doc = {
            "user_id": user_id,
            "items": [nuevo_item],
            "updated_at": datetime.utcnow()
        }
        await cart_collection.insert_one(doc)
        return _serialize_cart(doc)

    items = cart.get("items", [])
    encontrado = False

    for item in items:
        if item["product_id"] == product_id:
            nueva_cantidad = item["quantity"] + quantity
            if nueva_cantidad > product["stock"]:
                return {"error": f"Stock insuficiente. Máximo: {product['stock']}"}
            item["quantity"] = nueva_cantidad
            encontrado = True
            break

    if not encontrado:
        items.append(nuevo_item)

    await cart_collection.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "updated_at": datetime.utcnow()}}
    )
    cart["items"] = items
    return _serialize_cart(cart)


async def update_cart_item_service(user_id: str, product_id: str, quantity: int):
    cart = await cart_collection.find_one({"user_id": user_id})
    if not cart:
        return {"error": "Carrito no encontrado"}

    items = cart.get("items", [])

    if quantity == 0:
        items = [i for i in items if i["product_id"] != product_id]
    else:
        product = await _get_product(product_id)
        if not product:
            return {"error": "Producto no encontrado"}
        if quantity > product["stock"]:
            return {"error": f"Stock insuficiente. Disponible: {product['stock']}"}

        encontrado = False
        for item in items:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                item["stock"] = product["stock"]
                encontrado = True
                break

        if not encontrado:
            return {"error": "El producto no está en el carrito"}

    await cart_collection.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "updated_at": datetime.utcnow()}}
    )
    cart["items"] = items
    return _serialize_cart(cart)


async def remove_from_cart_service(user_id: str, product_id: str):
    cart = await cart_collection.find_one({"user_id": user_id})
    if not cart:
        return {"error": "Carrito no encontrado"}

    items = [i for i in cart.get("items", []) if i["product_id"] != product_id]
    await cart_collection.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "updated_at": datetime.utcnow()}}
    )
    cart["items"] = items
    return _serialize_cart(cart)


async def clear_cart_service(user_id: str):
    await cart_collection.update_one(
        {"user_id": user_id},
        {"$set": {"items": [], "updated_at": datetime.utcnow()}}
    )
    return {"user_id": user_id, "items": [], "total": 0.0, "total_items": 0}