# Pedidos Veloz — Plataforma de Pedidos em Microsserviços

Solução fim a fim (do dev ao prod) para a **Loja Veloz**: ambiente local
reproduzível com Docker Compose, conteinerização segura, orquestração em
Kubernetes, pipeline de CI/CD, observabilidade e escalabilidade automática.

> 🎥 **Vídeo pitch (até 4 min):** [https://youtu.be/2fcHbnvvBjw](https://youtu.be/2fcHbnvvBjw)

---

## Arquitetura

```
                    ┌──────────────┐
   Cliente  ───────▶│  API Gateway │  (único ponto de entrada HTTP)
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    Orders    │──── publica evento "PedidoCriado" ──▶ RabbitMQ
                    └──┬────────┬──┘
                       │        │
              ┌────────▼┐    ┌──▼────────┐
              │Inventory│    │ Payments  │ (gateway externo simulado)
              └─────────┘    └───────────┘
                       │
                 ┌─────▼─────┐
                 │ PostgreSQL │
                 └───────────┘
```

| Serviço      | Responsabilidade                              | Stack            |
|--------------|-----------------------------------------------|------------------|
| api-gateway  | Entrada HTTP, roteamento                      | FastAPI          |
| orders       | Criar/consultar pedidos, orquestrar, eventos  | FastAPI + Postgres |
| payments     | Integração de pagamento (externa, simulada)   | FastAPI          |
| inventory    | Reserva e baixa de estoque                    | FastAPI          |
| db           | Persistência de pedidos                       | PostgreSQL 16    |
| rabbitmq     | Mensageria de eventos (`PedidoCriado`)        | RabbitMQ         |

---

## 1. Rodar localmente (Docker Compose)

Pré-requisitos: Docker + Docker Compose.

```bash
cp .env.example .env          # ajuste as variáveis se quiser
docker compose up --build     # sobe TODA a stack com um único comando
```

O gateway fica disponível em `http://localhost:8080`.

### Testar a API
```bash
# Criar um pedido
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"cli-123","item_sku":"SKU-001","quantity":2,"amount":199.90}'

# Consultar pedido
curl http://localhost:8080/api/orders/<ID_RETORNADO>

# Consultar estoque
curl http://localhost:8080/api/stock/SKU-001
```

Painel do RabbitMQ: `http://localhost:15672` (guest/guest).

---

## 2. Testes

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
for s in api-gateway orders payments inventory; do
  (cd services/$s && pip install -r requirements.txt && pytest -q)
done
```

---

## 3. Deploy no Kubernetes

Pré-requisitos: cluster (minikube/kind/GKE) + `kubectl` + métricas habilitadas
(`minikube addons enable metrics-server`).

```bash
# 1. Publique as imagens (ou deixe o CI fazer) e ajuste <REGISTRY> nos manifests
# 2. Aplique na ordem:
kubectl apply -f k8s/00-namespace-config.yaml
kubectl apply -f k8s/10-postgres.yaml
kubectl apply -f k8s/20-services.yaml
kubectl apply -f k8s/30-hpa-netpol.yaml

kubectl get pods -n pedidos-veloz
kubectl get hpa  -n pedidos-veloz
```

---

## 4. CI/CD (GitHub Actions)

`.github/workflows/ci-cd.yml` executa, a cada push:

1. **Lint + testes** (matriz para os 4 serviços)
2. **Build** das imagens
3. **Scan** de vulnerabilidades (Trivy)
4. **Publicação** no GitHub Container Registry (versionamento por SHA/semver)

Secrets do pipeline (`GITHUB_TOKEN`) são gerenciados pelo GitHub — nunca em código.

---

## 5. Observabilidade

- **Métricas:** `/metrics` (Prometheus) em todos os serviços.
- **Logs:** JSON estruturado em stdout (12-Factor).
- **Traces:** OpenTelemetry → Collector → Jaeger/Tempo.

Detalhes em [`observability/README.md`](observability/README.md).

---

## 6. Infraestrutura como Código

Esqueleto Terraform em [`infra/terraform/`](infra/terraform/) para provisionar o
cluster de forma reproduzível.

---

## Decisões e estratégias

- **Deploy:** Rolling Update (padrão), com Canary recomendado para o `orders`.
- **Escala:** HPA por CPU (orders 3→15, gateway 2→10).
- **Segurança:** usuário não-root, root FS somente leitura, `drop ALL` de
  capabilities, Pod Security Admission `restricted`, NetworkPolicy default-deny.

Veja os relatórios em [`docs/`](docs/) para a fundamentação completa.
