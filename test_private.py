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


# --- CREATE ---

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


# --- READ ---

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


# --- UPDATE ---

def test_update_item():
    created = httpx.post(f"{BASE_URL}/items", json={"name": "apple"}).json()
    r = httpx.put(f"{BASE_URL}/items/{created['id']}", json={"name": "green apple"})
    assert r.status_code == 200
    assert r.json()["name"] == "green apple"


def test_update_item_partial_keeps_other_fields():
    created = httpx.post(f"{BASE_URL}/items", json={"name": "apple", "description": "old"}).json()
    r = httpx.put(f"{BASE_URL}/items/{created['id']}", json={"description": "new"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "apple"
    assert data["description"] == "new"


def test_update_item_not_found():
    r = httpx.put(f"{BASE_URL}/items/99999", json={"name": "ghost"})
    assert r.status_code == 404


# --- DELETE ---

def test_delete_item_returns_200():
    created = httpx.post(f"{BASE_URL}/items", json={"name": "apple"}).json()
    r = httpx.delete(f"{BASE_URL}/items/{created['id']}")
    assert r.status_code == 200


def test_delete_item_actually_removes_it():
    created = httpx.post(f"{BASE_URL}/items", json={"name": "apple"}).json()
    httpx.delete(f"{BASE_URL}/items/{created['id']}")
    r = httpx.get(f"{BASE_URL}/items/{created['id']}")
    assert r.status_code == 404