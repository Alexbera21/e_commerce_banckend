from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from app.database import user_collection
from bson import ObjectId

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    try:
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
    except:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return user


async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    return current_user


# ← NUEVO
async def get_current_moderator(current_user: dict = Depends(get_current_user)):
    """Admin y moderator pueden pasar."""
    if current_user["role"] not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Se requiere rol de moderador o admin")
    return current_user