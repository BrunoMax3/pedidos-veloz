variable "project_id" {
  description = "ID do projeto na cloud"
  type        = string
}

variable "region" {
  description = "Região do cluster"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Ambiente (dev/staging/prod) - permite reuso do módulo"
  type        = string
  default     = "prod"
}

variable "node_count" {
  description = "Número inicial de nós do cluster"
  type        = number
  default     = 3
}
