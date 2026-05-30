"""Gera o Relatório Teórico (Parte Teórica) em PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate,
                                Paragraph, Spacer, ListFlowable, ListItem)
from report_style import build_styles, header_band, data_table, footer

S = build_styles()


def P(t, s="body"):
    return Paragraph(t, S[s])


def bullets(items):
    return ListFlowable(
        [ListItem(P(i, "bullet"), leftIndent=10, value="•") for i in items],
        bulletType="bullet", start="•", leftIndent=8)


story = []
story.append(header_band(
    "Relatório Técnico — Parte Teórica",
    "Entrega contínua de uma plataforma de pedidos em microsserviços",
    ["Disciplina: Cloud DevOps Engineering &nbsp;|&nbsp; Caso: Loja Veloz — &ldquo;Pedidos Veloz&rdquo;",
     "Do Docker Compose ao Kubernetes com observabilidade e CI/CD",
     "Aluno: Bruno Maximino dos Reis"],
    S))
story.append(Spacer(1, 10))

# 1
story.append(P("1. Arquitetura de microsserviços e o papel do DevOps em cloud-native", "h1"))
story.append(P(
    "A arquitetura de microsserviços decompõe uma aplicação em serviços pequenos, "
    "independentes e organizados em torno de capacidades de negócio. Cada serviço "
    "tem seu próprio ciclo de vida, pode ser desenvolvido, implantado e escalado de "
    "forma autônoma e se comunica com os demais por interfaces bem definidas (HTTP/REST, "
    "gRPC ou mensageria assíncrona). O estilo se opõe ao monólito, em que todas as "
    "funcionalidades compartilham o mesmo processo e a mesma cadência de deploy — "
    "exatamente a dor relatada pela Loja Veloz, onde cada time sobe partes do sistema "
    "&ldquo;como dá&rdquo; e qualquer alteração coloca em risco todo o ambiente."))
story.append(P(
    "Os benefícios — autonomia de times, escalabilidade seletiva, isolamento de falhas e "
    "liberdade tecnológica — vêm acompanhados de custos: comunicação em rede, consistência "
    "distribuída e, sobretudo, complexidade operacional. É aí que entra o DevOps. Mais do "
    "que ferramentas, DevOps é uma cultura que aproxima desenvolvimento e operações por "
    "meio de automação, responsabilidade compartilhada e feedback rápido. Em um ambiente "
    "<b>cloud-native</b> — aplicações projetadas para nuvem, empacotadas em contêineres, "
    "orquestradas dinamicamente e operadas de forma elástica — o DevOps materializa-se em "
    "pipelines de entrega contínua, infraestrutura como código e telemetria abrangente. "
    "A metodologia <b>12-Factor App</b> formaliza esses princípios: configuração por "
    "ambiente, processos stateless, logs como streams, descartabilidade e paridade entre "
    "dev e produção."))

# 2
story.append(P("2. Conteinerização: Docker e Kubernetes — quando usar cada um", "h1"))
story.append(P(
    "<b>Conteinerização</b> é o empacotamento de uma aplicação com todas as suas "
    "dependências em uma unidade isolada e portátil, que executa de forma idêntica em "
    "qualquer ambiente. Contêineres compartilham o kernel do sistema operacional "
    "hospedeiro, o que os torna muito mais leves e rápidos que máquinas virtuais, sem o "
    "overhead de um SO completo por instância. Isso resolve o clássico &ldquo;na minha máquina "
    "funciona&rdquo;, garantindo paridade entre desenvolvimento e produção."))
story.append(P(
    "<b>Docker e Kubernetes operam em camadas diferentes</b> e são complementares, não "
    "concorrentes. O Docker é a plataforma de <i>construção e execução</i> de contêineres: "
    "a partir de um Dockerfile, gera-se uma imagem versionada e imutável. O Kubernetes é o "
    "<i>orquestrador</i>: gerencia o ciclo de vida de muitos contêineres em um cluster de "
    "máquinas, cuidando de agendamento, escala, autocorreção, rede e descoberta de serviços.&ldquo;, &rdquo;body"))
story.append(data_table([
    ["Aspecto", "Docker (+ Compose)", "Kubernetes"],
    ["Escopo", "Build e execução de contêineres em um host", "Orquestração em cluster de múltiplos nós"],
    ["Quando usar", "Desenvolvimento local, build de imagens, stacks simples", "Produção, alta disponibilidade, escala automática"],
    ["Recuperação de falha", "Manual / reinício básico", "Autocorreção, reagendamento, probes"],
    ["Escala", "Limitada ao host", "Horizontal automática (HPA) entre nós"],
], S, col_widths=[3.2 * cm, 6.6 * cm, 7.0 * cm]))
story.append(Spacer(1, 4))
story.append(P(
    "Na prática: usa-se <b>Docker Compose</b> para padronizar o ambiente local — subir "
    "toda a stack com um comando — e <b>Kubernetes</b> para produção, onde resiliência, "
    "escala sob demanda e governança são obrigatórias. Foi exatamente a divisão adotada "
    "neste projeto."))

# 3
story.append(P("3. Fundamentação teórica", "h1"))
story.append(P("3.1 Orquestração de contêineres", "h2"))
story.append(P(
    "Orquestração é a automação do agendamento, da implantação, da rede, do "
    "balanceamento de carga e do dimensionamento de contêineres em um conjunto de "
    "máquinas. No Kubernetes, o estado desejado é declarado (quantas réplicas, qual "
    "imagem, quais limites de recurso) e o <i>control plane</i> trabalha continuamente "
    "para reconciliar o estado real com o declarado. Os objetos centrais são o <b>Pod</b> "
    "(menor unidade implantável), o <b>Deployment</b> (gerencia réplicas e atualizações "
    "controladas), o <b>Service</b> (descoberta e balanceamento interno) e os <b>ConfigMaps/"
    "Secrets</b> (configuração e credenciais desacopladas da imagem). Probes de "
    "<i>liveness</i> e <i>readiness</i> permitem ao cluster reiniciar processos travados e "
    "rotear tráfego apenas para instâncias prontas."))

story.append(P("3.2 CI/CD em ambientes distribuídos", "h2"))
story.append(P(
    "<b>Integração Contínua (CI)</b> é a prática de integrar e validar mudanças com "
    "frequência: a cada commit, o pipeline executa lint, testes automatizados e a "
    "construção das imagens, oferecendo feedback rápido. <b>Entrega/Implantação Contínua "
    "(CD)</b> automatiza a publicação dos artefatos versionados em um registry e seu "
    "deploy nos ambientes, com <i>gates</i> de qualidade e segurança entre as etapas. "
    "Em sistemas distribuídos isso é vital: com muitos serviços evoluindo em paralelo, "
    "só a automação garante que cada um seja testado, escaneado e versionado de forma "
    "consistente. Credenciais sensíveis nunca ficam no código — são injetadas como "
    "<i>secrets</i> do pipeline. Estratégias de release (rolling, blue-green, canary) "
    "reduzem o risco de cada implantação."))

story.append(P("3.3 Observabilidade: métricas, logs e traces", "h2"))
story.append(P(
    "Observabilidade é a capacidade de inferir o estado interno de um sistema a partir de "
    "seus sinais externos — essencial quando uma única requisição atravessa vários "
    "serviços. Apoia-se em três pilares:"))
story.append(bullets([
    "<b>Métricas</b> — séries temporais numéricas e agregáveis (latência, throughput, "
    "taxa de erro, uso de CPU). Respondem &ldquo;o que&rdquo; está acontecendo e alimentam alertas e "
    "autoescala. Padrão de mercado: Prometheus.",
    "<b>Logs</b> — registros discretos de eventos. Tratados como streams estruturados "
    "(JSON) e centralizados, ajudam a entender &ldquo;por que&rdquo; algo ocorreu.",
    "<b>Traces (rastreamento distribuído)</b> — seguem uma requisição ponta a ponta, "
    "correlacionando os serviços por um <i>trace_id</i> propagado. Revelam &ldquo;onde&rdquo; está o "
    "gargalo ou a falha. Padrão aberto: OpenTelemetry, com backends como Jaeger/Tempo.",
]))

# 4 caso concreto
story.append(P("4. Caso concreto de referência: Online Boutique (Google)", "h1"))
story.append(P(
    "Como referência pública e madura, adotamos o <b>Online Boutique</b> "
    "(GoogleCloudPlatform/microservices-demo), aplicação de e-commerce cloud-native "
    "mantida pelo Google. Ela é composta por cerca de uma dezena de microsserviços "
    "escritos em múltiplas linguagens, que se comunicam predominantemente via gRPC e roda "
    "em qualquer cluster Kubernetes — de um minikube local ao GKE gerenciado. O projeto "
    "demonstra na prática os mesmos padrões exigidos por este desafio: orquestração no "
    "Kubernetes, separação por serviço, observabilidade (tracing e métricas), service mesh "
    "(Istio) e deploy declarativo. Ele valida as escolhas da nossa proposta e serve de "
    "espelho arquitetural para a &ldquo;Pedidos Veloz&rdquo;, que adota uma versão enxuta e didática "
    "dos mesmos princípios (HTTP/REST no lugar de gRPC, quatro serviços de domínio em vez "
    "de uma dezena), suficiente para o MVP de quatro semanas."))

# 5 justificativas
story.append(P("5. Justificativa das principais decisões arquiteturais", "h1"))
story.append(bullets([
    "<b>Microsserviços por domínio</b> (Gateway, Pedidos, Pagamentos, Estoque): isolam "
    "falhas e permitem escalar só o que sofre pico — o serviço de Pedidos, no caminho "
    "crítico da campanha promocional.",
    "<b>Docker Compose no local, Kubernetes em produção</b>: paridade dev/prod (12-Factor) "
    "com baixo custo de entrada e resiliência onde importa.",
    "<b>Imagens multi-stage e usuário não-root</b>: imagens enxutas, superfície de ataque "
    "reduzida e versionamento por SHA/semver.",
    "<b>CI/CD com testes e scan de vulnerabilidades</b>: cada mudança é validada antes de "
    "ir a produção, reduzindo o risco de deploy.",
    "<b>Mensageria para o evento &ldquo;PedidoCriado&rdquo;</b>: desacopla efeitos colaterais "
    "(notificações, antifraude) do fluxo síncrono, melhorando resiliência e tempo de "
    "resposta.",
    "<b>Observabilidade desde o MVP</b>: métricas, logs estruturados e tracing aumentam a "
    "rastreabilidade de falhas entre serviços, a maior dor relatada.",
]))

# refs
story.append(P("Referências (fontes primárias)", "h1"))
story.append(P(
    "Kubernetes — Documentation (Pods, Deployments, Services, ConfigMaps/Secrets, HPA, "
    "Pod Security). Docker — Documentation (Dockerfile, multi-stage, Compose). "
    "The Twelve-Factor App (12factor.net). HashiCorp Terraform — Documentation. "
    "GitHub Actions — Documentation. OpenTelemetry e Istio — Documentation. "
    "GoogleCloudPlatform/microservices-demo (Online Boutique), GitHub.&ldquo;, &rdquo;meta"))


def build():
    doc = BaseDocTemplate(
        r"c:\Users\bruno\Desktop\pedidos-veloz\docs\Relatorio_Teorico.pdf",
        pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.6 * cm, bottomMargin=1.8 * cm,
        title="Relatório Técnico - Parte Teórica - Pedidos Veloz")
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    doc.build(story)
    print("Relatorio_Teorico.pdf gerado")


if __name__ == "__main__":
    build()