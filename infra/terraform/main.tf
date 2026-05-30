# ESQUELETO de IaC para o cluster Kubernetes gerenciado (exemplo GKE).
# Objetivo: tornar a infraestrutura reproduzível e versionada.
# Justificativa no relatório prático (seção IaC).

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cluster Kubernetes gerenciado
resource "google_container_cluster" "primary" {
  name     = "pedidos-veloz-${var.environment}"
  location = var.region

  # Remove o node pool default para gerenciar um próprio (boa prática)
  remove_default_node_pool = true
  initial_node_count       = 1

  # Workload Identity para acesso seguro a serviços da cloud (sem chaves)
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}

# Node pool gerenciado, com autoscaling alinhado ao HPA da aplicação
resource "google_container_node_pool" "primary_nodes" {
  name     = "pool-${var.environment}"
  location = var.region
  cluster  = google_container_cluster.primary.name

  initial_node_count = var.node_count

  autoscaling {
    min_node_count = var.node_count
    max_node_count = 10
  }

  node_config {
    machine_type = "e2-standard-2"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    # Hardening básico do nó
    shielded_instance_config {
      enable_secure_boot = true
    }
  }
}
