import pytest
import httpx
import os

BASE_URL = os.getenv("BASE_URL", "http://student-app:8080")

@pytest.mark.asyncio
async def test_ping():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/ping")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_crud_flow():
    payload = {"city": "Moscow", "temperature": 25.5, "condition": "Sunny"}
    async with httpx.AsyncClient() as client:
        post_res = await client.post(f"{BASE_URL}/weather", json=payload)
        assert post_res.status_code in [200, 201]
        get_res = await client.get(f"{BASE_URL}/weather/Moscow")
        assert get_res.status_code == 200
        data = get_res.json()
        assert data["city"] == "Moscow"
        assert data["temperature"] == 25.5

@pytest.mark.asyncio
async def test_not_found():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather/UnknownCity")
        assert response.status_code == 404