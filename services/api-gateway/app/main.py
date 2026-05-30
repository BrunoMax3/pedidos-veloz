"""API Gateway (HTTP) - Pedidos Veloz.

Único ponto de entrada HTTP exposto ao mundo externo. Encaminha requisições
para os serviços internos (orders/inventory) e centraliza o roteamento.
Em produção fica atrás de um Ingress/Service Mesh.
"""
import os
import sys
import logging

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field

SERVICE_NAME = os.getenv("SERVICE_NAME", "api-gateway")
ORDERS_URL = os.getenv("ORDERS_URL", "http://orders:8000")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory:8000")

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='{"service":"%s","level":"%%(levelname)s","msg":"%%(message)s"}' % SERVICE_NAME)
logger = logging.getLogger(SERVICE_NAME)

REQUESTS = Counter("gateway_requests_total", "Requisições no gateway", ["route"])

app = FastAPI(title="API Gateway - Pedidos Veloz")


class OrderRequest(BaseModel):
    customer_id: str
    item_sku: str
    quantity: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)


@app.get("/health/live", response_class=PlainTextResponse)
def live():
    return "OK"


@app.get("/health/ready", response_class=PlainTextResponse)
def ready():
    return "READY"


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/orders", status_code=201)
def create_order(req: OrderRequest):
    REQUESTS.labels(route="create_order").inc()
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(f"{ORDERS_URL}/orders", json=req.model_dump())
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"orders indisponível: {exc}")
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()


@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    REQUESTS.labels(route="get_order").inc()
    with httpx.Client(timeout=10.0) as client:
        r = client.get(f"{ORDERS_URL}/orders/{order_id}")
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()


@app.get("/api/stock/{sku}")
def get_stock(sku: str):
    REQUESTS.labels(route="get_stock").inc()
    with httpx.Client(timeout=10.0) as client:
        r = client.get(f"{INVENTORY_URL}/stock/{sku}")
    return r.json()
