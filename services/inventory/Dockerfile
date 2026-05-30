# ---- Estágio 1: build das dependências ----
FROM python:3.12-slim AS builder

WORKDIR /install

# Evita .pyc e usa stdout sem buffer (logs em tempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
# Instala as dependências em um prefixo isolado, copiado depois.
RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt

# ---- Estágio 2: imagem final enxuta ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/deps/bin:$PATH \
    PYTHONPATH=/deps/lib/python3.12/site-packages

# Cria usuário não-root (boa prática de segurança)
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app

# Copia apenas as dependências já compiladas e o código
COPY --from=builder /install/deps /deps
COPY app/ ./app/

USER appuser

EXPOSE 8000

# Healthcheck a nível de imagem (complementa os probes do K8s)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health/live').status==200 else 1)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
