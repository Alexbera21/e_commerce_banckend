from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import stripe
import os
from app.utils.dependencies import get_current_user
from app.database import order_collection
from bson import ObjectId

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/payments", tags=["Payments"])


class PaymentIntent(BaseModel):
    order_id: str


class ConfirmPayment(BaseModel):
    order_id: str
    payment_intent_id: str


@router.post(
    "/create-payment-intent",
    summary="Crear intención de pago",
    description="Crea un PaymentIntent de Stripe para procesar el pago de una orden."
)
async def create_payment_intent(
    body: PaymentIntent,
    current_user: dict = Depends(get_current_user)
):
    try:
        order = await order_collection.find_one({"_id": ObjectId(body.order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        if str(order["user_id"]) != str(current_user["_id"]):
            raise HTTPException(status_code=403, detail="No autorizado")

        amount = int(order["total"] * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="pen",
            metadata={
                "order_id": body.order_id,
                "user_id": str(current_user["_id"])
            }
        )

        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": order["total"]
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/confirm",
    summary="Confirmar pago",
    description="Confirma el pago y actualiza el estado de la orden."
)
async def confirm_payment(
    body: ConfirmPayment,
    current_user: dict = Depends(get_current_user)
):
    try:
        intent = stripe.PaymentIntent.retrieve(body.payment_intent_id)

        if intent.status == "succeeded":
            await order_collection.update_one(
                {"_id": ObjectId(body.order_id)},
                {"$set": {
                    "status": "confirmed",
                    "payment_status": "paid",
                    "payment_intent_id": body.payment_intent_id
                }}
            )
            return {"message": "Pago confirmado exitosamente", "status": "paid"}
        else:
            raise HTTPException(status_code=400, detail="El pago no fue completado")

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/status/{order_id}",
    summary="Estado del pago",
    description="Verifica el estado del pago de una orden."
)
async def payment_status(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        order = await order_collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        return {
            "order_id": order_id,
            "payment_status": order.get("payment_status", "pending"),
            "order_status": order.get("status", "pending"),
            "total": order.get("total", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))