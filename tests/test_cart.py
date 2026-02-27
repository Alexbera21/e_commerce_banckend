import pytest


@pytest.mark.asyncio
async def test_get_empty_cart(client, auth_headers):
    response = await client.get("/cart/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0.0


@pytest.mark.asyncio
async def test_add_to_cart(client, auth_headers, admin_headers):
    product = await client.post("/products/", json={
        "name": "Producto Carrito",
        "description": "Test",
        "price": 25.0,
        "category": "test",
        "stock": 10
    }, headers=admin_headers)
    product_id = product.json()["id"]

    response = await client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 2
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 50.0
    assert response.json()["total_items"] == 2


@pytest.mark.asyncio
async def test_add_to_cart_insufficient_stock(client, auth_headers, admin_headers):
    product = await client.post("/products/", json={
        "name": "Producto Stock Bajo",
        "description": "Test",
        "price": 10.0,
        "category": "test",
        "stock": 2
    }, headers=admin_headers)
    product_id = product.json()["id"]

    response = await client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 99
    }, headers=auth_headers)
    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]