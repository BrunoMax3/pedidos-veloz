# Versionamento de providers (boa prática: travar versões).
terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  # Em produção, use backend remoto com lock de state (evita corrupção).
  # backend "gcs" {
  #   bucket = "pedidos-veloz-tfstate"
  #   prefix = "prod"
  # }
}
