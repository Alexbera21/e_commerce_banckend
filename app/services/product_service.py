from app.database import product_collection
from datetime import datetime
from bson import ObjectId


def serialize_product(product):
    product["id"] = str(product["_id"])
    del product["_id"]
    return product


async def create_product_service(product):
    product_dict = product.model_dump()

    if product.original_price and product.original_price > product.price:
        discount = (
            (product.original_price - product.price)
            / product.original_price
        ) * 100
        product_dict["discount_percentage"] = round(discount, 2)
    else:
        product_dict["discount_percentage"] = 0

    product_dict["created_at"] = datetime.utcnow()
    result = await product_collection.insert_one(product_dict)
    created_product = await product_collection.find_one({"_id": result.inserted_id})
    return serialize_product(created_product)


async def get_products_service(query):
    products = []
    async for product in product_collection.find(query):
        products.append(serialize_product(product))
    return products


async def get_product_by_id_service(product_id):
    try:
        product = await product_collection.find_one({"_id": ObjectId(product_id)})
    except:
        return None
    if not product:
        return None
    return serialize_product(product)


async def delete_product_service(product_id):
    try:
        result = await product_collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count
    except:
        return 0


async def update_product_images_service(product_id: str, image_url: str):
    try:
        product = await product_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return None

        images = product.get("images", [])
        if image_url not in images:
            images.append(image_url)

        await product_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"images": images}}
        )

        updated = await product_collection.find_one({"_id": ObjectId(product_id)})
        return serialize_product(updated)
    except:
        return None


async def delete_product_image_service(product_id: str, image_url: str):
    try:
        product = await product_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return None

        images = [img for img in product.get("images", []) if img != image_url]

        await product_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"images": images}}
        )

        updated = await product_collection.find_one({"_id": ObjectId(product_id)})
        return serialize_product(updated)
    except:
        return None