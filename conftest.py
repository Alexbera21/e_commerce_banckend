import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient


def get_mock_db():
    client = AsyncMongoMockClient()
    db = client["ecommerce_test"]

    import app.database as database
    database.user_collection = db["users"]
    database.product_collection = db["products"]
    database.order_collection = db["orders"]
    database.cart_collection = db["carts"]

    return db


@pytest.fixture
def mock_db():
    return get_mock_db()


@pytest.fixture
async def client(mock_db):
    from app.main import app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_headers(client):
    await client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234"
    })
    response = await client.post("/auth/login", data={
        "username": "test@test.com",
        "password": "test1234"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(client):
    await client.post("/auth/register", json={
        "name": "Admin Test",
        "email": "test@admin.com",
        "password": "test1234"
    })
    response = await client.post("/auth/login", data={
        "username": "test@admin.com",
        "password": "test1234"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}