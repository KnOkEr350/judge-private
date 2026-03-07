import httpx
import os
import time
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")


def wait_for_server(timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(f"{BASE_URL}/ping", timeout=2)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Сервер не поднялся за отведённое время")


@pytest.fixture(scope="session", autouse=True)
def server_ready():
    wait_for_server()


@pytest.fixture(autouse=True)
def reset_state():
    response = httpx.get(f"{BASE_URL}/items")
    if response.status_code == 200:
        for item in response.json():
            httpx.delete(f"{BASE_URL}/items/{item['id']}")
    yield


def test_create_item_returns_201():
    r = httpx.post(f"{BASE_URL}/items", json={"name": "apple", "description": "a fruit"})
    assert r.status_code == 201


def test_create_item_returns_id_and_fields():
    r = httpx.post(f"{BASE_URL}/items", json={"name": "apple", "description": "a fruit"})
    data = r.json()
    assert "id" in data
    assert data["name"] == "apple"
    assert data["description"] == "a fruit"


def test_create_item_without_description():
    r = httpx.post(f"{BASE_URL}/items", json={"name": "banana"})
    assert r.status_code == 201
    assert r.json()["name"] == "banana"


def test_create_multiple_items_have_unique_ids():
    r1 = httpx.post(f"{BASE_URL}/items", json={"name": "item1"})
    r2 = httpx.post(f"{BASE_URL}/items", json={"name": "item2"})
    assert r1.json()["id"] != r2.json()["id"]



def test_get_all_items_empty():
    r = httpx.get(f"{BASE_URL}/items")
    assert r.status_code == 200
    assert r.json() == []


def test_get_all_items_returns_all_created():
    httpx.post(f"{BASE_URL}/items", json={"name": "apple"})
    httpx.post(f"{BASE_URL}/items", json={"name": "orange"})
    r = httpx.get(f"{BASE_URL}/items")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_item_by_id():
    created = httpx.post(f"{BASE_URL}/items", json={"name": "apple", "description": "fruit"}).json()
    r = httpx.get(f"{BASE_URL}/items/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "apple"


def test_get_item_not_found():
    r = httpx.get(f"{BASE_URL}/items/99999")
    assert r.status_code == 404


def test_update_item():
    created = httpx.post(f"{BASE_URL}/items", json={"name": "apple"}).json()
    r = httpx.put(f"{BASE_URL}/items/{created['id']}", json={"name": "green apple"})
    assert r.status_code == 200
    assert r.json()["name"] == "green apple"


def test_update_item_not_found():
    r = httpx.put(f"{BASE_URL}/items/99999", json={"name": "ghost"})
    assert r.status_code == 404


# --- DELETE ---

def test_delete_item():
    created = httpx.post(f"{BASE_URL}/items", json={"name": "apple"}).json()
    r = httpx.delete(f"{BASE_URL}/items/{created['id']}")
    assert r.status_code == 200


def test_delete_item_not_found():
    r = httpx.delete(f"{BASE_URL}/items/99999")
    assert r.status_code == 404


def test_delete_item_actually_removes_it():
    created = httpx.post(f"{BASE_URL}/items", json={"name": "apple"}).json()
    httpx.delete(f"{BASE_URL}/items/{created['id']}")
    r = httpx.get(f"{BASE_URL}/items/{created['id']}")
    assert r.status_code == 404

def test_weather_returns_200():
    r = httpx.get(f"{BASE_URL}/weather", params={"city": "Moscow"}, timeout=30)
    assert r.status_code == 200


def test_weather_returns_city_and_temperature():
    r = httpx.get(f"{BASE_URL}/weather", params={"city": "Moscow"}, timeout=30)
    data = r.json()
    assert "city" in data
    assert "temperature" in data


def test_weather_temperature_is_number():
    r = httpx.get(f"{BASE_URL}/weather", params={"city": "London"}, timeout=30)
    data = r.json()
    assert isinstance(data["temperature"], (int, float))


def test_weather_city_not_found():
    r = httpx.get(f"{BASE_URL}/weather", params={"city": "DefinitelyNotARealCity12345"}, timeout=30)
    assert r.status_code == 404


def test_weather_saves_to_db_and_updates():
    r1 = httpx.get(f"{BASE_URL}/weather", params={"city": "Paris"}, timeout=30)
    assert r1.status_code == 200
    r2 = httpx.get(f"{BASE_URL}/weather", params={"city": "Paris"}, timeout=30)
    assert r2.status_code == 200
    assert r2.json()["city"] == r1.json()["city"]

def test_weather_cache_returns_same_result():
    r1 = httpx.get(f"{BASE_URL}/weather", params={"city": "Berlin"}, timeout=30)
    assert r1.status_code == 200
    r2 = httpx.get(f"{BASE_URL}/weather", params={"city": "Berlin"}, timeout=30)
    assert r2.status_code == 200
    assert r2.json() == r1.json()