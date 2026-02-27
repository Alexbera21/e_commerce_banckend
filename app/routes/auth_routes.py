import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from bson import ObjectId
from passlib.context import CryptContext

from app.models.user_model import UserCreate
from app.models.token_model import RefreshTokenRequest
from app.services.auth_service import register_user, authenticate_user
from app.utils.auth_utils import decode_token, create_access_token, create_refresh_token
from app.utils.dependencies import get_current_admin, get_current_user
from app.database import user_collection, database
from app.services.email_service import (
    send_welcome_email,
    send_password_reset,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context       = CryptContext(schemes=["bcrypt"], deprecated="auto")
reset_tokens_col  = database["reset_tokens"]


@router.post("/register", summary="Registrarse")
async def register(user: UserCreate):
    created_user = await register_user(user)
    if not created_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Email de bienvenida (no bloquea si falla)
    try:
        send_welcome_email(user.email, user.name)
    except Exception as e:
        print(f"[EMAIL WARN] welcome: {e}")

    return {"message": "Usuario creado correctamente"}


@router.post("/login", summary="Iniciar sesión")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = await authenticate_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return token


@router.get("/me", summary="Mi perfil")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id":    str(current_user["_id"]),
        "name":  current_user["name"],
        "email": current_user["email"],
        "role":  current_user["role"],
    }


@router.post("/refresh", summary="Renovar token")
async def refresh_token(body: RefreshTokenRequest):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    token_data = {
        "user_id": payload["user_id"],
        "email":   payload["email"],
        "role":    payload["role"],
    }
    return {
        "access_token":  create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type":    "bearer",
    }


class RoleUpdate(BaseModel):
    user_id: str
    role: str


@router.put("/users/role", summary="Cambiar rol de usuario (Admin)")
async def update_user_role(body: RoleUpdate, admin: dict = Depends(get_current_admin)):
    valid_roles = ["customer", "moderator", "admin"]
    if body.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Rol inválido. Opciones: {valid_roles}")

    result = await user_collection.update_one(
        {"_id": ObjectId(body.user_id)},
        {"$set": {"role": body.role}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"message": f"Rol actualizado a '{body.role}' correctamente"}


# ── RECUPERACIÓN DE CONTRASEÑA ────────────────────────────────────────────────

@router.post("/forgot-password", summary="Solicitar recuperación de contraseña")
async def forgot_password(request: Request):
    body  = await request.json()
    email = body.get("email", "").strip().lower()

    if not email:
        raise HTTPException(status_code=400, detail="Email requerido")

    user = await user_collection.find_one({"email": email})

    # Responde igual exista o no el email (seguridad)
    if not user:
        return {"message": "Si el email está registrado recibirás un correo en breve"}

    token   = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(minutes=30)

    await reset_tokens_col.update_one(
        {"email": email},
        {"$set": {"token": token, "expires": expires, "used": False}},
        upsert=True
    )

    try:
        send_password_reset(
            user_email=email,
            user_name=user.get("name", "Usuario"),
            reset_token=token,
            base_url="http://localhost:5173"
        )
    except Exception as e:
        print(f"[EMAIL WARN] password_reset: {e}")

    return {"message": "Si el email está registrado recibirás un correo en breve"}


class ResetPasswordBody(BaseModel):
    token:        str
    new_password: str


@router.post("/reset-password", summary="Restablecer contraseña con token")
async def reset_password(body: ResetPasswordBody):
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Mínimo 6 caracteres")

    record = await reset_tokens_col.find_one({"token": body.token})

    if not record:
        raise HTTPException(status_code=400, detail="Token inválido")
    if record.get("used"):
        raise HTTPException(status_code=400, detail="Token ya utilizado")
    if datetime.utcnow() > record["expires"]:
        raise HTTPException(status_code=400, detail="Token expirado — solicita uno nuevo")

    hashed = pwd_context.hash(body.new_password)

    await user_collection.update_one(
        {"email": record["email"]},
        {"$set": {"password": hashed}}
    )
    await reset_tokens_col.update_one(
        {"token": body.token},
        {"$set": {"used": True}}
    )

    return {"message": "Contraseña actualizada correctamente"}