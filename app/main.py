from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_routes import router as auth_router
from app.routes.product_routes import router as product_router
from app.routes.order_routes import router as order_router
from app.routes.cart_routes import router as cart_router
from app.routes.review_routes import router as review_router
from app.routes.payment_routes import router as payment_router
from app.routes.banner_routes import router as banner_router
from app.routes.settings_routes      import router as settings_router
from app.routes.image_library_routes import router as library_router
from app.routes.user_routes import router as user_router

app = FastAPI(
    title="TechStore API",
    version="1.0.0",
    description="""
## 🛒 API de TechStore

Bienvenido a la API oficial de **TechStore**, tu tienda de tecnología.

### 🔐 ¿Cómo autenticarse?
1. Regístrate en `/auth/register`
2. Inicia sesión en `/auth/login`
3. Copia el `access_token` que te devuelve
4. Haz clic en el botón **Authorize 🔒** arriba
5. Escribe `Bearer tu_token_aquí` y confirma

### 👥 Roles de usuario
| Rol | Permisos |
|-----|----------|
| `customer` | Ver productos, carrito, órdenes propias |
| `moderator` | Todo lo anterior + crear/eliminar productos |
| `admin` | Acceso total |

### 📦 Flujo de compra
1. Agrega productos al carrito `/cart/add`
2. Revisa tu carrito `/cart/`
3. Confirma la compra `/orders/from-cart`
4. Paga con Stripe `/payments/create-payment-intent`
5. Revisa tus órdenes `/orders/my-orders`
    """,
    openapi_tags=[
        {
            "name": "Auth",
            "description": "🔐 **Autenticación** — Registro, login, refresh token y gestión de roles"
        },
        {
            "name": "Products",
            "description": "📦 **Productos** — Crear, listar, buscar y eliminar productos"
        },
        {
            "name": "Cart",
            "description": "🛒 **Carrito** — Agregar, actualizar, eliminar productos del carrito"
        },
        {
            "name": "Orders",
            "description": "📋 **Órdenes** — Crear órdenes, ver historial y gestionar estados"
        },
        {
            "name": "Reviews",
            "description": "⭐ **Reseñas** — Dejar y ver reseñas de productos"
        },
        {
            "name": "Payments",
            "description": "💳 **Pagos** — Procesar pagos con Stripe"
        },
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Auth"],
    summary="Estado de la API",
    description="Verifica que la API esté funcionando correctamente."
)
async def root():
    return {
        "message": "TechStore API funcionando correctamente 🚀",
        "status": "OK",
        "version": "1.0.0"
    }


app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(cart_router)
app.include_router(review_router)
app.include_router(payment_router)
app.include_router(banner_router)
app.include_router(settings_router)
app.include_router(library_router)
app.include_router(user_router)