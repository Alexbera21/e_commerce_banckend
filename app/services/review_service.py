from app.database import review_collection, product_collection
from bson import ObjectId
from datetime import datetime


def serialize_review(review: dict) -> dict:
    review["id"] = str(review["_id"])
    del review["_id"]
    return review


async def create_review_service(user_id: str, user_name: str, product_id: str, rating: float, comment: str):
    # Verificar si ya dejó una review
    existing = await review_collection.find_one({
        "user_id": user_id,
        "product_id": product_id
    })
    if existing:
        return {"error": "Ya dejaste una review para este producto"}

    review = {
        "user_id": user_id,
        "user_name": user_name,
        "product_id": product_id,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.utcnow()
    }

    await review_collection.insert_one(review)

    # Recalcular rating promedio del producto
    reviews = []
    async for r in review_collection.find({"product_id": product_id}):
        reviews.append(r)

    if reviews:
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        await product_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"rating": round(avg_rating, 1)}}
        )

    return serialize_review(review)


async def get_product_reviews_service(product_id: str):
    reviews = []
    async for review in review_collection.find(
        {"product_id": product_id}
    ).sort("created_at", -1):
        reviews.append(serialize_review(review))
    return reviews


async def delete_review_service(review_id: str, user_id: str):
    try:
        result = await review_collection.delete_one({
            "_id": ObjectId(review_id),
            "user_id": user_id
        })
        return result.deleted_count
    except:
        return 0