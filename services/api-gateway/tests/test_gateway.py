from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_ready():
    assert client.get("/health/ready").status_code == 200


def test_metrics_exposed():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "gateway_requests_total" in r.text


def test_create_order_validation():
    # quantity inválida -> 422 antes de qualquer chamada externa
    r = client.post("/api/orders", json={"customer_id": "c", "item_sku": "s",
                                         "quantity": -1, "amount": 10})
    assert r.status_code == 422
