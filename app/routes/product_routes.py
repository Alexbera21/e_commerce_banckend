from fastapi import APIRouter, HTTPException, Query, Depends, status, UploadFile, File
from typing import Optional
import cloudinary
import cloudinary.uploader
import time
from bson import ObjectId

from app.cloudinary_config import *
from app.utils.dependencies import get_current_moderator
from app.models.product_model import ProductCreate
from app.database import product_collection
from app.services.product_service import (
    create_product_service,
    get_products_service,
    get_product_by_id_service,
    delete_product_service,
    update_product_images_service,
    delete_product_image_service
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Crea un nuevo producto. Solo administradores y moderadores."
)
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_moderator)
):
    return await create_product_service(product)


@router.patch(
    "/{product_id}",
    summary="Actualizar producto",
    description="Actualiza los datos de un producto. Solo administradores y moderadores."
)
async def update_product(
    product_id: str,
    product: dict,
    current_user: dict = Depends(get_current_moderator)
):
    update_data = {k: v for k, v in product.items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    result = await product_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return await get_product_by_id_service(product_id)


@router.post(
    "/{product_id}/upload-image",
    summary="Subir imagen del producto",
    description="Sube una imagen a Cloudinary y la agrega a la galería del producto."
)
async def upload_image(
    product_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_moderator)
):
    product = await get_product_by_id_service(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes JPG, PNG o WEBP")

    unique_id = f"product_{product_id}_{int(time.time())}"

    contents = await file.read()
    result = cloudinary.uploader.upload(
        contents,
        folder="techstore/products",
        public_id=unique_id,
        resource_type="image"
    )

    image_url = result["secure_url"]
    updated = await update_product_images_service(product_id, image_url)

    return {
        "message": "Imagen agregada a la galería",
        "image_url": image_url,
        "total_imagenes": len(updated["images"]),
        "product": updated
    }


@router.delete(
    "/{product_id}/delete-image",
    summary="Eliminar imagen del producto",
    description="Elimina una imagen específica de la galería del producto."
)
async def delete_image(
    product_id: str,
    image_url: str,
    current_user: dict = Depends(get_current_moderator)
):
    product = await get_product_by_id_service(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if image_url not in product["images"]:
        raise HTTPException(status_code=404, detail="Imagen no encontrada en el producto")

    public_id = image_url.split("/")[-1].split(".")[0]
    cloudinary.uploader.destroy(f"techstore/products/{public_id}")

    updated = await delete_product_image_service(product_id, image_url)

    return {
        "message": "Imagen eliminada correctamente",
        "total_imagenes": len(updated["images"]),
        "product": updated
    }


@router.get(
    "/",
    summary="Listar productos",
    description="Obtiene todos los productos. Puedes filtrar por categoría, precio y buscar por nombre."
)
async def get_products(
    category: Optional[str] = Query(None, description="Categoría: smartphones, laptops, gaming, audio, cameras, components"),
    min_price: Optional[float] = Query(None, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, description="Precio máximo"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
):
    query = {}
    if category:
        query["category"] = category
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    return await get_products_service(query)


@router.get(
    "/{product_id}",
    summary="Obtener producto por ID",
    description="Obtiene el detalle de un producto específico."
)
async def get_product(product_id: str):
    product = await get_product_by_id_service(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar producto",
    description="Elimina un producto. Solo administradores y moderadores."
)
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_moderator)
):
    deleted = await delete_product_service(product_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado correctamente"}