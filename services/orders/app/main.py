"""Serviço de Pedidos (Orders) - Pedidos Veloz.

Responsável por criar e consultar pedidos. Ao criar um pedido:
  1. Reserva estoque no Serviço de Estoque (chamada síncrona).
  2. Solicita o pagamento ao Serviço de Pagamentos (chamada síncrona).
  3. Persiste o pedido no PostgreSQL.
  4. Publica o evento "PedidoCriado" na mensageria (RabbitMQ) de forma assíncrona.

Princípios 12-Factor aplicados: configuração via variáveis de ambiente,
processo stateless, logs como stream para stdout, port binding.
"""
import json
import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager

import httpx
import pika
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuração (12-Factor: config sempre por ambiente)
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://veloz:veloz@db:5432/pedidos")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory:8000")
PAYMENTS_URL = os.getenv("PAYMENTS_URL", "http://payments:8000")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
SERVICE_NAME = os.getenv("SERVICE_NAME", "orders")

# ---------------------------------------------------------------------------
# Logs estruturados em JSON (logs como stream - 12-Factor)
# ---------------------------------------------------------------------------
class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "msg": record.getMessage(),
        }
        if hasattr(record, "order_id"):
            payload["order_id"] = record.order_id
        return json.dumps(payload)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Métricas Prometheus
# ---------------------------------------------------------------------------
ORDERS_CREATED = Counter("orders_created_total", "Total de pedidos criados")
ORDER_LATENCY = Histogram("order_create_seconds", "Latência da criação de pedido")


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db(retries: int = 10):
    """Cria a tabela de pedidos com retry (o banco pode subir depois do serviço)."""
    for attempt in range(retries):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orders (
                        id UUID PRIMARY KEY,
                        customer_id TEXT NOT NULL,
                        item_sku TEXT NOT NULL,
                        quantity INT NOT NULL,
                        amount NUMERIC(10,2) NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT now()
                    );
                    """
                )
                conn.commit()
            logger.info("Banco inicializado")
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"DB indisponível (tentativa {attempt + 1}): {exc}")
            time.sleep(3)
    raise RuntimeError("Não foi possível conectar ao banco de dados")


def publish_event(event: dict):
    """Publica o evento PedidoCriado na fila. Falha de mensageria não derruba o pedido."""
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue="PedidoCriado", durable=True)
        channel.basic_publish(
            exchange="",
            routing_key="PedidoCriado",
            body=json.dumps(event),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
        logger.info("Evento PedidoCriado publicado")
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Falha ao publicar evento (degradação suave): {exc}")


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
class OrderRequest(BaseModel):
    customer_id: str = Field(..., examples=["cli-123"])
    item_sku: str = Field(..., examples=["SKU-001"])
    quantity: int = Field(..., gt=0, examples=[2])
    amount: float = Field(..., gt=0, examples=[199.90])


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Serviço de Pedidos - Pedidos Veloz", lifespan=lifespan)


@app.get("/health/live", response_class=PlainTextResponse)
def live():
    """Liveness: o processo está de pé."""
    return "OK"


@app.get("/health/ready", response_class=PlainTextResponse)
def ready():
    """Readiness: dependências (banco) estão acessíveis."""
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return "READY"
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=503, detail="DB indisponível")


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/orders", status_code=201)
@ORDER_LATENCY.time()
def create_order(req: OrderRequest):
    order_id = str(uuid.uuid4())
    logger.info("Criando pedido", extra={"order_id": order_id})

    # 1. Reserva de estoque (síncrono)
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.post(
                f"{INVENTORY_URL}/reserve",
                json={"item_sku": req.item_sku, "quantity": req.quantity},
            )
        if r.status_code != 200:
            raise HTTPException(status_code=409, detail="Estoque insuficiente")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Estoque indisponível: {exc}")

    # 2. Pagamento (síncrono, integração externa simulada)
    try:
        with httpx.Client(timeout=5.0) as client:
            p = client.post(
                f"{PAYMENTS_URL}/charge",
                json={"order_id": order_id, "amount": req.amount},
            )
        status = "PAGO" if p.status_code == 200 else "PAGAMENTO_RECUSADO"
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Pagamento indisponível: {exc}")

    # 3. Persistência
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO orders (id, customer_id, item_sku, quantity, amount, status)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (order_id, req.customer_id, req.item_sku, req.quantity, req.amount, status),
        )
        conn.commit()

    ORDERS_CREATED.inc()

    # 4. Evento assíncrono
    publish_event({"event": "PedidoCriado", "order_id": order_id, "status": status})

    return {"id": order_id, "status": status}


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return JSONResponse(content=json.loads(json.dumps(row, default=str)))
