# =============================================================================
# VARIABLES.TF - Variables principales Fode-DevOps Infrastructure
# =============================================================================

variable "project_name" {
  description = "Nom du projet"
  type        = string
  default     = "fode-devops"
}

variable "environment" {
  description = "Environnement de déploiement"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "L'environnement doit être dev, staging ou prod."
  }
}

variable "aws_region" {
  description = "Région AWS"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block pour le VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "instance_type" {
  description = "Type d'instance EC2"
  type        = string
  default     = "t2.micro"

  validation {
    condition     = contains(["t2.micro", "t2.small", "t3.micro", "t3.small"], var.instance_type)
    error_message = "Le type d'instance doit être compatible avec le Free Tier."
  }
}