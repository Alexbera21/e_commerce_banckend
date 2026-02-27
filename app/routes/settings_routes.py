from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.database import database
from app.utils.dependencies import get_current_moderator

router = APIRouter(prefix="/settings", tags=["Settings"])
settings_col = database["settings"]

# ── CATEGORÍAS ──
class Category(BaseModel):
    id: str
    label: str
    emoji: str
    color: str

class CategoriesUpdate(BaseModel):
    categories: List[Category]

DEFAULT_CATEGORIES = [
    {"id": "smartphones", "label": "Smartphones", "emoji": "📱", "color": "#00d4ff"},
    {"id": "laptops",     "label": "Laptops",     "emoji": "💻", "color": "#7c3aed"},
    {"id": "gaming",      "label": "Gaming",      "emoji": "🎮", "color": "#ff6b35"},
    {"id": "audio",       "label": "Audio",       "emoji": "🎧", "color": "#00ff88"},
    {"id": "cameras",     "label": "Cámaras",     "emoji": "📷", "color": "#f59e0b"},
    {"id": "components",  "label": "Componentes", "emoji": "🔌", "color": "#ec4899"},
]

@router.get("/categories", summary="Obtener categorías")
async def get_categories():
    doc = await settings_col.find_one({"key": "categories"})
    if not doc:
        return {"categories": DEFAULT_CATEGORIES}
    return {"categories": doc["categories"]}

@router.put("/categories", summary="Actualizar categorías (Admin)")
async def update_categories(
    body: CategoriesUpdate,
    current_user: dict = Depends(get_current_moderator)
):
    cats = [c.dict() for c in body.categories]
    await settings_col.update_one(
        {"key": "categories"},
        {"$set": {"categories": cats}},
        upsert=True
    )
    return {"message": "Categorías actualizadas", "categories": cats}

# ── CONFIGURACIÓN DE TIENDA ──
class StoreUpdate(BaseModel):
    name: Optional[str] = None
    logo_text: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    whatsapp: Optional[str] = None
    welcome_message: Optional[str] = None

DEFAULT_STORE = {
    "name": "TechStore",
    "logo_text": "TECHSTORE",
    "logo_url": None,
    "description": "Tu tienda tech de confianza. Smartphones, laptops, gaming y más.",
    "whatsapp": "913340613",
    "welcome_message": "¡Hola! 👋 Bienvenido a TechStore. ¿En qué puedo ayudarte hoy?"
}

@router.get("/store", summary="Obtener configuración de tienda")
async def get_store():
    doc = await settings_col.find_one({"key": "store"})
    if not doc:
        return DEFAULT_STORE
    return {k: v for k, v in doc.items() if k not in ["_id", "key"]}

@router.put("/store", summary="Actualizar configuración de tienda (Admin)")
async def update_store(
    body: StoreUpdate,
    current_user: dict = Depends(get_current_moderator)
):
    update_data = {k: v for k, v in body.dict().items() if v is not None}
    await settings_col.update_one(
        {"key": "store"},
        {"$set": update_data},
        upsert=True
    )
    return {"message": "Configuración actualizada", **update_data}