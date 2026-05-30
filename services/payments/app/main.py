"""Serviço de Pagamentos (Payments) - Pedidos Veloz.

Simula a integração com um gateway de pagamento externo. Mantido stateless:
nenhuma informação sensível é persistida. Em produção, a credencial do gateway
viria de um Secret (ver k8s/secrets.yaml), nunca do código.
"""
import json
import logging
import os
import random
import sys
import time

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field

SERVICE_NAME = os.getenv("SERVICE_NAME", "payments")
# Credencial viria de Secret. Default só para ambiente local.
GATEWAY_API_KEY = os.getenv("PAYMENT_GATEWAY_KEY", "local-dev-key")
APPROVAL_RATE = float(os.getenv("APPROVAL_RATE", "0.9"))

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='{"service":"%s","level":"%%(levelname)s","msg":"%%(message)s"}' % SERVICE_NAME)
logger = logging.getLogger(SERVICE_NAME)

CHARGES = Counter("payment_charges_total", "Cobranças processadas", ["result"])

app = FastAPI(title="Serviço de Pagamentos - Pedidos Veloz")


class ChargeRequest(BaseModel):
    order_id: str
    amount: float = Field(..., gt=0)


@app.get("/health/live", response_class=PlainTextResponse)
def live():
    return "OK"


@app.get("/health/ready", response_class=PlainTextResponse)
def ready():
    # Readiness verifica se a credencial do gateway foi injetada.
    return "READY" if GATEWAY_API_KEY else PlainTextResponse("NO_KEY", status_code=503)


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/charge")
def charge(req: ChargeRequest):
    time.sleep(random.uniform(0.05, 0.2))  # latência simulada do gateway externo
    approved = random.random() < APPROVAL_RATE
    result = "approved" if approved else "declined"
    CHARGES.labels(result=result).inc()
    logger.info(f"Cobrança {req.order_id}: {result}")
    if not approved:
        return PlainTextResponse("DECLINED", status_code=402)
    return {"order_id": req.order_id, "result": "approved"}
