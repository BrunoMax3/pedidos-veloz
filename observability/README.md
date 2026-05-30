# Observabilidade — Pedidos Veloz

Três pilares cobertos:

- **Métricas** (Prometheus): cada serviço expõe `/metrics` no formato Prometheus
  (contadores de pedidos, cobranças, requisições no gateway, nível de estoque).
  O `prometheus.yml` faz o scrape; em K8s o scrape é automático via annotations.
- **Logs** (stream estruturado): todos os serviços emitem logs em JSON para
  stdout (12-Factor). Em produção, um agente (Fluent Bit/Loki) agrega e indexa.
- **Traces** (OpenTelemetry): instrumentação OTLP enviando spans ao
  OpenTelemetry Collector, que exporta para Jaeger/Tempo. Permite seguir uma
  requisição `gateway -> orders -> inventory -> payments` ponta a ponta.

## Instrumentar tracing nos serviços (exemplo, orders)
```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp \
            opentelemetry-instrumentation-fastapi
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
export OTEL_SERVICE_NAME=orders
opentelemetry-instrument uvicorn app.main:app --host 0.0.0.0 --port 8000
```
A auto-instrumentação propaga o `trace_id` entre os serviços via headers HTTP.
