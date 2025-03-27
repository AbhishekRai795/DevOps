import pytest
from httpx import AsyncClient
from apiserver import app

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/login", params={"username": "admin", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_failure():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/login", params={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_add_numbers():
    async with AsyncClient(app=app, base_url="http://test") as client:
        data = {"num1": 5, "num2": 7}
        response = await client.post("/add/", json=data)
    assert response.status_code == 200
    assert response.json()["sum"] == 12

@pytest.mark.asyncio
async def test_protected_route():
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/login", params={"username": "admin", "password": "password"})
        access_token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/protected", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "You are authorized"
