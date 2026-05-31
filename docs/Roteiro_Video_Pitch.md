# Roteiro do Vídeo Pitch — Pedidos Veloz (até 4 min)

> **Como gravar:** Abre o VS Code com a pasta do projeto e o navegador com o GitHub.
> Vai alternando entre as duas janelas enquanto fala. Use o gravador do Windows: `Win + G`.
> Fale com calma — você não precisa ler palavra por palavra, use como guia.
> Publique no YouTube (pode ser **não listado**) e cole o link no README e nos PDFs.

---

### 0:00 – 0:30 — Abertura
**O que mostrar na tela:** Abre o [README.md](../README.md) no VS Code ou no GitHub.

> "Olá! Sou Bruno e esse aqui é o **Pedidos Veloz** — um projeto que criei como
> solução Cloud DevOps para uma empresa chamada Loja Veloz.
> O problema deles era que toda vez que iam atualizar o sistema, o site ficava fora do ar.
> Quando tinha muito acesso, o sistema não aguentava. E quando algo dava errado,
> ninguém sabia onde estava o problema. Então eu montei uma solução do zero pra resolver
> isso tudo, e vou mostrar como ficou."

---

### 0:30 – 1:10 — Arquitetura
**O que mostrar na tela:** Abre a pasta [services/](../services/) no VS Code.

> "A primeira coisa que fiz foi dividir o sistema em partes menores — os chamados
> microsserviços. Ao invés de uma aplicação enorme e difícil de mexer, ficamos com
> quatro serviços independentes: um **Gateway**, que é a porta de entrada do sistema;
> o serviço de **Pedidos**, que é o coração da aplicação;
> o serviço de **Pagamentos**; e o de **Estoque**.
> Cada um tem sua própria pasta aqui. Todos foram feitos em Python."

---

### 1:10 – 1:55 — Containers e ambiente local
**O que mostrar na tela:** Abre o [docker-compose.yml](../docker-compose.yml) e depois o [services/orders/Dockerfile](../services/orders/Dockerfile).

> "Pra garantir que o projeto funciona igual na máquina de todo mundo,
> eu usei o **Docker**. Com um único comando — `docker compose up` —
> todos os quatro serviços sobem juntos automaticamente.
> Esse arquivo aqui, o docker-compose.yml, é quem organiza tudo isso:
> define os serviços, as redes entre eles e onde os dados ficam salvos.
> E cada serviço tem o seu próprio Dockerfile — olha aqui —
> que é basicamente a receita pra montar o serviço.
> Por segurança, nenhum deles roda como administrador da máquina."

---

### 1:55 – 2:35 — Kubernetes
**O que mostrar na tela:** Abre a pasta [k8s/](../k8s/) e vai clicando nos arquivos `.yaml`.

> "Pra produção — onde o sistema vai rodar de verdade —
> eu usei o **Kubernetes**, que é basicamente um gerenciador de servidores.
> Esses arquivos aqui configuram tudo: quantas cópias de cada serviço rodam,
> como elas se comunicam, onde ficam as senhas e configurações.
> O legal é que configurei o sistema pra verificar se cada serviço está saudável
> antes de mandar requisição pra ele — isso resolve o problema de queda durante
> as atualizações, que era a dor principal da empresa."

---

### 2:35 – 3:10 — CI/CD
**O que mostrar na tela:** Abre o [.github/workflows/ci-cd.yml](../.github/workflows/ci-cd.yml).

> "Aqui é onde automatizei a parte de publicar novas versões do sistema.
> Esse arquivo é o pipeline — sempre que alguém sobe uma alteração no código,
> ele dispara automaticamente: roda os testes, verifica se tem falha de segurança,
> empacota a aplicação e publica. Tudo isso sem ninguém precisar fazer nada manualmente.
> Se algum teste falhar, a publicação trava ali mesmo — nada quebrado vai pra produção."

---

### 3:10 – 3:50 — Observabilidade, deploy e escala
**O que mostrar na tela:** Abre a pasta [observability/](../observability/).

> "O terceiro problema da empresa era não saber onde estava a falha quando algo dava errado.
> Pra isso, adicionei monitoramento em todos os serviços: métricas de desempenho,
> logs organizados e rastreamento — que permite ver o caminho completo de um pedido,
> desde a entrada até o banco de dados.
> Sobre escala: o sistema aumenta o número de cópias automaticamente quando o acesso cresce,
> e diminui quando acalma. Então pra aquele pico de campanha que a empresa temia,
> o sistema se adapta sozinho."

---

### 3:50 – 4:00 — Fechamento
**O que mostrar na tela:** Volta pro [README.md](../README.md).

> "Resumindo: o sistema agora atualiza sem cair, escala quando precisa,
> e quando algo dá errado, dá pra saber exatamente onde.
> Esse é o Pedidos Veloz. Obrigado!"

---

## Checklist antes de gravar
- [ ] VS Code aberto com a pasta do projeto
- [ ] Navegador aberto no repositório do GitHub
- [ ] Gravador ligado: `Win + G` e clica no botão de gravar
- [ ] Ensaia uma vez cronometrando — tente ficar entre 3:30 e 4:00 min
- [ ] Fala com calma, pode pausar entre as seções
