from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from bson import ObjectId
from app.database import database
from app.utils.dependencies import get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])
user_collection = database["users"]

def serialize_user(u):
    return {
        "id":         str(u["_id"]),
        "name":       u.get("name", ""),
        "email":      u.get("email", ""),
        "role":       u.get("role", "customer"),
        "created_at": str(u.get("created_at", "")),
    }

@router.get("/", summary="Listar usuarios (Admin)")
async def get_users(admin: dict = Depends(get_current_admin)):
    users = await user_collection.find().to_list(1000)
    return [serialize_user(u) for u in users]

class RoleUpdate(BaseModel):
    role: str

@router.put("/{user_id}/role", summary="Cambiar rol de usuario (Admin)")
async def update_role(
    user_id: str,
    body: RoleUpdate,
    admin: dict = Depends(get_current_admin)
):
    valid = ["customer", "admin", "moderator"]
    if body.role not in valid:
        raise HTTPException(status_code=400, detail=f"Rol inválido. Opciones: {valid}")

    result = await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": body.role}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"message": f"Rol actualizado a '{body.role}'"}

@router.delete("/{user_id}", summary="Eliminar usuario (Admin)")
async def delete_user(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado"}