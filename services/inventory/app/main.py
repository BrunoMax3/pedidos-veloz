"""Serviço de Estoque (Inventory) - Pedidos Veloz.

Reserva e dá baixa em itens. Para o MVP o estoque é mantido em memória
(processo stateless do ponto de vista de configuração; o estado real iria
para Redis/Postgres em produção - decisão documentada no relatório).
"""
import logging
import os
import sys
import threading

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field

SERVICE_NAME = os.getenv("SERVICE_NAME", "inventory")
INITIAL_STOCK = int(os.getenv("INITIAL_STOCK", "100"))

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='{"service":"%s","level":"%%(levelname)s","msg":"%%(message)s"}' % SERVICE_NAME)
logger = logging.getLogger(SERVICE_NAME)

_lock = threading.Lock()
_stock: dict[str, int] = {}

STOCK_GAUGE = Gauge("inventory_stock_level", "Nível de estoque por SKU", ["sku"])

app = FastAPI(title="Serviço de Estoque - Pedidos Veloz")


class ReserveRequest(BaseModel):
    item_sku: str
    quantity: int = Field(..., gt=0)


@app.get("/health/live", response_class=PlainTextResponse)
def live():
    return "OK"


@app.get("/health/ready", response_class=PlainTextResponse)
def ready():
    return "READY"


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/reserve")
def reserve(req: ReserveRequest):
    with _lock:
        current = _stock.get(req.item_sku, INITIAL_STOCK)
        if current < req.quantity:
            logger.info(f"Estoque insuficiente para {req.item_sku}")
            return PlainTextResponse("INSUFFICIENT", status_code=409)
        _stock[req.item_sku] = current - req.quantity
        STOCK_GAUGE.labels(sku=req.item_sku).set(_stock[req.item_sku])
    logger.info(f"Reservado {req.quantity} de {req.item_sku}")
    return {"item_sku": req.item_sku, "remaining": _stock[req.item_sku]}


@app.get("/stock/{sku}")
def stock(sku: str):
    return {"item_sku": sku, "quantity": _stock.get(sku, INITIAL_STOCK)}
