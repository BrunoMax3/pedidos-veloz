from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_live():
    assert client.get("/health/live").status_code == 200


def test_metrics_exposed():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "payment_charges_total" in r.text


def test_charge_always_approved(monkeypatch):
    import app.main as m
    monkeypatch.setattr(m.random, "random", lambda: 0.0)  # < APPROVAL_RATE
    r = client.post("/charge", json={"order_id": "o-1", "amount": 10.0})
    assert r.status_code == 200
    assert r.json()["result"] == "approved"


def test_charge_declined(monkeypatch):
    import app.main as m
    monkeypatch.setattr(m.random, "random", lambda: 0.999)  # > APPROVAL_RATE
    r = client.post("/charge", json={"order_id": "o-2", "amount": 10.0})
    assert r.status_code == 402
