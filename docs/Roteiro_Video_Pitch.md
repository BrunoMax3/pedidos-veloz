# Roteiro do Vídeo Pitch — Pedidos Veloz (até 4 min)

> Dica: grave a tela mostrando o repositório, o `docker compose up` rodando e os
> manifests. Fale com naturalidade — o texto abaixo é guia, não para ler robótico.
> Publique no YouTube (pode ser **não listado**) e cole o link no README e nos PDFs.

---

### 0:00 – 0:30 — Abertura e problema
**Tela:** README aberto / título do projeto.

> "Olá! Sou [seu nome] e este é o **Pedidos Veloz**, a proposta Cloud DevOps para a
> Loja Veloz. A empresa cresceu rápido e passou a sofrer com três dores:
> indisponibilidade durante os deploys, dificuldade de escalar nos picos e pouca
> rastreabilidade de falhas entre serviços. Vou mostrar como resolvi isso ponta a
> ponta — do desenvolvimento local até a produção."

### 0:30 – 1:10 — Arquitetura
**Tela:** diagrama no README / pasta `services/`.

> "A aplicação foi quebrada em quatro microsserviços: um **API Gateway** como única
> porta de entrada, o serviço de **Pedidos**, que orquestra o fluxo, e os serviços de
> **Estoque** e **Pagamentos**. Os pedidos são persistidos no **PostgreSQL** e cada
> pedido criado dispara um evento **‘PedidoCriado’** numa fila RabbitMQ, desacoplando
> os efeitos colaterais. Tudo em Python com FastAPI."

### 1:10 – 1:55 — Containers e ambiente local
**Tela:** Dockerfile + terminal com `docker compose up --build` e um `curl`.

> "No ambiente local, toda a stack sobe com **um único comando**: `docker compose up`.
> Cada serviço tem um Dockerfile **multi-stage**, gerando imagens enxutas e rodando
> com **usuário não-root** por segurança. Repare: faço um POST no gateway e o pedido
> percorre estoque, pagamento e banco, retornando o status. Reproduzível em qualquer
> máquina."

### 1:55 – 2:35 — Kubernetes (produção)
**Tela:** pasta `k8s/` e trechos dos manifests.

> "Para produção, levei para o **Kubernetes**. Cada serviço tem Deployment e Service;
> configuração em **ConfigMap** e credenciais em **Secret**. Apliquei **probes de
> liveness e readiness** — o que elimina a queda durante o deploy, porque o tráfego só
> vai para réplicas prontas. Em segurança: **Pod Security restricted**, root filesystem
> somente leitura, capabilities removidas e **NetworkPolicy default-deny**."

### 2:35 – 3:10 — CI/CD
**Tela:** `.github/workflows/ci-cd.yml`.

> "A entrega é automatizada com **GitHub Actions**. A cada push, o pipeline roda
> **lint e testes** nos quatro serviços, faz o **build**, executa um **scan de
> vulnerabilidades com Trivy** e **publica as imagens versionadas** no registry. Os
> segredos são gerenciados pelo próprio GitHub — nada de credencial no código. Se um
> teste falha, nada vai para produção."

### 3:10 – 3:50 — Observabilidade, deploy e escala
**Tela:** endpoint `/metrics` e `observability/`.

> "Por fim, **observabilidade** desde o MVP: **métricas** Prometheus em todos os
> serviços, **logs** estruturados em JSON e **tracing distribuído** com OpenTelemetry,
> seguindo a requisição entre os serviços. A estratégia de deploy é **Rolling Update**,
> evoluindo para **Canary** no serviço de Pedidos. E a escala é automática via **HPA**:
> de 3 a 15 réplicas conforme a CPU — pronto para o pico da campanha."

### 3:50 – 4:00 — Fechamento
**Tela:** README / diagrama.

> "Resumindo: deploys sem queda, escala sob demanda, entrega automatizada e
> rastreabilidade total. Esse é o **Pedidos Veloz**. Obrigado!"

---

## Checklist de gravação
- [ ] Mostrar `docker compose up` realmente funcionando (ou um print/gif se faltar tempo).
- [ ] Mostrar pelo menos um `curl` criando um pedido.
- [ ] Passar o olho pelos manifests do `k8s/` e pelo workflow do CI/CD.
- [ ] Mostrar um `/metrics` respondendo.
- [ ] Não passar de 4 minutos — ensaie uma vez cronometrando.
