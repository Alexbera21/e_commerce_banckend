from app.database import user_collection
from app.utils.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token  # ← NUEVO
)
from datetime import datetime
from bson import ObjectId


def serialize_user(user):
    user["id"] = str(user["_id"])
    del user["_id"]
    del user["hashed_password"]
    return user


async def register_user(user_data):
    existing_user = await user_collection.find_one({"email": user_data.email})
    if existing_user:
        return None

    user_dict = {
        "name": user_data.name,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "role": "admin" if user_data.email.endswith("@admin.com") else "customer",
        "created_at": datetime.utcnow()
    }

    result = await user_collection.insert_one(user_dict)
    created_user = await user_collection.find_one({"_id": result.inserted_id})
    return serialize_user(created_user)


async def authenticate_user(email: str, password: str):
    user = await user_collection.find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None

    token_data = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    }

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),  # ← NUEVO
        "token_type": "bearer"
    }