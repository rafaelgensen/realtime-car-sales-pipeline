variable "project_id" {
  type        = string
  description = "ID do projeto GCP"
}

variable "env" {
  type        = string
  description = "Ambiente (dev, prod, etc.)"
}

variable "region" {
  type        = string
  description = "Região do GCP"
}