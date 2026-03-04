import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    response = client.get("/items")
    if response.status_code == 200:
        for item in response.json():
            client.delete(f"/items/{item['id']}")
    yield


def test_create_item_returns_201():
    r = client.post("/items", json={"name": "apple", "description": "a fruit"})
    assert r.status_code == 201


def test_create_item_returns_id_and_fields():
    r = client.post("/items", json={"name": "apple", "description": "a fruit"})
    data = r.json()
    assert "id" in data
    assert data["name"] == "apple"
    assert data["description"] == "a fruit"


def test_create_item_without_description():
    r = client.post("/items", json={"name": "banana"})
    assert r.status_code == 201
    assert r.json()["name"] == "banana"


def test_create_multiple_items_have_unique_ids():
    r1 = client.post("/items", json={"name": "item1"})
    r2 = client.post("/items", json={"name": "item2"})
    assert r1.json()["id"] != r2.json()["id"]




def test_get_all_items_empty():
    r = client.get("/items")
    assert r.status_code == 200
    assert r.json() == []


def test_get_all_items_returns_all_created():
    client.post("/items", json={"name": "apple"})
    client.post("/items", json={"name": "orange"})
    r = client.get("/items")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_item_by_id():
    created = client.post("/items", json={"name": "apple", "description": "fruit"}).json()
    r = client.get(f"/items/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "apple"


def test_get_item_not_found():
    r = client.get("/items/99999")
    assert r.status_code == 404




def test_update_item():
    created = client.post("/items", json={"name": "apple"}).json()
    r = client.put(f"/items/{created['id']}", json={"name": "green apple"})
    assert r.status_code == 200
    assert r.json()["name"] == "green apple"


def test_update_item_partial_keeps_other_fields():
    created = client.post("/items", json={"name": "apple", "description": "old"}).json()
    r = client.put(f"/items/{created['id']}", json={"description": "new"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "apple"
    assert data["description"] == "new"


def test_update_item_not_found():
    r = client.put("/items/99999", json={"name": "ghost"})
    assert r.status_code == 404


def test_delete_item_returns_200():
    created = client.post("/items", json={"name": "apple"}).json()
    r = client.delete(f"/items/{created['id']}")
    assert r.status_code == 200


def test_delete_item_actually_removes_it():
    created = client.post("/items", json={"name": "apple"}).json()
    client.delete(f"/items/{created['id']}")
    r = client.get(f"/items/{created['id']}")
    assert r.status_code == 404


def test_delete_item_not_found():
    r = client.delete("/items/99999")
    assert r.status_code == 404