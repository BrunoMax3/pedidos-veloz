"""Gera o Relatório Técnico - Parte Prática em PDF."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, ListFlowable, ListItem, Preformatted,
                                Table, TableStyle)
from report_style import build_styles, header_band, data_table, footer, CODEBG

S = build_styles()


def P(t, s="body"):
    return Paragraph(t, S[s])


def bullets(items):
    return ListFlowable(
        [ListItem(P(i, "bullet"), leftIndent=10, value="•") for i in items],
        bulletType="bullet", start="•", leftIndent=8)


def code(text):
    """Bloco de código com fundo, preservando quebras de linha."""
    pre = Preformatted(text.strip("\n"), S["code"])
    t = Table([[pre]], colWidths=[16.8 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODEBG),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBEFORE", (0, 0), (0, -1), 2, colors.HexColor("#1B998B")),
    ]))
    return t


story = []
story.append(header_band(
    "Relatório Técnico — Parte Prática",
    "Projeto &ldquo;Pedidos Veloz&rdquo; — implementação fim a fim",
    ["Caso: Loja Veloz &nbsp;|&nbsp; Stack: Python/FastAPI, Docker, Kubernetes, GitHub Actions",
     "Aluno: Bruno Maximino dos Reis",
     "Vídeo pitch: https://youtu.be/2fcHbnvvBjw"],
    S))
story.append(Spacer(1, 10))

# 1
story.append(P("1. Visão geral e arquitetura", "h1"))
story.append(P(
    "A solução implementa a plataforma &ldquo;Pedidos Veloz&rdquo; como quatro microsserviços de "
    "domínio, um banco PostgreSQL e mensageria RabbitMQ. O <b>API Gateway</b> é o único "
    "ponto de entrada HTTP; ele encaminha as requisições ao serviço de <b>Pedidos</b>, "
    "que orquestra a reserva no <b>Estoque</b>, a cobrança no serviço de <b>Pagamentos</b> "
    "(integração externa simulada), persiste o pedido e publica o evento assíncrono "
    "<b>&ldquo;PedidoCriado&rdquo;</b> na fila."))
story.append(code(
    "Cliente ──▶ API Gateway ──▶ Orders ──┬──▶ Inventory\n"
    "                                      ├──▶ Payments (gateway externo)\n"
    "                                      ├──▶ PostgreSQL  (persistência)\n"
    "                                      └──▶ RabbitMQ    (evento PedidoCriado)"))
story.append(data_table([
    ["Serviço", "Responsabilidade", "Porta / Exposição"],
    ["api-gateway", "Entrada HTTP e roteamento", "8080 (externo)"],
    ["orders", "Cria/consulta pedidos, orquestra, emite evento", "interno"],
    ["payments", "Cobrança (integração externa simulada)", "interno"],
    ["inventory", "Reserva e baixa de estoque", "interno"],
    ["db / rabbitmq", "Persistência / mensageria de eventos", "interno"],
], S, col_widths=[3.0 * cm, 9.5 * cm, 4.3 * cm]))

# 2
story.append(P("2. Ambiente local com Docker Compose", "h1"))
story.append(P(
    "Toda a stack sobe com um único comando. O Compose define duas redes (<i>frontend</i> "
    "e <i>backend</i>, isolando o que é exposto do que é interno), um volume persistente "
    "para o banco, variáveis de ambiente por serviço e <i>healthchecks</i> com "
    "<i>depends_on</i> condicional — o serviço de Pedidos só inicia quando o banco e a "
    "fila estão saudáveis."))
story.append(code(
    "cp .env.example .env\n"
    "docker compose up --build      # sobe toda a stack\n\n"
    "curl -X POST http://localhost:8080/api/orders \\\n"
    "  -H 'Content-Type: application/json' \\\n"
    "  -d '{\"customer_id\":\"cli-1\",\"item_sku\":\"SKU-001\",\"quantity\":2,\"amount\":199.90}'"))

# 3
story.append(P("3. Conteinerização e versionamento", "h1"))
story.append(P(
    "Cada serviço tem um Dockerfile <b>multi-stage</b>: o primeiro estágio instala as "
    "dependências; o segundo copia apenas o necessário para uma imagem final enxuta. "
    "Boas práticas de segurança aplicadas: usuário <b>não-root</b>, redução de camadas, "
    "dependências mínimas (<i>python:3.12-slim</i>) e <i>healthcheck</i> na imagem. As "
    "imagens são versionadas no pipeline por <i>SHA</i> curto, <i>semver</i> (em tags) e "
    "<i>latest</i> no branch principal."))
story.append(code(
    "FROM python:3.12-slim AS builder\n"
    "COPY requirements.txt .\n"
    "RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt\n\n"
    "FROM python:3.12-slim\n"
    "RUN useradd --uid 10001 appuser\n"
    "COPY --from=builder /install/deps /deps\n"
    "COPY app/ ./app/\n"
    "USER appuser        # nunca executa como root\n"
    "CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]"))

# 4
story.append(P("4. Kubernetes — produção mínima", "h1"))
story.append(P(
    "Os manifests estão organizados por responsabilidade (namespace/config, banco, "
    "serviços, escala/rede). Cada serviço tem <b>Deployment</b> e <b>Service</b>; o "
    "PostgreSQL é um <b>StatefulSet</b> com volume persistente. A configuração não "
    "sensível vai em <b>ConfigMap</b>; credenciais (URL do banco, chave do gateway) em "
    "<b>Secret</b>, injetadas como variáveis de ambiente."))
story.append(P("Segurança aplicada e justificativa:", "h2"))
story.append(bullets([
    "<b>Pod Security Admission &ldquo;restricted&rdquo;</b> no namespace: bloqueia pods privilegiados "
    "e exige boas práticas por padrão — defesa na entrada do cluster.",
    "<b>securityContext</b>: <i>runAsNonRoot</i>, <i>readOnlyRootFilesystem</i>, "
    "<i>allowPrivilegeEscalation: false</i> e <i>drop ALL</i> de capabilities — reduz o "
    "impacto de um contêiner comprometido.",
    "<b>NetworkPolicy default-deny</b> de ingresso: só o tráfego explicitamente permitido "
    "trafega — segmentação de rede.",
    "<b>readiness/liveness probes</b>: o cluster reinicia processos travados e só envia "
    "tráfego a réplicas prontas, evitando indisponibilidade durante deploys.",
]))
story.append(P(
    "Cada serviço expõe <i>/health/live</i> e <i>/health/ready</i>; o readiness do serviço "
    "de Pedidos verifica a conexão com o banco, garantindo que réplicas sem banco não "
    "recebam requisições."))

# 5
story.append(P("5. CI/CD (GitHub Actions)", "h1"))
story.append(P(
    "O pipeline executa em duas fases. <b>(1) test</b>: em matriz para os quatro serviços, "
    "roda lint (ruff) e testes (pytest). <b>(2) build-and-push</b> (apenas em push para "
    "main/tags): faz o build da imagem, executa <b>scan de vulnerabilidades</b> com Trivy "
    "e publica no GitHub Container Registry. As credenciais usam o <i>GITHUB_TOKEN</i> "
    "gerenciado — nenhum segredo no código. O <i>gate</i> de testes impede que código "
    "quebrado seja publicado."))
story.append(data_table([
    ["Etapa", "Ferramenta", "Gate"],
    ["Lint", "ruff", "Informativo"],
    ["Testes", "pytest (14 testes)", "Bloqueante"],
    ["Build", "docker buildx", "Bloqueante"],
    ["Scan", "Trivy (CRITICAL/HIGH)", "Informativo no MVP"],
    ["Publicação", "GHCR + tags SHA/semver", "Só em main/tags"],
], S, col_widths=[3.8 * cm, 6.0 * cm, 7.0 * cm]))

# 6
story.append(P("6. Observabilidade", "h1"))
story.append(P(
    "Os três pilares estão contemplados. <b>Métricas</b>: todos os serviços expõem "
    "<i>/metrics</i> no formato Prometheus (pedidos criados, cobranças por resultado, "
    "requisições no gateway, nível de estoque). <b>Logs</b>: emitidos em JSON estruturado "
    "para stdout (12-Factor), prontos para agregação por Loki/Fluent Bit. <b>Traces</b>: "
    "instrumentação OpenTelemetry (OTLP) enviando spans a um Collector que exporta para "
    "Jaeger/Tempo, permitindo seguir uma requisição <i>gateway → orders → inventory → "
    "payments</i> ponta a ponta, com o <i>trace_id</i> propagado entre os serviços."))
story.append(code(
    "export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317\n"
    "export OTEL_SERVICE_NAME=orders\n"
    "opentelemetry-instrument uvicorn app.main:app --host 0.0.0.0 --port 8000"))

# 7
story.append(P("7. Estratégia de deploy", "h1"))
story.append(P(
    "Adotamos <b>Rolling Update</b> como padrão (nativo do Deployment): novas réplicas "
    "sobem e passam pelo readiness antes que as antigas sejam removidas, garantindo "
    "indisponibilidade zero — a dor relatada de &ldquo;quedas durante deploys&rdquo;. Para o serviço "
    "de <b>Pedidos</b>, no caminho crítico da campanha, recomendamos evoluir para "
    "<b>Canary</b>: liberar a nova versão para uma fração do tráfego, observar métricas e "
    "erros e só então promover. O <b>Blue-Green</b> foi considerado, mas exige o dobro de "
    "recursos em paralelo; o Canary oferece rollback igualmente rápido com custo menor — "
    "daí a escolha."))

# 8
story.append(P("8. Escalabilidade", "h1"))
story.append(P(
    "Usamos <b>HPA (Horizontal Pod Autoscaler)</b> por utilização de CPU nos serviços do "
    "caminho crítico: <i>orders</i> (3→15 réplicas, alvo 65%) e <i>api-gateway</i> (2→10, "
    "alvo 70%). A política de <i>behavior</i> sobe rápido (janela de 30s) e desce devagar "
    "(300s), evitando oscilação. O <b>HPA</b> foi preferido ao <b>VPA</b> porque o gargalo "
    "esperado em campanha é volume de requisições concorrentes — resolvido somando "
    "réplicas, não engordando uma só. O VPA fica como recomendação futura para ajuste "
    "fino de <i>requests/limits</i> de serviços de carga estável (ex.: o banco), pois "
    "ambos não devem atuar sobre a mesma métrica simultaneamente."))
story.append(code(
    "minReplicas: 3\n"
    "maxReplicas: 15\n"
    "metrics:\n"
    "  - type: Resource\n"
    "    resource: { name: cpu, target: { type: Utilization, averageUtilization: 65 } }"))

# 9
story.append(P("9. Infraestrutura como Código (Terraform)", "h1"))
story.append(P(
    "Um esqueleto Terraform provisiona o cluster Kubernetes gerenciado de forma "
    "<b>reproduzível e versionada</b>: providers com versão travada, variáveis por "
    "ambiente, sugestão de <i>state</i> remoto com lock e um <i>node pool</i> com "
    "autoscaling alinhado ao HPA. A justificativa do esqueleto é demonstrar a abordagem "
    "de IaC dentro do prazo de quatro semanas; a evolução natural é modularizar (network, "
    "cluster, node_pool) e separar <i>workspaces</i> por ambiente."))

# 10
story.append(P("10. Reprodução e conclusão", "h1"))
story.append(P(
    "O repositório traz README com instruções completas: subir local com "
    "<i>docker compose up --build</i>, rodar os 14 testes e aplicar os manifests no "
    "Kubernetes. A proposta endereça diretamente as dores da Loja Veloz: o "
    "<b>Rolling/Canary</b> elimina quedas no deploy; o <b>HPA</b> dá escala sob demanda no "
    "pico; o <b>CI/CD com testes e scan</b> reduz o tempo e o risco de entrega; e a "
    "<b>observabilidade</b> (métricas, logs e tracing) ataca a baixa rastreabilidade de "
    "falhas entre serviços. O resultado é um caminho claro e automatizado do "
    "desenvolvimento à produção."))


def build():
    doc = BaseDocTemplate(
        r"c:\Users\bruno\Desktop\pedidos-veloz\docs\Relatorio_Pratico.pdf",
        pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.6 * cm, bottomMargin=1.8 * cm,
        title="Relatório Técnico - Parte Prática - Pedidos Veloz")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    doc.build(story)
    print("Relatorio_Pratico.pdf gerado")


if __name__ == "__main__":
    build()