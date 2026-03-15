import pytest
import httpx
import os
import time

BASE_URL = os.getenv("BASE_URL", "http://student-app:8080")

@pytest.mark.asyncio
async def test_ping():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/ping")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_external_weather_integration():
    params = {"lat": 55.75, "lon": 37.61}

    async with httpx.AsyncClient() as client:
        start_time = time.time()
        res1 = await client.get(f"{BASE_URL}/weather/external", params=params)
        duration1 = time.time() - start_time

        assert res1.status_code == 200
        data = res1.json()
        assert "current_weather" in data

        start_time = time.time()
        res2 = await client.get(f"{BASE_URL}/weather/external", params=params)
        duration2 = time.time() - start_time

        assert res2.status_code == 200
        assert duration2 < duration1, "Redis caching is not working!"


@pytest.mark.asyncio
async def test_history_in_db():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather/history")
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)
        assert len(history) > 0
        assert "city" in history[0] or "lat" in history[0]