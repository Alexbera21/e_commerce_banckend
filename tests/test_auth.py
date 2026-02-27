import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/auth/register", json={
        "name": "Nuevo Usuario",
        "email": "nuevo@test.com",
        "password": "123456"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Usuario creado correctamente"


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={
        "name": "Login User",
        "email": "login@test.com",
        "password": "123456"
    })
    response = await client.post("/auth/login", data={
        "username": "login@test.com",
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()