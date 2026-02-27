from fastapi import APIRouter, HTTPException, Depends
from app.models.review_model import ReviewCreate
from app.services.review_service import (
    create_review_service,
    get_product_reviews_service,
    delete_review_service
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post(
    "/{product_id}",
    summary="Dejar una review",
    description="Crea una review para un producto. Solo puedes dejar una review por producto."
)
async def create_review(
    product_id: str,
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    result = await create_review_service(
        user_id=str(current_user["_id"]),
        user_name=current_user["name"],
        product_id=product_id,
        rating=review.rating,
        comment=review.comment
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get(
    "/{product_id}",
    summary="Ver reviews de un producto",
    description="Obtiene todas las reviews de un producto."
)
async def get_reviews(product_id: str):
    return await get_product_reviews_service(product_id)


@router.delete(
    "/{review_id}",
    summary="Eliminar mi review",
    description="Elimina tu propia review."
)
async def delete_review(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    deleted = await delete_review_service(review_id, str(current_user["_id"]))
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Review no encontrada")
    return {"message": "Review eliminada correctamente"}