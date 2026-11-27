import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def clear_items():
    main._items.clear()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_get_item():
    r = client.post("/items", json={"name": "Caneta", "price": 2.5})
    assert r.status_code == 201
    item = r.json()
    assert item == {"id": 1, "name": "Caneta", "price": 2.5}

    r = client.get(f"/items/{item['id']}")
    assert r.status_code == 200
    assert r.json() == item


def test_list_items():
    client.post("/items", json={"name": "A", "price": 1})
    client.post("/items", json={"name": "B", "price": 2})
    r = client.get("/items")
    assert r.status_code == 200
    assert [i["name"] for i in r.json()] == ["A", "B"]


def test_get_missing_item_returns_404():
    r = client.get("/items/999")
    assert r.status_code == 404


def test_create_item_invalid_payload_returns_422():
    r = client.post("/items", json={"name": "Sem preço"})
    assert r.status_code == 422
