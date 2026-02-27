import pytest


@pytest.mark.asyncio
async def test_get_products_public(client):
    response = await client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_product_as_admin(client, admin_headers):
    response = await client.post("/products/", json={
        "name": "Producto Test",
        "description": "Descripción test",
        "price": 99.99,
        "original_price": 120.00,
        "category": "electronics",
        "stock": 10,
        "images": []
    }, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Producto Test"
    assert response.json()["discount_percentage"] > 0


@pytest.mark.asyncio
async def test_create_product_unauthorized(client, auth_headers):
    response = await client.post("/products/", json={
        "name": "Producto Test",
        "description": "Descripción test",
        "price": 99.99,
        "category": "electronics",
        "stock": 10
    }, headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_product_by_id(client, admin_headers):
    created = await client.post("/products/", json={
        "name": "Producto ID Test",
        "description": "Test",
        "price": 50.0,
        "category": "test",
        "stock": 5
    }, headers=admin_headers)
    product_id = created.json()["id"]
    response = await client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id