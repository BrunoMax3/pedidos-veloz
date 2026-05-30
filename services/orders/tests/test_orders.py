from fastapi.testclient import TestClient
import app.main as m

# Evita inicializar o banco no startup durante o teste unitário
m.app.router.lifespan_context = None
client = TestClient(m.app, raise_server_exceptions=False)


def test_health_live():
    assert client.get("/health/live").status_code == 200


def test_metrics_exposed():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "orders_created_total" in r.text


def test_create_order_validation():
    r = client.post("/orders", json={"customer_id": "c", "item_sku": "s",
                                      "quantity": 0, "amount": 10})
    assert r.status_code == 422
