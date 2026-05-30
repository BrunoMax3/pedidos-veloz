from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_live():
    assert client.get("/health/live").status_code == 200


def test_reserve_ok():
    r = client.post("/reserve", json={"item_sku": "SKU-TEST", "quantity": 5})
    assert r.status_code == 200
    assert r.json()["remaining"] == 95


def test_reserve_insufficient():
    r = client.post("/reserve", json={"item_sku": "SKU-LOW", "quantity": 99999})
    assert r.status_code == 409


def test_reserve_invalid_quantity():
    r = client.post("/reserve", json={"item_sku": "SKU-X", "quantity": 0})
    assert r.status_code == 422  # validação Pydantic
