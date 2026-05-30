# IaC — Terraform (esqueleto)

Estrutura mínima para provisionar o cluster de forma **reproduzível e versionada**.

```bash
terraform init
terraform plan  -var="project_id=SEU_PROJETO"
terraform apply -var="project_id=SEU_PROJETO"
```

> Esqueleto intencional: o foco do desafio é demonstrar a abordagem de IaC
> (providers travados, variáveis por ambiente, state remoto com lock, node pool
> com autoscaling). Em produção, evoluir para **módulos reutilizáveis**
> (network, cluster, node_pool) e separar workspaces por ambiente.
